import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")  # student | mentor | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False)
    settings: Mapped["UserSettings"] = relationship("UserSettings", back_populates="user", uselist=False)
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(String(20), nullable=True)
    profile_image: Mapped[str] = mapped_column(Text, nullable=True)
    language_preference: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="profile")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    theme: Mapped[str] = mapped_column(String(20), default="light")

    user: Mapped["User"] = relationship("User", back_populates="settings")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(Text, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    grade: Mapped[int] = mapped_column(nullable=True)
    school_name: Mapped[str] = mapped_column(String(200), nullable=True)
    joined_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    skill_progress: Mapped[list["StudentSkillProgress"]] = relationship("StudentSkillProgress", back_populates="student")
    badges: Mapped[list["StudentBadge"]] = relationship("StudentBadge", back_populates="student")
    achievements: Mapped[list["StudentAchievement"]] = relationship("StudentAchievement", back_populates="student")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship("QuizAttempt", back_populates="student")
    video_progress: Mapped[list["VideoProgress"]] = relationship("VideoProgress", back_populates="student")

class StudentSkillProgress(Base):
    __tablename__ = "student_skill_progress"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="CASCADE"))
    progress_percentage: Mapped[float] = mapped_column(default=0.0)
    level: Mapped[int] = mapped_column(default=1)

    student: Mapped["Student"] = relationship("Student", back_populates="skill_progress")
    skill: Mapped["Skill"] = relationship("Skill")

class Mentor(Base):
    __tablename__ = "mentors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(default=0.0)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    skills: Mapped[list["MentorSkill"]] = relationship("MentorSkill", back_populates="mentor")
    sessions: Mapped[list["LiveSession"]] = relationship("LiveSession", back_populates="mentor")
    # applications: Mapped[list["MentorApplication"]] = relationship("MentorApplication", back_populates="mentor_user", foreign_keys="[MentorApplication.user_id]", primaryjoin="Mentor.user_id == MentorApplication.user_id", overlaps="")

class MentorSkill(Base):
    __tablename__ = "mentor_skills"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    mentor_id: Mapped[str] = mapped_column(String, ForeignKey("mentors.id", ondelete="CASCADE"))
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="CASCADE"))

    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill")

class MentorApplication(Base):
    __tablename__ = "mentor_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    resume_url: Mapped[str] = mapped_column(Text, nullable=True)
    intro_video_url: Mapped[str] = mapped_column(Text, nullable=True)
    expertise: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | rejected
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    admin_comment: Mapped[str] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    mentor_user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

# Import here to avoid circular
from app.models.skill import Skill  # noqa
from app.models.content import VideoProgress  # noqa
from app.models.quiz import QuizAttempt  # noqa
from app.models.gamification import StudentBadge, StudentAchievement  # noqa
from app.models.notification import Notification  # noqa
from app.models.session import LiveSession  # noqa
