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

# Simple in-memory cache for admin summary to avoid repeated slow calls in rapid succession.
# TTL is short to keep data fresh while improving responsiveness for the UI during rapid reloads.
_ADMIN_SUMMARY_CACHE = {
    "ts": None,
    "data": None,
}
_ADMIN_SUMMARY_TTL_SECONDS = float(os.getenv("ADMIN_SUMMARY_TTL", "3"))


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


@app.api_route("/api/catalogo/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catalogo_gateway(path: str, request: Request):
    """Ruta requests a Catálogo Service"""
    return await proxy_request(SERVICES["catalogo"], f"/catalogo/{path}", request)


@app.api_route("/api/proveedores/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proveedores_gateway(path: str, request: Request):
    """Ruta requests a Proveedores Service"""
    return await proxy_request(SERVICES["proveedores"], f"/proveedores/{path}", request)


@app.api_route("/api/contratacion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def contratacion_gateway(path: str, request: Request):
    """Ruta requests a Contratación Service"""
    # Contratacion service router defines its own paths (e.g. '/health', '/pedidos').
    # Forward the incoming subpath directly so the service receives the expected route.
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

        proveedores_candidates = [
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores/metrics",
            f"{SERVICES['proveedores']}/proveedores/admin/metrics",
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores",
            f"{SERVICES['proveedores']}/proveedores/v1/admin/proveedores",
        ]

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
        """Try multiple common shapes to extract a numeric count from a service response."""
        if data is None:
            return None
        # If it's already a number
        if isinstance(data, int):
            return data
        # If dict try common keys
        if isinstance(data, dict):
            # New: some services return {'orders': N} or {'orders_by_status': {...}}
            if 'orders' in data:
                v = data['orders']
                if isinstance(v, int):
                    return v
                if isinstance(v, dict):
                    # sum counts by status
                    try:
                        return sum(int(x) for x in v.values())
                    except Exception:
                        pass
            if 'orders_by_status' in data and isinstance(data['orders_by_status'], dict):
                try:
                    return sum(int(x) for x in data['orders_by_status'].values())
                except Exception:
                    pass
            for k in ('total', 'count', 'results', 'size'):
                if k in data and isinstance(data[k], int):
                    return data[k]
            # items / data / results might be arrays
            for arr_key in ('items', 'data', 'results'):
                if arr_key in data and isinstance(data[arr_key], list):
                    return len(data[arr_key])
        # If a list, return length
        if isinstance(data, list):
            return len(data)
        return None

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
