import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer
from app.models.user import Student
from app.core.security import get_current_user, require_mentor, require_admin

router = APIRouter(prefix="/quiz", tags=["Quiz"])

class OptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "mcq"
    order_index: int = 0
    options: List[OptionCreate]

class QuizCreate(BaseModel):
    module_id: str
    title: str
    description: Optional[str] = None
    pass_percentage: float = 60.0
    questions: List[QuestionCreate] = []

class AnswerSubmit(BaseModel):
    question_id: str
    selected_option_id: str

class QuizSubmit(BaseModel):
    answers: List[AnswerSubmit]

@router.get("/module/{module_id}")
async def list_quizzes(module_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Quiz).where(Quiz.module_id == module_id))
    quizzes = result.scalars().all()
    return [{"id": q.id, "title": q.title, "description": q.description, "pass_percentage": q.pass_percentage} for q in quizzes]

from sqlalchemy import func

import os

@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: str, 
    skill_name: Optional[str] = None, 
    order_index: Optional[int] = None, 
    quiz_title: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    _=Depends(get_current_user)
):
    log_file = "quiz_sync_log.txt"
    log_msg = f"--- FETCH REQUEST: id={quiz_id}, skill={skill_name}, order={order_index}, title={quiz_title} ---\n"
    
    # 1. Try Title-based lookup FIRST (Most accurate for sync)
    quiz = None
    if quiz_title:
        res = await db.execute(select(Quiz).where(Quiz.title == quiz_title))
        quiz = res.scalar_one_or_none()
        if quiz:
            log_msg += f"  - SUCCESS: Found quiz via EXACT title match: '{quiz_title}'\n"

    # 2. Try metadata-based lookup 
    if not quiz and skill_name and order_index is not None:
        from app.models.skill import Skill, SkillModule
        skill_res = await db.execute(select(Skill).where(Skill.name.ilike(f"%{skill_name}%")))
        skill = skill_res.scalar_one_or_none()
        if skill:
            log_msg += f"  - Found matching skill: {skill.name} ({skill.id})\n"
            # Try both raw order and +1 shift
            for idx in [order_index, order_index + 1]:
                res = await db.execute(
                    select(Quiz).join(SkillModule).where(
                        SkillModule.skill_id == skill.id,
                        SkillModule.order_index == idx
                    )
                )
                quiz = res.scalar_one_or_none()
                if quiz:
                    log_msg += f"  - SUCCESS: Found quiz via Skill={skill_name} and Order={idx} (ID={quiz.id})\n"
                    break
            if not quiz:
                log_msg += f"  - FAILED: No Quiz found for Skill={skill.id} with Order in [ {order_index}, {order_index + 1} ]\n"
        else:
            log_msg += f"  - FAILED: No skill found matching '{skill_name}'\n"

    # 2. Try direct ID if metadata failed
    if not quiz:
        quiz_res = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = quiz_res.scalar_one_or_none()
        if quiz:
            log_msg += f"  - SUCCESS: Found quiz via direct ID match: {quiz_id}\n"

    # 3. Fallback: Search for quiz by title contains
    if not quiz:
        res = await db.execute(select(Quiz).where(Quiz.title.ilike(f"%{quiz_id}%")))
        quiz = res.scalar_one_or_none()
        if quiz:
            log_msg += f"  - SUCCESS: Found quiz via title-match with '{quiz_id}'\n"

    # Log the result
    with open(log_file, "a") as f:
        f.write(log_msg)

    # 2. Fallback: Search for quiz by module_id if the ID didn't match
    if not quiz:
        from app.models.skill import SkillModule, Skill
        # Try finding a module whose ID or title contains the "quiz_id" 
        # (Useful if the frontend passes the Firebase module ID like 'com1' or 'cr1')
        mod_res = await db.execute(
            select(SkillModule).where(
                (SkillModule.id == quiz_id) | 
                (SkillModule.title.ilike(f"%{quiz_id}%")) |
                (SkillModule.id.ilike(f"{quiz_id}%"))
            )
        )
        module = mod_res.scalar_one_or_none()
        
        # If still no luck, take the first 2-3 characters (e.g., 'cr' from 'cr1') and match against Skill names
        if not module and len(quiz_id) >= 2:
            prefix = quiz_id[:2].lower()
            skill_res = await db.execute(select(Skill).where(Skill.name.ilike(f"{prefix}%")))
            skill = skill_res.scalar_one_or_none()
            if skill:
                # Try to find the module by its order index (last char of 'cr1' -> 1)
                order_str = quiz_id[-1]
                if order_str.isdigit():
                    order_val = int(order_str)
                    m_res = await db.execute(select(SkillModule).where(
                        SkillModule.skill_id == skill.id, 
                        SkillModule.order_index == order_val
                    ))
                    module = m_res.scalar_one_or_none()

        if module:
            q_lookup = await db.execute(select(Quiz).where(Quiz.module_id == module.id))
            quiz = q_lookup.scalar_one_or_none()

    # 3. Last Resort Fallback: Search for any quiz whose title matches roughly
    if not quiz:
        res = await db.execute(select(Quiz).where(Quiz.title.ilike(f"%{quiz_id}%")))
        quiz = res.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail=f"Quiz '{quiz_id}' not found in SQLite backend.")

    # Fetch 3 random questions from the pool
    q_res = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.quiz_id == quiz.id)
        .options(selectinload(QuizQuestion.options))
        .order_by(func.random())
        .limit(3)
    )
    questions = q_res.scalars().all()

    return {
        "id": quiz.id,
        "module_id": quiz.module_id,
        "title": quiz.title,
        "pass_percentage": quiz.pass_percentage,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": [{"id": o.id, "option_text": o.option_text} for o in q.options]
            }
            for q in questions
        ]
    }

