import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class LiveSession(Base):
    __tablename__ = "live_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    mentor_id: Mapped[str] = mapped_column(String, ForeignKey("mentors.id", ondelete="CASCADE"))
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    session_date: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=60)
    meeting_link: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="sessions")
    attendees: Mapped[list["SessionAttendance"]] = relationship("SessionAttendance", back_populates="session")

class SessionAttendance(Base):
    __tablename__ = "session_attendance"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("live_sessions.id", ondelete="CASCADE"))
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    attended: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    session: Mapped["LiveSession"] = relationship("LiveSession", back_populates="attendees")

from app.models.user import Mentor  # noqa
