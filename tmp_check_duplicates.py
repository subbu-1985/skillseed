import asyncio
from app.database import AsyncSessionLocal
from app.models.quiz import Quiz
from sqlalchemy import select, func

async def check():
    db = AsyncSessionLocal()
    # Check for duplicate titles
    res = await db.execute(select(Quiz.title, func.count(Quiz.id)).group_by(Quiz.title).having(func.count(Quiz.id) > 1))
    for r in res.all():
        print(f"Duplicate Quiz: '{r[0]}', Count: {r[1]}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
