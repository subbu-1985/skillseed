import asyncio
from app.database import AsyncSessionLocal
from app.models.skill import Skill, SkillModule
from sqlalchemy import select

async def check():
    db = AsyncSessionLocal()
    res = await db.execute(select(Skill))
    skills = res.scalars().all()
    print("SKILLS:")
    for s in skills:
        print(f"  {s.id}: {s.name}")
        res2 = await db.execute(select(SkillModule).where(SkillModule.skill_id == s.id))
        mods = res2.scalars().all()
        for m in mods:
            print(f"    {m.id}: {m.title} (order={m.order_index})")
    await db.close()

if __name__ == "__main__":
    asyncio.run(check())
