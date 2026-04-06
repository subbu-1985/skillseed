import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User, UserProfile, UserSettings, Student, Mentor
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "student"  # student | mentor
    first_name: str = ""
    last_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    if body.role not in ("student", "mentor"):
        raise HTTPException(status_code=400, detail="Role must be student or mentor")

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        is_active=True,
    )
    profile = UserProfile(
        id=str(uuid.uuid4()),
        user_id=user_id,
        first_name=body.first_name,
        last_name=body.last_name,
        language_preference="en",
    )
    settings = UserSettings(id=str(uuid.uuid4()), user_id=user_id)
    db.add(user)
    db.add(profile)
    db.add(settings)

    if body.role == "student":
        student = Student(id=str(uuid.uuid4()), user_id=user_id)
        db.add(student)
    elif body.role == "mentor":
        mentor = Mentor(id=str(uuid.uuid4()), user_id=user_id, approved=False)
        db.add(mentor)

    await db.commit()

    # --- Save JSON Backup ---
    import json
    import os
    backup_file = "users_data.json"
    backup_list = []
    if os.path.exists(backup_file):
        try:
            with open(backup_file, "r") as f:
                backup_list = json.load(f)
        except json.JSONDecodeError:
            pass
    backup_list.append({
        "id": user_id,
        "email": body.email,
        "role": body.role,
        "first_name": body.first_name,
        "last_name": body.last_name,
        "registered_at": str(user.created_at) if hasattr(user, 'created_at') else None
    })
    try:
        with open(backup_file, "w") as f:
            json.dump(backup_list, f, indent=4)
    except Exception:
        pass
    # ------------------------

    token = create_access_token({"sub": user_id, "role": body.role})
    return {"access_token": token, "token_type": "bearer", "role": body.role, "user_id": user_id}

@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "user_id": user.id}

@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_db), current_user: User = Depends(lambda: None)):
    # Uses security dependency in main
    pass