@router.post("", status_code=201)
async def create_quiz(body: QuizCreate, db: AsyncSession = Depends(get_db), _=Depends(require_mentor)):
    quiz = Quiz(id=str(uuid.uuid4()), module_id=body.module_id, title=body.title,
                description=body.description, pass_percentage=body.pass_percentage)
    db.add(quiz)
    await db.flush()

    for q_data in body.questions:
        question = QuizQuestion(
            id=str(uuid.uuid4()), quiz_id=quiz.id,
            question_text=q_data.question_text, question_type=q_data.question_type,
            order_index=q_data.order_index
        )
        db.add(question)
        await db.flush()
        for opt in q_data.options:
            db.add(QuizOption(id=str(uuid.uuid4()), question_id=question.id,
                              option_text=opt.option_text, is_correct=opt.is_correct))

    await db.commit()
    return {"id": quiz.id, "title": quiz.title}

@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    body: QuizSubmit,
    skill_name: Optional[str] = None,
    order_index: Optional[int] = None,
    quiz_title: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=403, detail="Student only")

    # 1. Try Title-based lookup FIRST (Most accurate)
    quiz = None
    if quiz_title:
        res = await db.execute(select(Quiz).where(Quiz.title == quiz_title))
        quiz = res.scalar_one_or_none()

    # 2. Try metadata lookup 
    if not quiz and skill_name and order_index is not None:
        from app.models.skill import Skill, SkillModule
        # Normalize index
        skill_res = await db.execute(select(Skill).where(Skill.name.ilike(f"%{skill_name}%")))
        skill = skill_res.scalar_one_or_none()
        if skill:
            for idx in [order_index, order_index + 1]:
                res = await db.execute(
                    select(Quiz).join(SkillModule).where(
                        SkillModule.skill_id == skill.id,
                        SkillModule.order_index == idx
                    )
                )
                quiz = res.scalar_one_or_none()
                if quiz: break

    # 3. Direct ID
    if not quiz:
        result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalar_one_or_none()
    
    # 4. Fallback search by title contains
    if not quiz:
        res = await db.execute(select(Quiz).where(Quiz.title.ilike(f"%{quiz_id}%")))
        quiz = res.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Score calculation
    correct = 0
    total = len(body.answers)
    for ans in body.answers:
        res = await db.execute(select(QuizOption).where(
            QuizOption.id == ans.selected_option_id,
            QuizOption.is_correct == True
        ))
        if res.scalar_one_or_none():
            correct += 1

    score = (correct / total * 100) if total > 0 else 0
    passed = score >= quiz.pass_percentage

    attempt = QuizAttempt(
        id=str(uuid.uuid4()), student_id=student.id, quiz_id=quiz.id,
        score=score, passed=passed
    )
    db.add(attempt)
    await db.flush()

    for ans in body.answers:
        db.add(QuizAnswer(id=str(uuid.uuid4()), attempt_id=attempt.id,
                          question_id=ans.question_id, selected_option_id=ans.selected_option_id))

    await db.commit()
    return {"score": round(score, 1), "correct": correct, "total": total, "passed": passed}


# ─── Add a question to an existing quiz (Mentor / Admin) ───────────────────────
@router.post("/{quiz_id}/questions", status_code=201)
async def add_question(
    quiz_id: str,
    body: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_mentor),
):
    res = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = res.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    question = QuizQuestion(
        id=str(uuid.uuid4()), quiz_id=quiz_id,
        question_text=body.question_text, question_type=body.question_type,
        order_index=body.order_index
    )
    db.add(question)
    await db.flush()
    for opt in body.options:
        db.add(QuizOption(id=str(uuid.uuid4()), question_id=question.id,
                          option_text=opt.option_text, is_correct=opt.is_correct))
    await db.commit()
    return {"id": question.id, "question_text": question.question_text}


