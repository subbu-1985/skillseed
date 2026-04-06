import asyncio
import json
from app.database import engine
from sqlalchemy import text

async def export_to_json():
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("""
                SELECT u.id, u.email, u.role, p.first_name, p.last_name, u.created_at
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
            """))
            rows = res.fetchall()
            
            users_list = []
            for row in rows:
                users_list.append({
                    "id": row[0],
                    "email": row[1],
                    "role": row[2],
                    "first_name": row[3] or "",
                    "last_name": row[4] or "",
                    "registered_at": str(row[5]) if row[5] else None
                })
                
            with open("users_data.json", "w") as f:
                json.dump(users_list, f, indent=4)
                
            print(f"Successfully exported {len(users_list)} users to users_data.json")
        except Exception as e:
            print(f"Error exporting data: {e}")

if __name__ == "__main__":
    asyncio.run(export_to_json())
