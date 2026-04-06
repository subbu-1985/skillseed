import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Float, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

# ─── Notifications ───────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notif_type: Mapped[str] = mapped_column(String(50), default="general")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="notifications")

# ─── Subscriptions ────────────────────────────────────────────────────────────

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    features: Mapped[str] = mapped_column(Text, nullable=True)  # JSON list as text
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("subscription_plans.id"))
    start_date: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    subscription_id: Mapped[str] = mapped_column(String, ForeignKey("subscriptions.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float)
    payment_status: Mapped[str] = mapped_column(String(30), default="pending")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="payments")

# ─── Gamification ─────────────────────────────────────────────────────────────

class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(Text, nullable=True)
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id"), nullable=True)
    criteria: Mapped[str] = mapped_column(Text, nullable=True)

class StudentBadge(Base):
    __tablename__ = "student_badges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    badge_id: Mapped[str] = mapped_column(String, ForeignKey("badges.id", ondelete="CASCADE"))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="badges")
    badge: Mapped["Badge"] = relationship("Badge")

class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    criteria: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(Text, nullable=True)

class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id", ondelete="CASCADE"))
    achievement_id: Mapped[str] = mapped_column(String, ForeignKey("achievements.id", ondelete="CASCADE"))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement")

# ─── Messaging ────────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    members: Mapped[list["ConversationMember"]] = relationship("ConversationMember", back_populates="conversation")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation")

class ConversationMember(Base):
    __tablename__ = "conversation_members"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="members")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    sender_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

# ─── Admin ────────────────────────────────────────────────────────────────────

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    admin_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    setting_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=True)

# ─── Languages ────────────────────────────────────────────────────────────────

class Language(Base):
    __tablename__ = "languages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    translations: Mapped[list["Translation"]] = relationship("Translation", back_populates="language")

class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    language_id: Mapped[str] = mapped_column(String, ForeignKey("languages.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped["Language"] = relationship("Language", back_populates="translations")

from app.models.user import User, Student  # noqa
