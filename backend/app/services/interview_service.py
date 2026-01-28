"""
Interview Service - Manages interview sessions and workflow
"""
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from ..schemas.interview import (
    InterviewSession, InterviewStatus, CreateInterviewRequest,
    SubmitAnswerRequest, AnswerRecord, Question,
    InterviewReport, AnswerEvaluation
)
from .question_service import get_question_service
from .ai_service import get_ai_service


class InterviewService:
    """Interview service"""
    
    def __init__(self):
        # In-memory storage (can be replaced with database later)
        self.sessions: Dict[str, InterviewSession] = {}
        self.question_service = get_question_service()
        self.ai_service = get_ai_service()
    
    def create_session(self, request: CreateInterviewRequest) -> InterviewSession:
        """
        Create interview session
        
        Args:
            request: Create request
        
        Returns:
            Interview session
        """
        session_id = str(uuid.uuid4())
        
        # Select questions automatically based on difficulty
        # If question_count is provided, use it; otherwise auto-determine (2 or 3)
        if request.question_count:
            # Use provided count
            if request.resume_data or request.jd_data:
                questions = self.question_service.select_questions_with_resume_jd(
                    count=request.question_count,
                    resume_data=request.resume_data,
                    jd_data=request.jd_data
                )
            else:
                questions = self.question_service.select_questions_for_interview(
                    count=request.question_count
                )
        else:
            # Auto-select based on difficulty (2 or 3 questions)
            questions = self.question_service.auto_select_questions(
                resume_data=request.resume_data,
                jd_data=request.jd_data
            )
        
        session = InterviewSession(
            id=session_id,
            candidate_name=request.candidate_name,
            position=request.position,
            status=InterviewStatus.PENDING,
            question_count=len(questions),
            current_question_index=0,
            questions=questions,
            answers=[],
            created_at=datetime.now()
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def start_interview(self, session_id: str) -> Optional[InterviewSession]:
        """Start interview"""
        session = self.sessions.get(session_id)
        if session and session.status == InterviewStatus.PENDING:
            session.status = InterviewStatus.IN_PROGRESS
        return session
    
    def get_current_question(self, session_id: str) -> Optional[Question]:
        """Get current question"""
        session = self.sessions.get(session_id)
        if not session or session.status != InterviewStatus.IN_PROGRESS:
            return None
        
        if session.current_question_index >= len(session.questions):
            return None
        
        return session.questions[session.current_question_index]
    
    def get_question_for_display(self, question: Question) -> dict:
        """Get question for display (hide answer)"""
        return {
            "id": question.id,
            "type": question.type,
            "difficulty": question.difficulty,
            "title": question.title,
            "content": question.content,
            "options": [{"key": o.key, "content": o.content} for o in question.options] if question.options else None,
            "key_points": question.key_points  # Show evaluation points as hints
        }
    
    async def submit_answer(
        self, 
        session_id: str,
        question_id: str,
        selected_option: Optional[str],
        explanation: str
    ) -> tuple[AnswerEvaluation, bool, Optional[Question]]:
        """
        Submit answer
        
        Args:
            session_id: Session ID
            question_id: Question ID
            selected_option: Selected option
            explanation: Problem-solving approach
        
        Returns:
            (Evaluation result, Has next question, Next question)
        """
        session = self.sessions.get(session_id)
        if not session or session.status != InterviewStatus.IN_PROGRESS:
            raise ValueError("无效的会话或会话未在进行中")
        
        # Get current question
        current_question = self.get_current_question(session_id)
        if not current_question or current_question.id != question_id:
            raise ValueError("题目不匹配")
        
        # Evaluate answer
        evaluation = await self.ai_service.evaluate_answer(
            question=current_question,
            selected_option=selected_option,
            explanation=explanation
        )
        
        # Record answer
        answer_record = AnswerRecord(
            question_id=question_id,
            selected_option=selected_option,
            explanation=explanation,
            evaluation=evaluation,
            submitted_at=datetime.now()
        )
        session.answers.append(answer_record)
        
        # Move to next question
        session.current_question_index += 1
        
        # Check if there's next question
        has_next = session.current_question_index < len(session.questions)
        next_question = None
        
        if has_next:
            next_question = session.questions[session.current_question_index]
        else:
            # Interview completed
            session.status = InterviewStatus.COMPLETED
            session.completed_at = datetime.now()
        
        return evaluation, has_next, next_question
    
    async def get_feedback_text(
        self,
        session_id: str,
        question_id: str
    ) -> str:
        """Get interviewer feedback text"""
        session = self.sessions.get(session_id)
        if not session:
            return ""
        
        # Find corresponding answer record
        for answer in session.answers:
            if answer.question_id == question_id:
                question = next((q for q in session.questions if q.id == question_id), None)
                if question:
                    return await self.ai_service.generate_interview_feedback(
                        question=question,
                        evaluation=answer.evaluation
                    )
        
        return ""
    
    async def generate_report(self, session_id: str) -> Optional[InterviewReport]:
        """Generate interview report"""
        session = self.sessions.get(session_id)
        if not session or session.status != InterviewStatus.COMPLETED:
            return None
        
        # Calculate interview duration
        duration = 0
        if session.completed_at and session.created_at:
            duration = int((session.completed_at - session.created_at).total_seconds())
        
        return await self.ai_service.generate_report(
            session_id=session.id,
            candidate_name=session.candidate_name,
            position=session.position,
            questions=session.questions,
            answers=session.answers,
            duration=duration
        )
    
    def get_welcome_message(self, session: InterviewSession) -> str:
        """Generate welcome message"""
        name = session.candidate_name or "候选人"
        position = session.position or "该职位"
        
        return f"""你好，{name}！欢迎参加{position}的快速面试环节。

我是你的AI面试官。接下来，我将向你展示{session.question_count}道逻辑思维题，请认真阅读题目，选择你认为正确的答案，并简要说明你的解题思路。如果想不出来，也可以简单写写你的想法。

准备好了吗？让我们开始吧！"""
    
    def cancel_session(self, session_id: str) -> bool:
        """Cancel interview"""
        session = self.sessions.get(session_id)
        if session and session.status in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
            session.status = InterviewStatus.CANCELLED
            return True
        return False


# Singleton instance
_interview_service: Optional[InterviewService] = None


def get_interview_service() -> InterviewService:
    """Get interview service singleton"""
    global _interview_service
    if _interview_service is None:
        _interview_service = InterviewService()
    return _interview_service
