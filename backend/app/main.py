from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers.api import router
from app.config import settings

app = FastAPI(
    title="15 Night Backend API",
    version="1.0.0",
    # docs_url="/docs",
    # openapi_url="/docs/openapi.json",
    docs_url=None,
    redoc_url=None
)

origins = [
    "http://localhost:3000",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://15night.nctucsunion.me",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,
    session_cookie="session"
)

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router, prefix="/api", tags=["API"])

@app.get("/")
def read_root():
    return {"message": "15 Night Backend API"}