# ─── Delete a question from a quiz (Mentor / Admin) ────────────────────────────
@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_mentor),
):
    res = await db.execute(select(QuizQuestion).where(QuizQuestion.id == question_id))
    q = res.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(q)
    await db.commit()
    return {"message": "Question deleted"}


# ─── My quiz history (Student) ─────────────────────────────────────────────────
@router.get("/history/me")
async def my_quiz_history(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    res = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=403, detail="Students only")

    res2 = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.student_id == student.id)
        .options(selectinload(QuizAttempt.quiz))
        .order_by(QuizAttempt.attempted_at.desc())
    )
    attempts = res2.scalars().all()

    out = []
    for a in attempts:
        quiz = a.quiz
        # get module + skill name
        from app.models.skill import SkillModule, Skill
        mod_res = await db.execute(select(SkillModule).where(SkillModule.id == quiz.module_id))
        mod = mod_res.scalar_one_or_none()
        skill_name = ""
        module_name = ""
        if mod:
            module_name = mod.title
            sk_res = await db.execute(select(Skill).where(Skill.id == mod.skill_id))
            sk = sk_res.scalar_one_or_none()
            if sk:
                skill_name = sk.name
        out.append({
            "attempt_id": a.id,
            "quiz_id": a.quiz_id,
            "quiz_title": quiz.title if quiz else "",
            "skill_name": skill_name,
            "module_name": module_name,
            "score": round(a.score, 1),
            "passed": a.passed,
            "attempted_at": a.attempted_at,
        })
    return out


# ─── Mentor: view quiz results for their students ──────────────────────────────
@router.get("/results/students", dependencies=[Depends(require_mentor)])
async def mentor_student_results(db: AsyncSession = Depends(get_db), _=Depends(require_mentor)):
    from app.models.user import User, UserProfile
    from app.models.skill import SkillModule, Skill

    res = await db.execute(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz), selectinload(QuizAttempt.student))
        .order_by(QuizAttempt.attempted_at.desc())
    )
    attempts = res.scalars().all()

    out = []
    for a in attempts:
        # Student name
        student_name = ""
        if a.student:
            u_res = await db.execute(select(User).where(User.id == a.student.user_id))
            u = u_res.scalar_one_or_none()
            if u:
                p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == u.id))
                p = p_res.scalar_one_or_none()
                student_name = f"{p.first_name} {p.last_name}" if p else u.email

        quiz = a.quiz
        skill_name = ""
        module_name = ""
        if quiz:
            mod_res = await db.execute(select(SkillModule).where(SkillModule.id == quiz.module_id))
            mod = mod_res.scalar_one_or_none()
            if mod:
                module_name = mod.title
                sk_res = await db.execute(select(Skill).where(Skill.id == mod.skill_id))
                sk = sk_res.scalar_one_or_none()
                if sk:
                    skill_name = sk.name

        out.append({
            "attempt_id": a.id,
            "student_id": a.student_id,
            "student_name": student_name,
            "quiz_title": quiz.title if quiz else "",
            "skill_name": skill_name,
            "module_name": module_name,
            "score": round(a.score, 1),
            "passed": a.passed,
            "attempted_at": a.attempted_at,
        })
    return out


# ─── Admin: all students quiz + activity summary ────────────────────────────────
@router.get("/admin/overview", dependencies=[Depends(require_admin)])
async def admin_quiz_overview(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User, UserProfile, Student
    from app.models.content import ActivityCompletion
    from sqlalchemy import func

    # All students
    res = await db.execute(select(Student))
    students = res.scalars().all()

    out = []
    for student in students:
        u_res = await db.execute(select(User).where(User.id == student.user_id))
        u = u_res.scalar_one_or_none()
        p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == student.user_id))
        p = p_res.scalar_one_or_none()
        student_name = f"{p.first_name} {p.last_name}" if p else (u.email if u else "Unknown")

        # Quiz stats
        qa_res = await db.execute(select(QuizAttempt).where(QuizAttempt.student_id == student.id))
        attempts = qa_res.scalars().all()
        total_attempts = len(attempts)
        passed = sum(1 for a in attempts if a.passed)
        avg_score = round(sum(a.score for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0

        # Activity completions
        ac_res = await db.execute(select(ActivityCompletion).where(ActivityCompletion.student_id == student.id))
        activities_done = len(ac_res.scalars().all())

        out.append({
            "student_id": student.id,
            "student_name": student_name,
            "email": u.email if u else "",
            "total_quiz_attempts": total_attempts,
            "quizzes_passed": passed,
            "avg_score": avg_score,
            "activities_completed": activities_done,
        })

    return out
