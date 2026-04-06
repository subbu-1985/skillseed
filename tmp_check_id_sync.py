import asyncio
from app.database import AsyncSessionLocal
from app.models.quiz import Quiz
from app.models.skill import SkillModule
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    m_res = await db.execute(select(SkillModule))
    m_ids = set(m.id for m in m_res.scalars().all())
    
    q_res = await db.execute(select(Quiz))
    quizzes = q_res.scalars().all()
    q_m_ids = [q.module_id for q in quizzes]
    
    print(f"Total Modules in SQLite: {len(m_ids)}")
    print(f"Total Quizzes in SQLite: {len(quizzes)}")
    mismatched = [q.title for q in quizzes if q.module_id not in m_ids]
    print(f"Mismatched Quizzes: {len(mismatched)}")
    if mismatched:
        print(f"First mismatch: {mismatched[0]}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
