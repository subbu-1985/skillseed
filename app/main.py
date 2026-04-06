import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.core.config import settings

# Ensure upload directories exist
for subdir in ("videos", "resumes", "avatars"):
    os.makedirs(os.path.join(settings.UPLOAD_DIR, subdir), exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="SkillSeed API",
    description="Soft Skills Learning Platform for Students (Grades 6–12)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Import and include routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.skills import router as skills_router
from app.routers.content import router as content_router
from app.routers.quiz import router as quiz_router
from app.routers.mentor import router as mentor_router
from app.routers.misc import (
    sessions_router, notif_router, progress_router,
    sub_router, admin_router, msg_router
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(skills_router)
app.include_router(content_router)
app.include_router(quiz_router)
app.include_router(mentor_router)
app.include_router(sessions_router)
app.include_router(notif_router)
app.include_router(progress_router)
app.include_router(sub_router)
app.include_router(admin_router)
app.include_router(msg_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "SkillSeed API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "default_admin": "admin@skillseed.com",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
