# backend/admission_scorer.py
from typing import List, Dict, Any, TypedDict

class EvaluatedCriterionDict(TypedDict, total=False):
    scoreContribution: int
    status: str

def compute_admission_decision(evaluated: List[EvaluatedCriterionDict]) -> Dict[str, Any]:
    total_score = sum(int(c.get("scoreContribution", 0)) for c in evaluated)
    max_possible_score = len(evaluated) * 5
    percentage = round((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
    admission_recommended = any(c.get("status") == "Met" for c in evaluated)

    return {
        "totalScore": total_score,
        "maxPossibleScore": max_possible_score,
        "percentage": percentage,
        "admissionRecommended": admission_recommended,
    }