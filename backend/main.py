from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import get_settings
from app.db.database import connect_mongo, disconnect_mongo, connect_redis, disconnect_redis
from app.api.v1.routes import resume_routes, github_routes, job_routes, report_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Recruiter Intelligence Platform v2")
    await connect_mongo()
    await connect_redis()
    yield
    await disconnect_mongo()
    await disconnect_redis()
    logger.info("Shutdown complete")
    

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered recruiter platform: resume -> Github -> compatibility -> PDF report",
        lifespan=lifespan,
    )   
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = "/api/v1"
    app.include_router(resume_routes.router, prefix=prefix)
    app.include_router(github_routes.router, prefix=prefix)
    app.include_router(job_routes.router, prefix=prefix)
    app.include_router(report_routes.router, prefix=prefix)

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
