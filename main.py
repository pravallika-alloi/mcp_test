from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.api_key import APIKeyHeader
import secrets
import uvicorn

app = FastAPI()

# ----- BASIC AUTH SETUP -----
security = HTTPBasic()

VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"

# ----- API KEY SETUP -----
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
VALID_API_KEY = "my-secret-api-key"

# Toggle which auth to use
AUTH_MODE = "basic"  # change to "apikey" when needed

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if AUTH_MODE == "basic":
        credentials: HTTPBasicCredentials = await security(request)
        correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
        if not (correct_username and correct_password):
            raise HTTPException(status_code=401, detail="Unauthorized")
    elif AUTH_MODE == "apikey":
        api_key = request.headers.get("x-api-key")
        if api_key != VALID_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    response = await call_next(request)
    return response

@app.get("/mcp")
async def mcp_endpoint():
    return {
        "tools": [
            {
                "name": "test_tool",
                "description": "Test MCP tool"
            }
        ]
    }

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
