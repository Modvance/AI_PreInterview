"""
Question API routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from ..schemas.interview import Question, QuestionType, DifficultyLevel
from ..services.question_service import get_question_service

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=List[Question])
async def get_all_questions():
    """Get all questions (for management)"""
    service = get_question_service()
    return service.get_all_questions()


@router.get("/types")
async def get_question_types():
    """Get question type list"""
    return [
        {"value": t.value, "label": get_type_label(t)}
        for t in QuestionType
    ]


@router.get("/difficulties")
async def get_difficulty_levels():
    """Get difficulty level list"""
    return [
        {"value": d.value, "label": get_difficulty_label(d)}
        for d in DifficultyLevel
    ]


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    """Get single question details"""
    service = get_question_service()
    question = service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.get("/by-type/{q_type}", response_model=List[Question])
async def get_questions_by_type(q_type: QuestionType):
    """Get questions by type"""
    service = get_question_service()
    return service.get_questions_by_type(q_type)


@router.get("/by-difficulty/{difficulty}", response_model=List[Question])
async def get_questions_by_difficulty(difficulty: DifficultyLevel):
    """Get questions by difficulty"""
    service = get_question_service()
    return service.get_questions_by_difficulty(difficulty)


def get_type_label(t: QuestionType) -> str:
    """Get type label"""
    labels = {
        QuestionType.LOGIC: "Logical Reasoning",
        QuestionType.MATH: "Mathematical Calculation",
        QuestionType.ALGORITHM: "Algorithm Thinking",
        QuestionType.SCENARIO: "Scenario Analysis"
    }
    return labels.get(t, t.value)


def get_difficulty_label(d: DifficultyLevel) -> str:
    """Get difficulty label"""
    labels = {
        DifficultyLevel.EASY: "Easy",
        DifficultyLevel.MEDIUM: "Medium",
        DifficultyLevel.HARD: "Hard"
    }
    return labels.get(d, d.value)
