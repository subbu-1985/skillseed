from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from app.database import get_db
from app.models.skill import Skill, SkillModule, SkillLevel
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/skills", tags=["Skills"])

class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class ModuleCreate(BaseModel):
    skill_id: str
    title: str
    description: Optional[str] = None
    order_index: int = 0
    is_premium: bool = False

@router.get("")
async def list_skills(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Skill).options(selectinload(Skill.modules)))
    skills = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "icon": s.icon,
            "color": s.color,
            "module_count": len(s.modules),
            "created_at": s.created_at,
        }
        for s in skills
    ]

@router.get("/{skill_id}")
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Skill).where(Skill.id == skill_id).options(
            selectinload(Skill.modules), selectinload(Skill.levels)
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {
        "id": skill.id, "name": skill.name, "description": skill.description,
        "icon": skill.icon, "color": skill.color,
        "levels": [{"level_number": l.level_number, "title": l.title, "min_progress": l.min_progress} for l in skill.levels],
        "modules": [{"id": m.id, "title": m.title, "description": m.description, "order_index": m.order_index, "is_premium": m.is_premium} for m in sorted(skill.modules, key=lambda x: x.order_index)],
    }

@router.post("", status_code=201)
async def create_skill(body: SkillCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    skill = Skill(id=str(uuid.uuid4()), **body.dict())
    db.add(skill)
    await db.commit()
    return {"id": skill.id, "name": skill.name}

@router.put("/{skill_id}")
async def update_skill(skill_id: str, body: SkillCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    for k, v in body.dict(exclude_none=True).items():
        setattr(skill, k, v)
    await db.commit()
    return {"message": "Updated"}

@router.delete("/{skill_id}")
async def delete_skill(skill_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.delete(skill)
    await db.commit()
    return {"message": "Deleted"}

@router.get("/{skill_id}/modules")
async def list_modules(skill_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(SkillModule).where(SkillModule.skill_id == skill_id).order_by(SkillModule.order_index)
    )
    modules = result.scalars().all()
    return [{"id": m.id, "title": m.title, "description": m.description, "order_index": m.order_index, "is_premium": m.is_premium} for m in modules]

@router.post("/modules", status_code=201)
async def create_module(body: ModuleCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    module = SkillModule(id=str(uuid.uuid4()), **body.dict())
    db.add(module)
    await db.commit()
    return {"id": module.id, "title": module.title}

@router.delete("/modules/{module_id}")
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(SkillModule).where(SkillModule.id == module_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")
    await db.delete(m)
    await db.commit()
    return {"message": "Deleted"}
