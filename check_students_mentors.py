import asyncio
from app.database import engine
from sqlalchemy import text

async def check_db():
    async with engine.connect() as conn:
        tables = [
            "users", "students", "mentors", "mentor_applications", "sessions"
        ]
        print("--- Database Record Counts ---")
        for table in tables:
            try:
                res = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"{table.ljust(20)}: {count}")
            except Exception as e:
                print(f"{table.ljust(20)}: ERROR (Table might not exist: {e})")
        
        # Also query users by role
        print("\n--- Users by Role ---")
        try:
            res = await conn.execute(text("SELECT role, COUNT(*) FROM users GROUP BY role"))
            roles = res.fetchall()
            for role, count in roles:
                print(f"Role '{role}': {count}")
        except Exception as e:
            print(f"Error querying roles: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
