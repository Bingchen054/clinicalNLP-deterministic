from dataclasses import dataclass
from typing import List, Dict, Optional, TypedDict

CriterionCategory = str  # "Respiratory"|"Imaging"|"Laboratory"|"Outpatient"|"Comorbidity"|"General"

@dataclass
class ExtractedCriterion:
    id: str
    text: str
    category: CriterionCategory

@dataclass
class ClinicalData:
    age: Optional[int] = None
    symptoms: List[str] = None
    vitals: Dict[str, float] = None
    labs: Dict[str, float] = None
    imagingFindings: List[str] = None
    oxygenRequirement: bool = False
    hypoxemia: bool = False
    comorbidities: List[str] = None
    outpatientFailure: bool = False

@dataclass
class EvaluatedCriterion:
    criterionId: str
    criterionText: str
    category: CriterionCategory
    status: str  # "Met" | "Partially Met" | "Missing"
    evidenceFound: str
    suggestedLanguage: str
    scoreContribution: int

@dataclass
class AdmissionDecision:
    totalScore: int
    maxPossibleScore: int
    percentage: int
    admissionRecommended: bool

@dataclass
class AlignmentResult:
    extractedCriteria: List[ExtractedCriterion]
    revisedNotes: Dict[str, str]
    missingCriteria: List[EvaluatedCriterion]
    overallScore: int
    admissionRecommended: bool