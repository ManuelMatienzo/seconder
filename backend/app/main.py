from fastapi import FastAPI

from app.core.config import settings
from app.modules.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="Backend para plataforma inteligente de atencion de emergencias vehiculares.",
    )

    app.include_router(api_router)

    return app


app = create_app()
