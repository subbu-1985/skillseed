import asyncio
from app.database import AsyncSessionLocal
from app.models.quiz import Quiz
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    res = await db.execute(select(Quiz))
    titles = [q.title for q in res.scalars().all()]
    print(f"Total Quizzes: {len(titles)}")
    if titles:
        print(f"Sample Title: '{titles[0]}'")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
