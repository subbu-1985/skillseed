import uuid, os, aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.user import Mentor, MentorApplication, Student, User, UserProfile
from app.models.skill import Skill
from app.core.security import get_current_user, require_admin, require_mentor
from app.core.config import settings

router = APIRouter(prefix="/mentor", tags=["Mentor"])

@router.post("/apply", status_code=201)
async def apply_as_mentor(
    expertise: str = Form(...),
    resume: UploadFile = File(None),
    intro_video: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    resume_url = None
    video_url = None

    if resume:
        ext = os.path.splitext(resume.filename)[1].lower()
        if ext not in (".pdf", ".doc", ".docx"):
            raise HTTPException(status_code=400, detail="Resume must be PDF or Word document")
        fname = f"{uuid.uuid4()}{ext}"
        path = os.path.join(settings.UPLOAD_DIR, "resumes", fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        async with aiofiles.open(path, "wb") as f:
            await f.write(await resume.read())
        resume_url = f"/static/resumes/{fname}"

    if intro_video:
        ext = os.path.splitext(intro_video.filename)[1].lower()
        if ext not in (".mp4", ".webm", ".mov"):
            raise HTTPException(status_code=400, detail="Video must be mp4/webm/mov")
        content = await intro_video.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > 100:
            raise HTTPException(status_code=413, detail="Intro video too large (max 100MB)")
        fname = f"{uuid.uuid4()}{ext}"
        path = os.path.join(settings.UPLOAD_DIR, "videos", fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
        video_url = f"/static/videos/{fname}"

    app = MentorApplication(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        resume_url=resume_url,
        intro_video_url=video_url,
        expertise=expertise,
        status="pending",
    )
    db.add(app)
    await db.commit()
    return {"message": "Application submitted", "application_id": app.id}

@router.get("/applications")
async def list_applications(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(MentorApplication).order_by(MentorApplication.submitted_at.desc()))
    apps = result.scalars().all()
    return [
        {"id": a.id, "user_id": a.user_id, "status": a.status,
         "expertise": a.expertise, "resume_url": a.resume_url,
         "intro_video_url": a.intro_video_url, "submitted_at": a.submitted_at}
        for a in apps
    ]

class ReviewDecision(BaseModel):
    decision: str  # approved | rejected
    comment: Optional[str] = None

@router.post("/applications/{app_id}/review")
async def review_application(
    app_id: str,
    body: ReviewDecision,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from datetime import datetime
    result = await db.execute(select(MentorApplication).where(MentorApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = body.decision
    app.admin_comment = body.comment
    app.reviewed_at = datetime.utcnow()

    if body.decision == "approved":
        # Create or activate mentor record
        res = await db.execute(select(Mentor).where(Mentor.user_id == app.user_id))
        mentor = res.scalar_one_or_none()
        if mentor:
            mentor.approved = True
        else:
            db.add(Mentor(id=str(uuid.uuid4()), user_id=app.user_id, approved=True))
        # Update user role
        res2 = await db.execute(select(User).where(User.id == app.user_id))
        user = res2.scalar_one_or_none()
        if user:
            user.role = "mentor"

    await db.commit()
    return {"message": f"Application {body.decision}"}

@router.get("/students")
async def my_students(db: AsyncSession = Depends(get_db), current_user=Depends(require_mentor)):
    res = await db.execute(select(Mentor).where(Mentor.user_id == current_user.id))
    mentor = res.scalar_one_or_none()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor record not found")

    res2 = await db.execute(
        select(Student).options(selectinload(Student.skill_progress))
    )
    students = res2.scalars().all()
    out = []
    for s in students:
        res3 = await db.execute(select(UserProfile).where(UserProfile.user_id == s.user_id))
        profile = res3.scalar_one_or_none()
        out.append({
            "id": s.id, "user_id": s.user_id,
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "grade": s.grade, "school_name": s.school_name,
        })
    return out
