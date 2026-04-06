
import asyncio
import uuid
import random
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User, UserProfile, Student, Mentor
from app.models.skill import Skill, SkillLevel, SkillModule
from app.models.content import Video, Activity
from app.models.quiz import Quiz, QuizQuestion, QuizOption
from app.models.notification import SubscriptionPlan
from app.core.security import hash_password
from sqlalchemy import select

async def seed_all():
    print("Starting comprehensive seeding...")
    
    # Reset tables for a perfect start
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded (now it won't be as we just dropped tables)
        res = await db.execute(select(Skill))
        if res.scalars().first():
            print("Database already has skills. Skipping seeding to avoid duplicates.")
            return

        # 2. Seed Subscription Plans
        plans = [
            ("Free", 0.0, 9999, "Access to basic modules, Limited quizzes"),
            ("Pro", 12.99, 30, "All modules, Unlimited quizzes, 1-on-1 sessions, Certification"),
            ("Yearly Pro", 99.99, 365, "All Pro features, 35% discount, Bonus workshops"),
        ]
        for name, price, days, features in plans:
            plan = SubscriptionPlan(id=str(uuid.uuid4()), name=name, price=price, duration_days=days, features=features)
            db.add(plan)

        # 3. Seed Users (Mentor, Student)
        users_data = [
            ("mentor1@skillseed.com", "mentor123", "mentor", "John", "Mentor"),
            ("mentor2@skillseed.com", "mentor123", "mentor", "Sarah", "Coach"),
            ("student1@skillseed.com", "student123", "student", "Alice", "Learner"),
        ]
        for email, pwd, role, f_name, l_name in users_data:
            id = str(uuid.uuid4())
            user = User(id=id, email=email, password_hash=hash_password(pwd), role=role, is_active=True)
            profile = UserProfile(id=str(uuid.uuid4()), user_id=id, first_name=f_name, last_name=l_name)
            db.add(user)
            db.add(profile)
            if role == "student":
                db.add(Student(id=str(uuid.uuid4()), user_id=id, grade=6, school_name="SkillSeed Academy"))
            elif role == "mentor":
                db.add(Mentor(id=str(uuid.uuid4()), user_id=id, bio=f"Expert in soft skills with 10 years of experience.", approved=True))

        # 4. Seed Skills & Modules
        skills_data = [
            ("Communication", "Master the art of expressing ideas clearly.", "0xFF2196F3", "record_voice_over"),
            ("Leadership", "Learn how to inspire and guide others.", "0xFF9C27B0", "groups"),
            ("Time Management", "Organize and plan your time effectively.", "0xFFFF9800", "timer"),
            ("Teamwork", "Collaborate efficiently with diverse groups.", "0xFF4CAF50", "handshake"),
            ("Creativity", "Unleash your imaginative potential.", "0xFFE91E63", "lightbulb"),
            ("Critical Thinking", "Analyze information objectively.", "0xFF009688", "psychology"),
            ("Adaptability", "Thrive in changing environments.", "0xFFFFC107", "vibrate"),
        ]

        for name, desc, color, icon in skills_data:
            skill_id = str(uuid.uuid4())
            skill = Skill(id=skill_id, name=name, description=desc, color=color, icon=icon)
            db.add(skill)

            # Levels
            for i in range(1, 4):
                db.add(SkillLevel(id=str(uuid.uuid4()), skill_id=skill_id, level_number=i, title=f"Level {i}: {name} Mastery"))

            # Modules
            for i in range(1, 4):
                module_id = str(uuid.uuid4())
                module = SkillModule(
                    id=module_id,
                    skill_id=skill_id,
                    title=f"{name} Basics {i}" if i==1 else f"Advanced {name} {i}",
                    description=f"Deep dive into part {i} of {name}.",
                    order_index=i
                )
                db.add(module)

                # Videos
                db.add(Video(
                    id=str(uuid.uuid4()),
                    module_id=module_id,
                    title=f"Introduction to {name} {i}",
                    description="Watch this to get started.",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    order_index=1
                ))

                # Activities
                db.add(Activity(
                    id=str(uuid.uuid4()),
                    module_id=module_id,
                    title=f"Reflective Journal: {name}",
                    description="Write down 3 things you learned about this skill.",
                    activity_type="writing"
                ))

                # Quiz
                quiz_id = str(uuid.uuid4())
                quiz = Quiz(id=quiz_id, module_id=module_id, title=f"{name} Knowledge Check {i}", pass_percentage=70.0)
                db.add(quiz)

                # Questions
                for j in range(1, 4):
                    q_id = str(uuid.uuid4())
                    q = QuizQuestion(id=q_id, quiz_id=quiz_id, question_text=f"Question {j} about {name}?", question_type="mcq")
                    db.add(q)
                    # Options
                    for k in range(1, 5):
                        db.add(QuizOption(id=str(uuid.uuid4()), question_id=q_id, option_text=f"Option {k}", is_correct=(k==1)))

        await db.commit()

        print("Success: Comprehensive seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_all())
