import asyncio
from app.database import init_db

async def main():
    try:
        await init_db()
        print("init_db successful")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
