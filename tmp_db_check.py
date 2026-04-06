import asyncio
from app.database import AsyncSessionLocal
from app.models.quiz import Quiz, QuizQuestion
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    res1 = await db.execute(select(Quiz))
    quizzes = res1.scalars().all()
    res2 = await db.execute(select(QuizQuestion))
    questions = res2.scalars().all()
    print(f"Quizzes found: {len(quizzes)}")
    print(f"Questions found: {len(questions)}")
    for q in quizzes:
        print(f"  Quiz ID: {q.id}, Title: {q.title}, Module ID: {q.module_id}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
