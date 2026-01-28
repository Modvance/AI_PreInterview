"""
Question Service - Manages interview questions
"""
import json
import random
from pathlib import Path
from typing import List, Optional
from ..schemas.interview import Question, QuestionType, DifficultyLevel


class QuestionService:
    """Question bank service"""
    
    def __init__(self):
        self.questions: List[Question] = []
        self._load_questions()
    
    def _load_questions(self):
        """Load questions from JSON file"""
        data_path = Path(__file__).parent.parent.parent / "data" / "questions.json"
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.questions = [Question(**q) for q in data.get("questions", [])]
        except FileNotFoundError:
            print(f"Warning: Question file not found at {data_path}")
            self.questions = []
        except Exception as e:
            print(f"Error loading questions: {e}")
            self.questions = []
    
    def get_all_questions(self) -> List[Question]:
        """Get all questions"""
        return self.questions
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None
    
    def get_questions_by_type(self, q_type: QuestionType) -> List[Question]:
        """Get questions by type"""
        return [q for q in self.questions if q.type == q_type]
    
    def get_questions_by_difficulty(self, difficulty: DifficultyLevel) -> List[Question]:
        """Get questions by difficulty"""
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def select_questions_for_interview(
        self,
        count: int = 3,
        difficulty_preference: Optional[DifficultyLevel] = None,
        type_preference: Optional[QuestionType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Question]:
        """
        Select questions for interview
        
        Args:
            count: Number of questions
            difficulty_preference: Difficulty preference
            type_preference: Type preference
            tags: Tag filter
        
        Returns:
            List of selected questions
        """
        candidates = self.questions.copy()
        
        # Filter by preferences
        if difficulty_preference:
            candidates = [q for q in candidates if q.difficulty == difficulty_preference]
        
        if type_preference:
            candidates = [q for q in candidates if q.type == type_preference]
        
        if tags:
            candidates = [
                q for q in candidates 
                if any(tag in q.tags for tag in tags)
            ]
        
        # Fallback to all questions if filtered results are insufficient
        if len(candidates) < count:
            candidates = self.questions.copy()
        
        # Random selection with type diversity
        if len(candidates) <= count:
            return candidates
        
        # Try to select different types of questions
        selected = []
        types_used = set()
        
        # First select one of each type
        random.shuffle(candidates)
        for q in candidates:
            if q.type not in types_used and len(selected) < count:
                selected.append(q)
                types_used.add(q.type)
        
        # Fill remaining slots randomly
        remaining = [q for q in candidates if q not in selected]
        random.shuffle(remaining)
        while len(selected) < count and remaining:
            selected.append(remaining.pop())
        
        return selected
    
    def auto_select_questions(
        self,
        resume_data: Optional[dict] = None,
        jd_data: Optional[dict] = None
    ) -> List[Question]:
        """
        Automatically select questions based on difficulty
        - First randomly select 3 questions with type diversity
        - Check if selected questions contain easy questions
        - If contains easy questions: keep 3 questions
        - If all selected are medium/hard: reduce to 2 questions
        
        Args:
            resume_data: Parsed resume data (reserved)
            jd_data: Parsed JD data (reserved)
        
        Returns:
            List of selected questions (2 or 3)
        """
        # Get all available questions
        candidates = self.questions.copy()
        
        if not candidates:
            return []
        
        # Step 1: First select 3 questions with type diversity
        selected = []
        types_used = set()
        
        # Shuffle for randomness
        random.shuffle(candidates)
        
        # Try to select diverse types first
        for q in candidates:
            if len(selected) >= 3:
                break
            if q.type not in types_used:
                selected.append(q)
                types_used.add(q.type)
        
        # If not enough diverse types, fill randomly
        remaining = [q for q in candidates if q not in selected]
        random.shuffle(remaining)
        while len(selected) < 3 and remaining:
            selected.append(remaining.pop())
        
        # Step 2: Check if selected questions contain easy questions
        has_easy = any(q.difficulty == DifficultyLevel.EASY for q in selected)
        
        # Step 3: Determine final count based on difficulty
        if has_easy:
            # Contains easy questions: keep 3 questions
            return selected
        else:
            # All are medium/hard: reduce to 2 questions
            # Keep first 2 questions (already shuffled, so random)
            return selected[:2]
    
    def select_questions_with_resume_jd(
        self,
        count: int = 3,
        resume_data: Optional[dict] = None,
        jd_data: Optional[dict] = None
    ) -> List[Question]:
        """
        Select targeted questions based on resume and JD data (reserved interface)
        
        Args:
            count: Number of questions
            resume_data: Parsed resume data
            jd_data: Parsed JD data
        
        Returns:
            List of selected questions
        """
        # TODO: Analyze resume and JD data to select targeted questions
        # Currently using default selection logic
        tags = []
        difficulty = None
        
        if resume_data:
            # Extract relevant info from resume
            skills = resume_data.get("skills", [])
            experience_years = resume_data.get("experience_years", 0)
            
            # Adjust difficulty based on experience
            if experience_years >= 5:
                difficulty = DifficultyLevel.HARD
            elif experience_years >= 2:
                difficulty = DifficultyLevel.MEDIUM
            else:
                difficulty = DifficultyLevel.EASY
            
            # Add tags based on skills
            if "algorithm" in skills or "data structure" in skills:
                tags.append("Algorithm")
            if "system design" in skills:
                tags.append("System Design")
        
        if jd_data:
            # Extract relevant info from JD
            requirements = jd_data.get("requirements", [])
            # Can add more filtering logic based on JD requirements
        
        return self.select_questions_for_interview(
            count=count,
            difficulty_preference=difficulty,
            tags=tags if tags else None
        )


# Singleton instance
_question_service: Optional[QuestionService] = None


def get_question_service() -> QuestionService:
    """Get question service singleton"""
    global _question_service
    if _question_service is None:
        _question_service = QuestionService()
    return _question_service
