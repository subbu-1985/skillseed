import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.core.security import get_current_user, require_admin, require_mentor

# ─── Live Sessions ────────────────────────────────────────────────────────────

sessions_router = APIRouter(prefix="/sessions", tags=["Live Sessions"])

class SessionCreate(BaseModel):
    skill_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    session_date: str
    start_time: str
    duration_minutes: int = 60
    meeting_link: Optional[str] = None

@sessions_router.get("")
async def list_sessions(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    from app.models.session import LiveSession
    result = await db.execute(select(LiveSession).where(LiveSession.is_active == True).order_by(LiveSession.session_date))
    sessions = result.scalars().all()
    return [
        {"id": s.id, "title": s.title, "skill_id": s.skill_id, "mentor_id": s.mentor_id,
         "session_date": s.session_date, "start_time": s.start_time,
         "duration_minutes": s.duration_minutes, "meeting_link": s.meeting_link}
        for s in sessions
    ]

@sessions_router.post("", status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_mentor)):
    from app.models.session import LiveSession
    from app.models.user import Mentor
    res = await db.execute(select(Mentor).where(Mentor.user_id == current_user.id))
    mentor = res.scalar_one_or_none()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    session = LiveSession(id=str(uuid.uuid4()), mentor_id=mentor.id, **body.dict())
    db.add(session)
    await db.commit()
    return {"id": session.id, "title": session.title, "meeting_link": session.meeting_link}

@sessions_router.post("/{session_id}/join")
async def join_session(session_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.session import LiveSession, SessionAttendance
    from app.models.user import Student
    res = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    res2 = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = res2.scalar_one_or_none()
    if student:
        attendance = SessionAttendance(
            id=str(uuid.uuid4()), session_id=session_id,
            student_id=student.id, attended=True, joined_at=datetime.utcnow()
        )
        db.add(attendance)
        await db.commit()

    return {"meeting_link": session.meeting_link, "title": session.title}

@sessions_router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_mentor)):
    from app.models.session import LiveSession
    res = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Not found")
    session.is_active = False
    await db.commit()
    return {"message": "Session cancelled"}

# ─── Notifications ────────────────────────────────────────────────────────────

notif_router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotifCreate(BaseModel):
    user_id: str
    title: str
    message: str
    notif_type: str = "general"

@notif_router.get("")
async def get_notifications(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.notification import Notification
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(50)
    )
    notifs = result.scalars().all()
    return [{"id": n.id, "title": n.title, "message": n.message, "notif_type": n.notif_type, "is_read": n.is_read, "created_at": n.created_at} for n in notifs]

@notif_router.post("/{notif_id}/read")
async def mark_read(notif_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.notification import Notification
    result = await db.execute(select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id))
    n = result.scalar_one_or_none()
    if n:
        n.is_read = True
        await db.commit()
    return {"message": "Marked as read"}

@notif_router.post("/broadcast")
async def broadcast(body: NotifCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.notification import Notification
    from app.models.user import User
    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    for u in users:
        db.add(Notification(id=str(uuid.uuid4()), user_id=u.id, title=body.title, message=body.message, notif_type=body.notif_type))
    await db.commit()
    return {"message": f"Broadcasted to {len(users)} users"}

# ─── Progress ─────────────────────────────────────────────────────────────────

progress_router = APIRouter(prefix="/progress", tags=["Progress"])

@progress_router.get("/me")
async def my_progress(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.user import Student, StudentSkillProgress
    from app.models.quiz import QuizAttempt
    from app.models.content import VideoProgress, ActivityCompletion

    res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    res2 = await db.execute(select(StudentSkillProgress).where(StudentSkillProgress.student_id == student.id))
    skill_progress = res2.scalars().all()

    res3 = await db.execute(select(QuizAttempt).where(QuizAttempt.student_id == student.id))
    quiz_attempts = res3.scalars().all()

    res4 = await db.execute(select(VideoProgress).where(VideoProgress.student_id == student.id, VideoProgress.completed == True))
    completed_videos = len(res4.scalars().all())

    return {
        "student_id": student.id,
        "skill_progress": [
            {"skill_id": sp.skill_id, "progress_percentage": sp.progress_percentage, "level": sp.level}
            for sp in skill_progress
        ],
        "quiz_attempts": len(quiz_attempts),
        "quiz_passed": sum(1 for a in quiz_attempts if a.passed),
        "videos_completed": completed_videos,
    }

# ─── Subscriptions ────────────────────────────────────────────────────────────

sub_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

class PlanCreate(BaseModel):
    name: str
    price: float
    duration_days: int = 30
    features: Optional[str] = None

@sub_router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    from app.models.notification import SubscriptionPlan
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True))
    plans = result.scalars().all()
    return [{"id": p.id, "name": p.name, "price": p.price, "duration_days": p.duration_days, "features": p.features} for p in plans]

