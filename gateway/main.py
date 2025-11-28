"""
API Gateway - Punto de entrada único para todos los microservicios
Enruta requests a los servicios correspondientes
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional

app = FastAPI(
    title="Eventos Peru - API Gateway",
    description="Gateway que enruta peticiones a los microservicios",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios
SERVICES = {
    "iam": "http://127.0.0.1:8010",
    "catalogo": "http://127.0.0.1:8020",
    "proveedores": "http://127.0.0.1:8030",
    "contratacion": "http://127.0.0.1:8040",
}


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
    if request.method in ["POST", "PUT", "PATCH"]:
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
    return await proxy_request(SERVICES["contratacion"], f"/contratacion/{path}", request)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
