import asyncio
from app.database import AsyncSessionLocal
from app.models.skill import Skill
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    res = await db.execute(select(Skill))
    for s in res.scalars().all():
        print(f"Skill: '{s.name}'")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
