import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(200), nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    modules: Mapped[list["SkillModule"]] = relationship("SkillModule", back_populates="skill")
    levels: Mapped[list["SkillLevel"]] = relationship("SkillLevel", back_populates="skill")

class SkillLevel(Base):
    __tablename__ = "skill_levels"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="CASCADE"))
    level_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    min_progress: Mapped[float] = mapped_column(default=0.0)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="levels")

class SkillModule(Base):
    __tablename__ = "skill_modules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_premium: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="modules")
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="module")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="module")
    quizzes: Mapped[list["Quiz"]] = relationship("Quiz", back_populates="module")

from app.models.content import Video, Activity  # noqa
from app.models.quiz import Quiz  # noqa
