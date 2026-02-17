from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db import Base, engine
from .storage.s3 import ensure_bucket
from .routes import health, projects, affirmations, voice, jobs, music, auth, billing, webhooks, privacy, limits, voices, coach
from .startup_migrations import run_lightweight_migrations

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()
    ensure_bucket()

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(affirmations.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(music.router, prefix="/api")
app.include_router(voices.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(privacy.router, prefix="/api")
app.include_router(limits.router, prefix="/api")
app.include_router(coach.router, prefix="/api")
