import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.models.skill import Skill, SkillLevel, SkillModule
from app.models.content import Video, Activity

async def seed_content():
    async with AsyncSessionLocal() as db:
        # Check if skills exist
        from sqlalchemy import select
        res = await db.execute(select(Skill))
        if res.scalars().first():
            print("Skills already seeded.")
            return

        skills_data = [
            ("Communication", "Master the art of expressing ideas clearly.", "blue"),
            ("Leadership", "Learn how to inspire and guide others.", "purple"),
            ("Time Management", "Organize and plan your time effectively.", "orange"),
            ("Teamwork", "Collaborate efficiently with diverse groups.", "green"),
            ("Creativity", "Unleash your imaginative potential.", "pink"),
            ("Critical Thinking", "Analyze information objectively.", "teal"),
            ("Adaptability", "Thrive in changing environments.", "amber"),
        ]

        for name, desc, color in skills_data:
            skill_id = str(uuid.uuid4())
            skill = Skill(
                id=skill_id,
                name=name,
                description=desc,
                color=color
            )
            db.add(skill)
            
            # Add a module
            module_id = str(uuid.uuid4())
            module = SkillModule(
                id=module_id,
                skill_id=skill_id,
                title=f"Introduction to {name}",
                description=f"Basic concepts of {name}.",
                order_index=1
            )
            db.add(module)
            
            # Add a video to module
            video = Video(
                id=str(uuid.uuid4()),
                module_id=module_id,
                title=f"What is {name}?",
                description=f"A video explaining {name}.",
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Placeholder
                order_index=1
            )
            db.add(video)

        await db.commit()
        print("Test skills and modules seeded.")

if __name__ == "__main__":
    asyncio.run(seed_content())
