"""Data manager main app file."""

import uvicorn as uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas.jwt import Settings
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from routers import messages, products, user

app = FastAPI()
app.include_router(messages.router, prefix="/manage")
app.include_router(products.router, prefix="/manage")
app.include_router(user.router, prefix="/manage")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/")
def read_root():
    return {"Data Management": "Start Page"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=7000, reload=True)
