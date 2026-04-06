import asyncio
from app.database import AsyncSessionLocal
from app.models.skill import SkillModule
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    res = await db.execute(select(SkillModule))
    for m in res.scalars().all():
        print(f"Module: '{m.title}', Order Index: {m.order_index}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
