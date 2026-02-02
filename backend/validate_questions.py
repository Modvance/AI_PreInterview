"""
Validate questions.json format and content
"""
import json
from pathlib import Path
from app.schemas.interview import Question, QuestionType, DifficultyLevel

def validate_questions():
    """Validate all questions in questions.json"""
    data_path = Path(__file__).parent / "data" / "questions.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    print(f"Total questions: {len(questions)}")
    
    # Statistics
    types = {}
    difficulties = {}
    errors = []
    
    for q_data in questions:
        # Count types and difficulties
        q_type = q_data.get("type")
        difficulty = q_data.get("difficulty")
        types[q_type] = types.get(q_type, 0) + 1
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        # Validate with Pydantic
        try:
            question = Question(**q_data)
            # Check required fields
            if not question.options or len(question.options) < 2:
                errors.append(f"{q_data['id']}: Need at least 2 options")
            if question.correct_answer not in [opt.key for opt in (question.options or [])]:
                errors.append(f"{q_data['id']}: correct_answer '{question.correct_answer}' not in options")
        except Exception as e:
            errors.append(f"{q_data['id']}: {str(e)}")
    
    print(f"\nType distribution:")
    for q_type, count in sorted(types.items()):
        print(f"  {q_type}: {count}")
    
    print(f"\nDifficulty distribution:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")
    
    if errors:
        print(f"\nErrors found ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n[SUCCESS] All questions validated successfully!")
        return True

if __name__ == "__main__":
    validate_questions()
