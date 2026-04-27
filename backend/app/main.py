from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

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

    cors_origins = [
        "http://localhost",
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

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
