import os, uuid, aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.content import Video, VideoProgress, Activity, ActivityCompletion
from app.models.user import Student
from app.core.security import get_current_user, require_admin, require_mentor
from app.core.config import settings

router = APIRouter(tags=["Content"])

# ─── Videos ──────────────────────────────────────────────────────────────────

@router.get("/modules/{module_id}/videos")
async def list_videos(module_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Video).where(Video.module_id == module_id).order_by(Video.order_index)
    )
    videos = result.scalars().all()
    return [
        {
            "id": v.id, "title": v.title, "description": v.description,
            "video_url": v.video_url, "thumbnail_url": v.thumbnail_url,
            "duration_seconds": v.duration_seconds, "order_index": v.order_index,
            "file_size_mb": v.file_size_mb, "created_at": v.created_at,
        }
        for v in videos
    ]

@router.post("/modules/{module_id}/videos", status_code=201)
async def upload_video(
    module_id: str,
    title: str = Form(...),
    description: str = Form(""),
    order_index: int = Form(0),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_mentor),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".mp4", ".webm", ".mkv", ".mov", ".avi"):
        raise HTTPException(status_code=400, detail="Unsupported video format")

    # Read and check size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"Video exceeds {settings.MAX_VIDEO_SIZE_MB}MB limit")

    filename = f"{uuid.uuid4()}{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "videos")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    video = Video(
        id=str(uuid.uuid4()),
        module_id=module_id,
        title=title,
        description=description,
        video_url=f"/static/videos/{filename}",
        order_index=order_index,
        uploaded_by=current_user.id,
        file_size_mb=round(size_mb, 2),
        original_filename=file.filename,
    )
    db.add(video)
    await db.commit()
    return {"id": video.id, "title": video.title, "video_url": video.video_url, "file_size_mb": video.file_size_mb}

@router.delete("/videos/{video_id}")
async def delete_video(video_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_mentor)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Remove file from disk
    if video.video_url:
        local_path = os.path.join(settings.UPLOAD_DIR, "videos", os.path.basename(video.video_url))
        if os.path.exists(local_path):
            os.remove(local_path)

    await db.delete(video)
    await db.commit()
    return {"message": "Video deleted"}

@router.post("/videos/{video_id}/progress")
async def update_video_progress(
    video_id: str,
    watched_percentage: float,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Get student
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=403, detail="Student only")

    result = await db.execute(
        select(VideoProgress).where(VideoProgress.student_id == student.id, VideoProgress.video_id == video_id)
    )
    vp = result.scalar_one_or_none()
    if vp:
        vp.watched_percentage = min(watched_percentage, 100.0)
        vp.completed = vp.watched_percentage >= 90.0
    else:
        from datetime import datetime
        vp = VideoProgress(
            id=str(uuid.uuid4()),
            student_id=student.id,
            video_id=video_id,
            watched_percentage=min(watched_percentage, 100.0),
            completed=watched_percentage >= 90.0,
        )
        db.add(vp)
    await db.commit()
    return {"watched_percentage": vp.watched_percentage, "completed": vp.completed}

# ─── Activities ───────────────────────────────────────────────────────────────

@router.get("/modules/{module_id}/activities")
async def list_activities(module_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Activity).where(Activity.module_id == module_id).order_by(Activity.order_index)
    )
    acts = result.scalars().all()
    return [
        {"id": a.id, "title": a.title, "description": a.description,
         "activity_type": a.activity_type, "order_index": a.order_index}
        for a in acts
    ]

class ActivityCreate(BaseModel):
    module_id: str
    title: str
    description: Optional[str] = None
    activity_type: str = "task"
    content_data: Optional[str] = None
    order_index: int = 0

@router.post("/activities", status_code=201)
async def create_activity(body: ActivityCreate, db: AsyncSession = Depends(get_db), _=Depends(require_mentor)):
    act = Activity(id=str(uuid.uuid4()), **body.dict())
    db.add(act)
    await db.commit()
    return {"id": act.id, "title": act.title}

@router.post("/activities/{activity_id}/complete")
async def complete_activity(
    activity_id: str,
    score: float = 0.0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=403, detail="Student only")

    completion = ActivityCompletion(
        id=str(uuid.uuid4()), student_id=student.id,
        activity_id=activity_id, score=score
    )
    db.add(completion)
    await db.commit()
    return {"message": "Activity completed", "score": score}
