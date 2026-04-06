from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    from app.models import user, skill, content, quiz, session, notification, gamification
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_admin()

async def seed_admin():
    from app.models.user import User, UserProfile
    from app.core.security import hash_password
    from sqlalchemy import select
    import uuid

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@skillseed.com"))
        existing = result.scalar_one_or_none()
        if not existing:
            admin_id = str(uuid.uuid4())
            admin = User(
                id=admin_id,
                email="admin@skillseed.com",
                password_hash=hash_password("admin123"),
                role="admin",
                is_active=True,
            )
            profile = UserProfile(
                id=str(uuid.uuid4()),
                user_id=admin_id,
                first_name="Admin",
                last_name="SkillSeed",
                language_preference="en",
            )
            db.add(admin)
            db.add(profile)
            await db.commit()
            print("Default admin seeded: admin@skillseed.com / admin123")
        else:
            print("Admin already exists.")
