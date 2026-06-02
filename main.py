from app.api.v1.endpoints import users
from app.lifespan import lifespan

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
import uvicorn
import os

# Define the API version prefix
API_PREFIX = "/api/v1"

PORT = settings.PORT     

# FastAPI Instance with Lifespan, root path, and docs url
app = FastAPI(
    title="Backend Service",
    description="API for managing Users Operations",
    version="1.0.0",
    lifespan=lifespan,
    root_path='/backend',
    docs_url="/management/swagger-ui",
    openapi_url="/management/openapi.json",
)

# Add CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "null"
    ],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route for user management operations
app.include_router(users.router, prefix=f"{API_PREFIX}", tags=["Users Operations"])

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract and customize the validation errors
    errors = exc.errors()
    custom_errors = []
    for error in errors:
        loc = error.get("loc", [])
        msg = error.get("msg", "")

        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]  # Strip the "Value error," prefix

        custom_errors.append({
            "field": loc[-1] if loc else "unknown",
            "message": msg
        })

    return JSONResponse(
        status_code=422,
        content={
            "status_code": 422,
            "message": "Los datos proporcionados no son válidos.",
            "errors": custom_errors
        }
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    error_detail = (
        exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    )
    api_version = error_detail.get("version", "0.0.0")
    error_message = error_detail.get("message", "An error occurred")
    error_list = error_detail.get("errors", [])

    if not isinstance(error_list, list):
        error_list = [{"message": str(error_list)}]

    formatted_errors = [
        {
            key: value if isinstance(value, str) else str(value)
            for key, value in error.items()
        }
        for error in error_list
    ]

    if api_version == "0.0.0":
        response_content = {
            "status_code": exc.status_code,
            "message": error_message,
            "errors": formatted_errors,
            "version": api_version,
        }
    else:
        response_content = {
            "message": error_message,
            "version": api_version,
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), access_log=False)