@sub_router.post("/plans", status_code=201)
async def create_plan(body: PlanCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.notification import SubscriptionPlan
    plan = SubscriptionPlan(id=str(uuid.uuid4()), **body.dict())
    db.add(plan)
    await db.commit()
    return {"id": plan.id, "name": plan.name}

class SubscribeRequest(BaseModel):
    plan_id: str
    payment_method: Optional[str] = "manual"

@sub_router.post("/subscribe")
async def subscribe(body: SubscribeRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.notification import SubscriptionPlan, Subscription, Payment
    from app.models.user import Student
    from datetime import date, timedelta

    res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=403, detail="Students only")

    res2 = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == body.plan_id))
    plan = res2.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    start = date.today()
    end = start + timedelta(days=plan.duration_days)

    sub = Subscription(id=str(uuid.uuid4()), student_id=student.id, plan_id=plan.id,
                       start_date=str(start), end_date=str(end))
    db.add(sub)
    await db.flush()

    payment = Payment(id=str(uuid.uuid4()), subscription_id=sub.id, amount=plan.price,
                      payment_status="completed", payment_method=body.payment_method, paid_at=datetime.utcnow())
    db.add(payment)
    await db.commit()
    return {"subscription_id": sub.id, "plan": plan.name, "end_date": str(end)}

# ─── Admin ────────────────────────────────────────────────────────────────────

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User, Student, Mentor, MentorApplication
    from app.models.skill import Skill
    from app.models.session import LiveSession

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    total_students = (await db.execute(select(func.count()).select_from(Student))).scalar()
    total_mentors = (await db.execute(select(func.count()).select_from(Mentor).where(Mentor.approved == True))).scalar()
    pending_apps = (await db.execute(select(func.count()).select_from(MentorApplication).where(MentorApplication.status == "pending"))).scalar()
    total_skills = (await db.execute(select(func.count()).select_from(Skill))).scalar()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_mentors": total_mentors,
        "pending_mentor_applications": pending_apps,
        "total_skills": total_skills,
    }

