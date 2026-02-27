from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

app = FastAPI()

# ----- BASIC AUTH SETUP -----
security = HTTPBasic()

VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"

# ----- API KEY SETUP -----
VALID_API_KEY = "my-secret-api-key"

# Toggle which auth to use
AUTH_MODE = "apikey"  # change to "apikey" when needed


@app.middleware("http")
async def auth_middleware(request: Request, call_next):

    # Allow health endpoint without auth
    if request.url.path == "/":
        return await call_next(request)

    try:
        if AUTH_MODE == "basic":
            auth = request.headers.get("Authorization")
            if not auth:
                return JSONResponse(status_code=401, content={"detail": "Missing credentials"})

            credentials: HTTPBasicCredentials = await security(request)
            correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
            correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)

            if not (correct_username and correct_password):
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        elif AUTH_MODE == "apikey":
            api_key = request.headers.get("x-api-key")
            if api_key != VALID_API_KEY:
                return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

        response = await call_next(request)
        return response

    except Exception:
        return JSONResponse(status_code=401, content={"detail": "Authentication failed"})


@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()

    method = body.get("method")
    request_id = body.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "railway-mcp-test",
                    "version": "1.0.0"
                }
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "Test MCP tool"
                    }
                ]
            }
        }

    return JSONResponse(
        status_code=400,
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }
    )
