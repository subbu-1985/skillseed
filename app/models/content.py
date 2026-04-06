import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    module_id: Mapped[str] = mapped_column(String, ForeignKey("skill_modules.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(Text, nullable=True)   # stored file path or URL
    thumbnail_url: Mapped[str] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    file_size_mb: Mapped[float] = mapped_column(Float, default=0.0)
    original_filename: Mapped[str] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    module: Mapped["SkillModule"] = relationship("SkillModule", back_populates="videos")
    progress: Mapped[list["VideoProgress"]] = relationship("VideoProgress", back_populates="video")

class VideoProgress(Base):
    __tablename__ = "video_progress"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    video_id: Mapped[str] = mapped_column(String, ForeignKey("videos.id", ondelete="CASCADE"))
    watched_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    completed: Mapped[bool] = mapped_column(default=False)
    last_watched: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="video_progress")
    video: Mapped["Video"] = relationship("Video", back_populates="progress")

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    module_id: Mapped[str] = mapped_column(String, ForeignKey("skill_modules.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    activity_type: Mapped[str] = mapped_column(String(50), default="task")  # task | puzzle | game
    content_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON stored as text
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    module: Mapped["SkillModule"] = relationship("SkillModule", back_populates="activities")
    completions: Mapped[list["ActivityCompletion"]] = relationship("ActivityCompletion", back_populates="activity")

class ActivityCompletion(Base):
    __tablename__ = "activity_completions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    activity_id: Mapped[str] = mapped_column(String, ForeignKey("activities.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="completed")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    activity: Mapped["Activity"] = relationship("Activity", back_populates="completions")

from app.models.skill import SkillModule  # noqa
from app.models.user import Student  # noqa
