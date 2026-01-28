"""
Interview API routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from ..schemas.interview import (
    CreateInterviewRequest, InterviewSessionResponse, 
    SubmitAnswerRequest, SubmitAnswerResponse,
    InterviewReport, MessageResponse, Question, QuestionDisplay
)
from ..services.interview_service import get_interview_service

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/sessions", response_model=InterviewSessionResponse)
async def create_interview_session(request: CreateInterviewRequest):
    """
    Create interview session
    
    - **candidate_name**: Candidate name (optional)
    - **position**: Applied position (optional)
    - **resume_data**: Parsed resume data (optional, reserved)
    - **jd_data**: Parsed JD data (optional, reserved)
    - **question_count**: Number of questions, default 3
    """
    service = get_interview_service()
    session = service.create_session(request)
    welcome_message = service.get_welcome_message(session)
    
    return InterviewSessionResponse(
        id=session.id,
        candidate_name=session.candidate_name,
        position=session.position,
        status=session.status,
        question_count=session.question_count,
        current_question_index=session.current_question_index,
        welcome_message=welcome_message,
        created_at=session.created_at
    )


@router.post("/sessions/{session_id}/start")
async def start_interview(session_id: str):
    """
    Start interview
    
    Returns the first question
    """
    service = get_interview_service()
    session = service.start_interview(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话未找到或已开始"
        )
    
    # Get first question
    question = service.get_current_question(session_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="没有可用题目"
        )
    
    return {
        "success": True,
        "message": "面试已开始",
        "data": {
            "session_id": session_id,
            "current_index": 0,
            "total_questions": session.question_count,
            "question": service.get_question_for_display(question)
        }
    }


@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get interview session info"""
    service = get_interview_service()
    session = service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话未找到"
        )
    
    return {
        "id": session.id,
        "candidate_name": session.candidate_name,
        "position": session.position,
        "status": session.status,
        "question_count": session.question_count,
        "current_question_index": session.current_question_index,
        "created_at": session.created_at,
        "completed_at": session.completed_at
    }


@router.get("/sessions/{session_id}/current-question")
async def get_current_question(session_id: str):
    """Get current question"""
    service = get_interview_service()
    session = service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话未找到"
        )
    
    question = service.get_current_question(session_id)
    if not question:
        return {
            "success": False,
            "message": "没有更多题目或面试未开始",
            "data": None
        }
    
    return {
        "success": True,
        "data": {
            "current_index": session.current_question_index,
            "total_questions": session.question_count,
            "question": service.get_question_for_display(question)
        }
    }


@router.post("/sessions/{session_id}/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """
    Submit answer
    
    - **question_id**: Question ID
    - **selected_option**: Selected option (A/B/C/D)
    - **explanation**: Problem-solving approach explanation
    """
    service = get_interview_service()
    
    try:
        evaluation, has_next, next_question = await service.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            selected_option=request.selected_option,
            explanation=request.explanation
        )
        
        # Get display version of next question
        next_q_display = None
        if next_question:
            next_q_display = QuestionDisplay(**service.get_question_for_display(next_question))
        
        return SubmitAnswerResponse(
            evaluation=evaluation,
            has_next_question=has_next,
            next_question=next_q_display
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions/{session_id}/feedback/{question_id}")
async def get_feedback(session_id: str, question_id: str):
    """Get interviewer feedback (for TTS)"""
    service = get_interview_service()
    feedback = await service.get_feedback_text(session_id, question_id)
    
    return {
        "success": True,
        "feedback": feedback
    }


@router.get("/sessions/{session_id}/report", response_model=InterviewReport)
async def get_interview_report(session_id: str):
    """
    Get interview report
    
    Only available after interview is completed
    """
    service = get_interview_service()
    report = await service.generate_report(session_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报告不可用，面试可能尚未完成"
        )
    
    return report


@router.post("/sessions/{session_id}/cancel", response_model=MessageResponse)
async def cancel_interview(session_id: str):
    """Cancel interview"""
    service = get_interview_service()
    success = service.cancel_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法取消此会话"
        )
    
    return MessageResponse(
        success=True,
        message="面试已取消"
    )


# ============ Reserved Interfaces ============

@router.post("/parse/resume")
async def parse_resume(data: dict):
    """
    Resume parsing interface (reserved)
    
    To be integrated with resume parsing service
    """
    # TODO: Call resume parsing service
    return {
        "success": False,
        "message": "简历解析服务尚未实现",
        "data": None
    }


@router.post("/parse/jd")
async def parse_jd(data: dict):
    """
    JD parsing interface (reserved)
    
    To be integrated with JD parsing service
    """
    # TODO: Call JD parsing service
    return {
        "success": False,
        "message": "JD解析服务尚未实现",
        "data": None
    }
