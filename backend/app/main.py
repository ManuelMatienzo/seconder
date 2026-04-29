from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
import os

load_dotenv()

from app.core.config import settings
from app.core.database import engine
from app.models import Notification
from app.modules.router import api_router


def create_app() -> FastAPI:
    try:
        Notification.__table__.create(bind=engine, checkfirst=True)
    except SQLAlchemyError:
        pass

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="Backend para plataforma inteligente de atencion de emergencias vehiculares.",
    )

    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()
