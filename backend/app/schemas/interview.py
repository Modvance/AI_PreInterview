"""
Interview related data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class QuestionType(str, Enum):
    """Question type enumeration"""
    LOGIC = "logic"           # Logical reasoning
    MATH = "math"             # Mathematical calculation
    ALGORITHM = "algorithm"   # Algorithm thinking
    SCENARIO = "scenario"     # Scenario analysis


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewStatus(str, Enum):
    """Interview status enumeration"""
    PENDING = "pending"          # Waiting to start
    IN_PROGRESS = "in_progress"  # In progress
    COMPLETED = "completed"      # Completed
    CANCELLED = "cancelled"      # Cancelled


# ============ Question Models ============

class QuestionOption(BaseModel):
    """Question option model"""
    key: str              # Option key: A, B, C, D
    content: str          # Option content


class Question(BaseModel):
    """Interview question model"""
    id: str
    type: QuestionType
    difficulty: DifficultyLevel
    title: str                          # Question title
    content: str                        # Question content
    options: Optional[List[QuestionOption]] = None  # Options (for multiple choice)
    correct_answer: str                 # Correct answer
    explanation: str                    # Answer explanation
    key_points: List[str]               # Key evaluation points
    tags: List[str] = []                # Tags


class QuestionDisplay(BaseModel):
    """Question display model (without answer)"""
    id: str
    type: QuestionType
    difficulty: DifficultyLevel
    title: str                          # Question title
    content: str                        # Question content
    options: Optional[List[QuestionOption]] = None  # Options (for multiple choice)
    key_points: List[str]               # Key evaluation points


# ============ Interview Session Models ============

class CreateInterviewRequest(BaseModel):
    """Create interview request model"""
    candidate_name: Optional[str] = None
    position: Optional[str] = None      # Applied position
    resume_data: Optional[dict] = None  # Resume parsed data (reserved)
    jd_data: Optional[dict] = None      # JD parsed data (reserved)
    question_count: int = Field(default=3, ge=2, le=5)  # Number of questions


class InterviewSession(BaseModel):
    """Interview session model"""
    id: str
    candidate_name: Optional[str] = None
    position: Optional[str] = None
    status: InterviewStatus = InterviewStatus.PENDING
    question_count: int = 3
    current_question_index: int = 0
    questions: List[Question] = []
    answers: List["AnswerRecord"] = []
    created_at: datetime
    completed_at: Optional[datetime] = None


class InterviewSessionResponse(BaseModel):
    """Interview session response model (without answers)"""
    id: str
    candidate_name: Optional[str] = None
    position: Optional[str] = None
    status: InterviewStatus
    question_count: int
    current_question_index: int
    welcome_message: str = ""
    created_at: datetime


# ============ Answer Models ============

class SubmitAnswerRequest(BaseModel):
    """Submit answer request model"""
    question_id: str
    selected_option: Optional[str] = None  # Selected option
    explanation: str  # Verbal explanation of solution


class AnswerEvaluation(BaseModel):
    """Answer evaluation result model"""
    is_correct: bool                    # Whether answer is correct
    score: int = Field(ge=0, le=100)    # Score 0-100
    feedback: str                       # AI feedback
    hints: List[str] = []               # Hints (if needed)
    key_points_hit: List[str] = []      # Key points mentioned
    key_points_missed: List[str] = []   # Key points missed


class AnswerRecord(BaseModel):
    """Answer record model"""
    question_id: str
    selected_option: Optional[str] = None
    explanation: str
    evaluation: AnswerEvaluation
    submitted_at: datetime


class SubmitAnswerResponse(BaseModel):
    """Submit answer response model"""
    evaluation: AnswerEvaluation
    has_next_question: bool
    next_question: Optional[QuestionDisplay] = None
    audio_feedback_url: Optional[str] = None  # TTS generated feedback audio (reserved)


# ============ Report Models ============

class QuestionReport(BaseModel):
    """Single question report model"""
    question_title: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    is_correct: bool
    score: int
    candidate_answer: str
    correct_answer: str
    evaluation_summary: str


class InterviewReport(BaseModel):
    """Interview report model"""
    session_id: str
    candidate_name: Optional[str] = None
    position: Optional[str] = None
    
    # Overall evaluation
    total_score: int = Field(ge=0, le=100)
    total_questions: int
    correct_count: int
    
    # Ability evaluation
    logic_ability: int = Field(ge=0, le=100)      # Logical thinking ability
    expression_ability: int = Field(ge=0, le=100) # Expression ability
    problem_solving: int = Field(ge=0, le=100)    # Problem solving ability
    
    # Detailed content
    question_reports: List[QuestionReport]
    strengths: List[str]        # Strengths
    weaknesses: List[str]       # Areas for improvement
    overall_comment: str        # Overall comment
    recommendation: str         # Recommendation
    
    # Time information
    interview_duration: int     # Interview duration (seconds)
    created_at: datetime


# ============ Common Response Models ============

class MessageResponse(BaseModel):
    """Common message response model"""
    success: bool
    message: str
    data: Optional[dict] = None
