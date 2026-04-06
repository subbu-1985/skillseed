import asyncio
from app.database import AsyncSessionLocal
from app.models.quiz import Quiz, QuizQuestion
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def check():
    db = AsyncSessionLocal()
    # Use selectinload to load questions
    res = await db.execute(select(Quiz).options(selectinload(Quiz.questions)))
    quizzes = res.scalars().all()
    print(f"Quizzes: {len(quizzes)}")
    for q in quizzes:
        print(f"  Quiz: '{q.title}', Questions count={len(q.questions)}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
