"""
API Gateway - Punto de entrada único para todos los microservicios
Enruta requests a los servicios correspondientes
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional
import asyncio
import json
import os
import logging
import time
import socket

app = FastAPI(
    title="Eventos Peru - API Gateway",
    description="Gateway que enruta peticiones a los microservicios",
    version="1.0.0"
)

# Configure basic logging for timing/debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios. Leer desde variables de entorno para despliegues en k8s/ArgoCD.
SERVICES = {
    "iam": os.getenv("IAM_SERVICE_URL", "http://127.0.0.1:8010"),
    "catalogo": os.getenv("CATALOGO_SERVICE_URL", "http://127.0.0.1:8020"),
    "proveedores": os.getenv("PROVEEDORES_SERVICE_URL", "http://127.0.0.1:8030"),
    "contratacion": os.getenv("CONTRATACION_SERVICE_URL", "http://127.0.0.1:8040"),
}

# Optional service token to call internal admin endpoints that require auth.
# Set ADMIN_SERVICE_TOKEN as an environment variable (a JWT or service token) in the deployment.
ADMIN_SERVICE_TOKEN = os.getenv("ADMIN_SERVICE_TOKEN")
# If an admin service token is provided at runtime, attempt a sanity check
#: if JWT_SECRET is available in the environment, verify the token signature
# so deployments with a mismatched admin token fail-fast and log useful info.
try:
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALG = os.getenv("JWT_ALG", os.getenv("JWT_ALGORITHM", "HS256"))
    if ADMIN_SERVICE_TOKEN and JWT_SECRET:
        from jose import jwt as _j, JWTError as _JWTError
        try:
            _j.decode(ADMIN_SERVICE_TOKEN, JWT_SECRET, algorithms=[JWT_ALG])
            logger.info("ADMIN_SERVICE_TOKEN signature validated with JWT_SECRET")
        except Exception:
            logger.warning("ADMIN_SERVICE_TOKEN present but failed signature validation with JWT_SECRET.\n" \
                           "If you intend to use ADMIN_SERVICE_TOKEN it must be a JWT signed with the cluster JWT_SECRET (HS256).\n" \
                           "Consider removing the secret so the Gateway forwards the incoming Authorization header instead.")
except Exception:
    # never crash the gateway startup because of the check
    logger.exception("Error while validating ADMIN_SERVICE_TOKEN (non-fatal)")

# Simple in-memory cache for admin summary to avoid repeated slow calls in rapid succession.
# TTL is short to keep data fresh while improving responsiveness for the UI during rapid reloads.
_ADMIN_SUMMARY_CACHE = {
    "ts": None,
    "data": None,
}
_ADMIN_SUMMARY_TTL_SECONDS = float(os.getenv("ADMIN_SUMMARY_TTL", "3"))

# Per-service winner cache to avoid repeatedly probing many candidate paths
_SERVICE_WINNER_CACHE = {}
# seconds to remember a working candidate URL for a service
_SERVICE_WINNER_TTL = float(os.getenv("SERVICE_WINNER_TTL", "60"))


async def proxy_request(
    service_url: str,
    path: str,
    request: Request,
) -> Response:
    """
    Proxy request to the target service
    """
    # Construir URL completa
    url = f"{service_url}{path}"
    
    # Obtener headers (excepto host)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Obtener body si existe
    body = None
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        body = await request.body()
    
    # Hacer request al servicio
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
        )
    
    # Retornar response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type"),
    )


async def _race_first_success(client: httpx.AsyncClient, urls, params=None, headers=None, per_request_timeout: float = 4.0):
    """Send requests to multiple candidate URLs in parallel and return the first response with status < 400.
    This version records per-URL timings and logs which URL finished and its duration.
    """
    async def _timed_get(u):
        t0 = time.time()
        try:
            r = await client.get(u, params=params, headers=headers, timeout=per_request_timeout)
            elapsed = (time.time() - t0) * 1000.0
            logger.info(f"race result: url={u} status={r.status_code} elapsed_ms={elapsed:.1f}")
            return (u, r, elapsed, None)
        except Exception as e:
            elapsed = (time.time() - t0) * 1000.0
            logger.info(f"race error: url={u} error={e} elapsed_ms={elapsed:.1f}")
            return (u, None, elapsed, e)

    tasks = [asyncio.create_task(_timed_get(u)) for u in urls]

    last_exc = None
    last_resp = None
    try:
        for fut in asyncio.as_completed(tasks, timeout=per_request_timeout + 0.5):
            try:
                u, r, elapsed, exc = await fut
            except Exception as e:
                last_exc = e
                continue
            if exc:
                last_exc = exc
                continue
            last_resp = (u, r, elapsed)
            if r.status_code < 400:
                # cancel remaining
                for t in tasks:
                    if not t.done():
                        t.cancel()
                logger.info(f"race winner: {u} elapsed_ms={elapsed:.1f} status={r.status_code}")
                # attach the winning url to the response object for callers
                try:
                    setattr(r, '_winner_url', u)
                except Exception:
                    pass
                return r
    except asyncio.TimeoutError:
        logger.info("race timeout waiting for candidates")
        pass

    # no successful response found
    if last_resp is not None:
        u, r, elapsed = last_resp
        logger.info(f"race none successful, returning last response from {u} status={r.status_code} elapsed_ms={elapsed:.1f}")
        return r
    if last_exc is not None:
        raise last_exc
    return None


@app.api_route("/api/iam/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def iam_gateway(path: str, request: Request):
    """Ruta requests a IAM Service"""
    return await proxy_request(SERVICES["iam"], f"/iam/{path}", request)


@app.api_route("/iam/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def iam_root_gateway(path: str, request: Request):
    """Proxy para soportar requests que llegan a /iam/* (útil para Swagger desde browser)."""
    return await proxy_request(SERVICES["iam"], f"/iam/{path}", request)


@app.api_route("/api/catalogo/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catalogo_gateway(path: str, request: Request):
    """Ruta requests a Catálogo Service"""
    return await proxy_request(SERVICES["catalogo"], f"/catalogo/{path}", request)


@app.api_route("/catalogo/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catalogo_root_gateway(path: str, request: Request):
    """Proxy para soportar requests que llegan a /catalogo/* (útil para Swagger desde browser)."""
    return await proxy_request(SERVICES["catalogo"], f"/catalogo/{path}", request)


@app.api_route("/api/proveedores/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proveedores_gateway(path: str, request: Request):
    """Ruta requests a Proveedores Service"""
    return await proxy_request(SERVICES["proveedores"], f"/proveedores/{path}", request)


@app.api_route("/proveedores/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proveedores_root_gateway(path: str, request: Request):
    """Proxy para soportar requests que llegan a /proveedores/* (útil para Swagger desde browser)."""
    return await proxy_request(SERVICES["proveedores"], f"/proveedores/{path}", request)


@app.api_route("/api/contratacion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def contratacion_gateway(path: str, request: Request):
    """Ruta requests a Contratación Service"""
    # Contratacion service router defines its own paths (e.g. '/health', '/pedidos').
    # Forward the incoming subpath directly so the service receives the expected route.
    return await proxy_request(SERVICES["contratacion"], f"/{path}", request)


@app.api_route("/contratacion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def contratacion_root_gateway(path: str, request: Request):
    """Proxy para soportar requests que llegan a /contratacion/* (útil para Swagger desde browser).

    Note: Contratacion service expects paths without the '/contratacion' prefix internally,
    but router defines endpoints with full paths; forward the subpath as-is.
    """
    return await proxy_request(SERVICES["contratacion"], f"/{path}", request)


@app.get("/health")
async def health_check():
    """Health check del gateway"""
    return {
        "status": "healthy",
        "services": SERVICES
    }


@app.get("/")
async def root():
    """Información del gateway"""
    return {
        "service": "Eventos Peru API Gateway",
        "version": "1.0.0",
        "services": {
            "iam": f"{SERVICES['iam']} (puerto 8010)",
            "catalogo": f"{SERVICES['catalogo']} (puerto 8020)",
            "proveedores": f"{SERVICES['proveedores']} (puerto 8030)",
            "contratacion": f"{SERVICES['contratacion']} (puerto 8040)",
        },
        "endpoints": {
            "iam": "/api/iam/*",
            "catalogo": "/api/catalogo/*",
            "proveedores": "/api/proveedores/*",
            "contratacion": "/api/contratacion/*",
        }
    }


@app.get("/api/admin/summary")
async def admin_summary(request: Request, from_date: Optional[str] = None, to_date: Optional[str] = None):
    """Aggregate simple admin metrics from microservices.

    This endpoint queries the main services for admin endpoints and
    returns a compact summary used by the dashboard. It is deliberatey
    conservative: it forwards small requests to each service and tries
    to extract common fields (like 'total'). If a service does not
    expose detailed metrics, the field may be null.
    """
    # Prepare optional headers for admin internal calls (service-to-service token)
    # If ADMIN_SERVICE_TOKEN is set, use it. Otherwise, try to reuse the incoming
    # `Authorization` header from the request (so the gateway can call admin endpoints
    # using the user's token when applicable).
    admin_headers = {}
    if ADMIN_SERVICE_TOKEN:
        admin_headers['Authorization'] = f"Bearer {ADMIN_SERVICE_TOKEN}"
    else:
        incoming_auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if incoming_auth:
            admin_headers['Authorization'] = incoming_auth

    # Return cached summary if recent
    import time
    now = time.time()
    cached_ts = _ADMIN_SUMMARY_CACHE.get("ts")
    if cached_ts and (now - cached_ts) < _ADMIN_SUMMARY_TTL_SECONDS:
        return _ADMIN_SUMMARY_CACHE.get("data")

    # Use a shorter client timeout for quicker failures; per-request timeouts applied below.
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Prepare params for contratacion
        params_cont = {}
        if from_date:
            params_cont['from'] = from_date
        if to_date:
            params_cont['to'] = to_date

        # If we have a cached winner for contratacion, prefer it to avoid probing many legacy paths
        cached = _SERVICE_WINNER_CACHE.get('contratacion')
        contratacion_candidates = []
        if cached and (time.time() - cached.get('ts', 0) < _SERVICE_WINNER_TTL):
            contratacion_candidates = [cached['url']]
        else:
            contratacion_candidates = [
            f"{SERVICES['contratacion']}/admin/metrics",
            f"{SERVICES['contratacion']}/metrics",
            f"{SERVICES['contratacion']}/v1/contratacion/admin/metrics",
            f"{SERVICES['contratacion']}/contratacion/admin/metrics",
            f"{SERVICES['contratacion']}/v1/contratacion/admin/counts",
            f"{SERVICES['contratacion']}/contratacion/admin/counts",
            f"{SERVICES['contratacion']}/contratacion/admin/pedidos",
            f"{SERVICES['contratacion']}/v1/contratacion/admin/pedidos",
            f"{SERVICES['contratacion']}/admin/pedidos",
            ]

        cached = _SERVICE_WINNER_CACHE.get('proveedores')
        if cached and (time.time() - cached.get('ts', 0) < _SERVICE_WINNER_TTL):
            proveedores_candidates = [cached['url']]
        else:
            proveedores_candidates = [
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores/metrics",
            f"{SERVICES['proveedores']}/proveedores/admin/metrics",
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores",
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores",
            ]

        cached = _SERVICE_WINNER_CACHE.get('iam')
        if cached and (time.time() - cached.get('ts', 0) < _SERVICE_WINNER_TTL):
            iam_candidates = [cached['url']]
        else:
            iam_candidates = [
            f"{SERVICES['iam']}/iam/admin/metrics",
            f"{SERVICES['iam']}/admin/metrics",
            f"{SERVICES['iam']}/iam/admin/users",
            f"{SERVICES['iam']}/iam/admin/users",
            ]

        # Fire the three races concurrently
        race_tasks = [
            asyncio.create_task(_race_first_success(client, contratacion_candidates, params=params_cont, headers=admin_headers, per_request_timeout=3.0)),
            asyncio.create_task(_race_first_success(client, proveedores_candidates, params={"limit": 1}, headers=admin_headers, per_request_timeout=3.0)),
            asyncio.create_task(_race_first_success(client, iam_candidates, params={"limit": 1}, headers=admin_headers, per_request_timeout=3.0)),
        ]

        contratacion_future, proveedores_future, iam_future = await asyncio.gather(*race_tasks, return_exceptions=True)

        # If we used a cached candidate and it returned a non-OK response, evict the cache so next call will probe again
        def _maybe_evict_cache(service_key, resp):
            try:
                if resp is None:
                    return
                status = getattr(resp, 'status_code', None)
                winner_url = getattr(resp, '_winner_url', None) or getattr(resp, 'url', None)
                # if status >=400 and we used a cached single candidate, evict
                cached = _SERVICE_WINNER_CACHE.get(service_key)
                if cached and cached.get('url') and status is not None and status >= 400:
                    logger.info(f"evicting cached candidate for {service_key} because status={status}")
                    try:
                        del _SERVICE_WINNER_CACHE[service_key]
                    except KeyError:
                        pass
                # if success, store the winning url in cache
                if status is not None and status < 400 and winner_url:
                    _SERVICE_WINNER_CACHE[service_key] = {'url': str(winner_url), 'ts': time.time()}
            except Exception:
                pass

        # update per-service caches based on responses
        _maybe_evict_cache('contratacion', contratacion_future if not isinstance(contratacion_future, Exception) else None)
        _maybe_evict_cache('proveedores', proveedores_future if not isinstance(proveedores_future, Exception) else None)
        _maybe_evict_cache('iam', iam_future if not isinstance(iam_future, Exception) else None)

        contratacion_resp = contratacion_future if not isinstance(contratacion_future, Exception) else None
        proveedores_resp = proveedores_future if not isinstance(proveedores_future, Exception) else proveedores_future
        iam_resp = iam_future if not isinstance(iam_future, Exception) else iam_future

    # Helper to safely parse JSON bodies
    def safe_json(resp):
        try:
            return resp.json()
        except Exception:
            return None
    def extract_count(data):
        """Robust extractor: search recursively for common count shapes anywhere in the JSON.

        It looks for (in order):
        - an `orders_by_status` dict (sums its values)
        - an `orders` numeric or dict (sums dict values)
        - numeric keys `total`, `count`, `size`
        - arrays under keys `items`, `data`, `results` (returns len)
        - if the entire payload is a list, return its length
        Returns None if nothing found.
        """
        if data is None:
            return None

        # If it's a number
        if isinstance(data, int):
            return data

        # Recursive search for a key matching any of the target names
        def recurse(obj):
            # primitives
            if obj is None:
                return None
            if isinstance(obj, int):
                return obj
            if isinstance(obj, list):
                # If list of items look like orders, return length
                if len(obj) > 0:
                    return len(obj)
                return 0

            if isinstance(obj, dict):
                # 1) orders_by_status
                if 'orders_by_status' in obj and isinstance(obj['orders_by_status'], dict):
                    try:
                        return sum(int(v) for v in obj['orders_by_status'].values())
                    except Exception:
                        pass

                # 2) orders (could be int or dict)
                if 'orders' in obj:
                    v = obj['orders']
                    if isinstance(v, int):
                        return v
                    if isinstance(v, dict):
                        try:
                            return sum(int(x) for x in v.values())
                        except Exception:
                            pass

                # 3) common numeric keys
                for k in ('total', 'count', 'size'):
                    if k in obj and isinstance(obj[k], int):
                        return obj[k]

                # 4) common array keys
                for arr_key in ('items', 'data', 'results'):
                    if arr_key in obj and isinstance(obj[arr_key], list):
                        return len(obj[arr_key])

                # Otherwise recurse into children (depth-first)
                for key, val in obj.items():
                    try:
                        res = recurse(val)
                        if res is not None:
                            return res
                    except Exception:
                        continue

            return None

        return recurse(data)

    summary = {
        "generatedAt": None,
        "orders": None,
        "providers": None,
        "users": None,
        "services": {}
    }

    # Parse contratacion response (we tried candidates sequentially above)
    if isinstance(contratacion_resp, Exception):
        summary['services']['contratacion'] = { 'ok': False, 'error': str(contratacion_resp) }
    elif contratacion_resp is None:
        summary['services']['contratacion'] = { 'ok': False, 'error': 'no-response' }
    else:
        summary['services']['contratacion'] = { 'ok': contratacion_resp.status_code }
        data = safe_json(contratacion_resp)
        # Log the response url and parsed body to help debug missing fields
        try:
            logger.info(f"contratacion response: url={getattr(contratacion_resp, 'url', None)} status={contratacion_resp.status_code} body={data}")
        except Exception:
            logger.info("contratacion response: could not log body")
        summary['orders'] = extract_count(data)
        # If the service returned a breakdown by status, propagate it to the top-level summary
        try:
            if isinstance(data, dict) and 'orders_by_status' in data:
                summary['orders_by_status'] = data.get('orders_by_status')
        except Exception:
            pass

    # Parse proveedores response
    resp = proveedores_resp
    if isinstance(resp, Exception):
        summary['services']['proveedores'] = { 'ok': False, 'error': str(resp) }
    else:
        summary['services']['proveedores'] = { 'ok': resp.status_code }
        data = safe_json(resp)
        summary['providers'] = extract_count(data)

    # Parse iam response
    resp = iam_resp
    if isinstance(resp, Exception):
        summary['services']['iam'] = { 'ok': False, 'error': str(resp) }
    else:
        summary['services']['iam'] = { 'ok': resp.status_code }
        data = safe_json(resp)
        summary['users'] = extract_count(data)

    from datetime import datetime
    summary['generatedAt'] = datetime.utcnow().isoformat() + 'Z'

    # Include the hostname of the gateway process (useful to identify which instance served the request)
    try:
        host_name = os.getenv("GATEWAY_HOSTNAME") or socket.gethostname()
    except Exception:
        host_name = None
    summary['connectedFrom'] = host_name

    # store in-memory cache
    _ADMIN_SUMMARY_CACHE['ts'] = now
    _ADMIN_SUMMARY_CACHE['data'] = summary

    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