@admin_router.get("/users")
async def list_all_users(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User, UserProfile
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    out = []
    for u in users:
        res2 = await db.execute(select(UserProfile).where(UserProfile.user_id == u.id))
        profile = res2.scalar_one_or_none()
        out.append({
            "id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active,
            "created_at": u.created_at,
            "name": f"{profile.first_name} {profile.last_name}" if profile else "",
        })
    return out

@admin_router.post("/users/{user_id}/toggle-active")
async def toggle_user(user_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.commit()
    return {"is_active": user.is_active}

@admin_router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User, Student
    from app.models.skill import Skill
    
    # 1. User Count
    total_users_res = await db.execute(select(User).where(User.role != "admin"))
    users = len(total_users_res.scalars().all())
    
    # 2. Get random mock data based on active database rows
    skills_res = await db.execute(select(Skill))
    skills = skills_res.scalars().all()
    
    skill_popularity = []
    import random
    for i, s in enumerate(skills):
        skill_popularity.append({"skill": s.name[:10]+"..", "val": random.randint(20, 100)})
        
    if not skill_popularity:
        skill_popularity = [{"skill": "Comm", "val": 80}, {"skill": "Lead", "val": 60}]
        
    return {
       "total_users": users,
       "user_growth_data": [
           {"month": "Oct", "val": max(users - 20, 10)},
           {"month": "Nov", "val": max(users - 10, 15)}, 
           {"month": "Dec", "val": max(users - 5, 25)},
           {"month": "Jan", "val": users}
       ],
       "skill_popularity": skill_popularity,
       "module_completion": round(random.uniform(40, 85), 1),
       "quiz_avg_score": round(random.uniform(65, 95), 1),
       "revenue": {"Free": 60, "Premium": users * 15}
    }

@admin_router.get("/content")
async def get_all_content(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.content import Video, Activity
    from app.models.skill import SkillModule
    from app.models.user import User, UserProfile
    
    # Get Videos
    v_res = await db.execute(select(Video))
    videos = v_res.scalars().all()
    
    # Get Activities
    a_res = await db.execute(select(Activity))
    activities = a_res.scalars().all()
    
    out = []
    
    for v in videos:
        # get module name
        m_res = await db.execute(select(SkillModule).where(SkillModule.id == v.module_id))
        mod = m_res.scalar_one_or_none()
        
        # get uploaded by
        uploader = "Admin"
        if v.uploaded_by:
            u_res = await db.execute(select(User).where(User.id == v.uploaded_by))
            u = u_res.scalar_one_or_none()
            if u:
                uploader = u.email
                
        out.append({
            "id": v.id,
            "title": v.title,
            "module": mod.title if mod else "Unknown",
            "type": "Video",
            "uploaded_by": uploader,
            "status": "Active",
            "created_at": v.created_at
        })
        
    for a in activities:
        m_res = await db.execute(select(SkillModule).where(SkillModule.id == a.module_id))
        mod = m_res.scalar_one_or_none()
        
        out.append({
            "id": a.id,
            "title": a.title,
            "module": mod.title if mod else "Unknown",
            "type": "Activity",
            "uploaded_by": "System",
            "status": "Active",
            "created_at": a.created_at
        })
        
    out.sort(key=lambda x: str(x['created_at']), reverse=True)
    return out

@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}

@admin_router.get("/mentor-applications")
async def list_mentor_applications(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import MentorApplication, User, UserProfile
    result = await db.execute(select(MentorApplication).order_by(MentorApplication.submitted_at.desc()))
    apps = result.scalars().all()
    out = []
    for app in apps:
        res2 = await db.execute(select(User).where(User.id == app.user_id))
        user = res2.scalar_one_or_none()
        name = ""
        if user:
            res3 = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
            prof = res3.scalar_one_or_none()
            if prof:
                name = f"{prof.first_name} {prof.last_name}"
        out.append({
            "id": app.id,
            "user_id": app.user_id,
            "name": name,
            "email": user.email if user else "",
            "expertise": app.expertise,
            "resume_url": app.resume_url,
            "intro_video_url": app.intro_video_url,
            "status": app.status,
            "submitted_at": app.submitted_at
        })
    return out

@admin_router.post("/mentor/{app_id}/approve")
async def approve_mentor(app_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import MentorApplication, Mentor, User
    result = await db.execute(select(MentorApplication).where(MentorApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = "approved"
    app.reviewed_at = datetime.utcnow()
    
    # Update user role and mentor approved status
    res2 = await db.execute(select(User).where(User.id == app.user_id))
    user = res2.scalar_one_or_none()
    if user:
        user.role = "mentor"
    
    res3 = await db.execute(select(Mentor).where(Mentor.user_id == app.user_id))
    mentor = res3.scalar_one_or_none()
    if mentor:
        mentor.approved = True
        
    await db.commit()
    return {"message": "Mentor approved"}

@admin_router.post("/mentor/{app_id}/reject")
async def reject_mentor(app_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import MentorApplication
    result = await db.execute(select(MentorApplication).where(MentorApplication.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = "rejected"
    app.reviewed_at = datetime.utcnow()
    await db.commit()
    return {"message": "Mentor rejected"}


# ─── Messaging ────────────────────────────────────────────────────────────────

msg_router = APIRouter(prefix="/messages", tags=["Messaging"])

class NewConversation(BaseModel):
    other_user_id: str

class SendMessage(BaseModel):
    conversation_id: str
    message: str

@msg_router.post("/conversation", status_code=201)
async def start_conversation(body: NewConversation, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.notification import Conversation, ConversationMember
    conv = Conversation(id=str(uuid.uuid4()))
    db.add(conv)
    await db.flush()
    db.add(ConversationMember(id=str(uuid.uuid4()), conversation_id=conv.id, user_id=current_user.id))
    db.add(ConversationMember(id=str(uuid.uuid4()), conversation_id=conv.id, user_id=body.other_user_id))
    await db.commit()
    return {"conversation_id": conv.id}

@msg_router.post("/send")
async def send_message(body: SendMessage, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.notification import Message
    msg = Message(id=str(uuid.uuid4()), conversation_id=body.conversation_id,
                  sender_id=current_user.id, message=body.message)
    db.add(msg)
    await db.commit()
    return {"id": msg.id, "sent_at": msg.sent_at}

@msg_router.get("/conversation/{conv_id}")
async def get_messages(conv_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    from app.models.notification import Message
    result = await db.execute(select(Message).where(Message.conversation_id == conv_id).order_by(Message.sent_at))
    msgs = result.scalars().all()
    return [{"id": m.id, "sender_id": m.sender_id, "message": m.message, "sent_at": m.sent_at} for m in msgs]
