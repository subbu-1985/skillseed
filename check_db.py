
import asyncio
from app.database import engine
from sqlalchemy import text

async def check_db():
    async with engine.connect() as conn:
        tables = [
            "users", "skills", "modules", "videos", "quizzes", "questions",
            "mentor_applications", "sessions", "notifications"
        ]
        for table in tables:
            try:
                res = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: Table might not exist or error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
