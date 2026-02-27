from typing import List, Dict

rule_matrix = [
    {"category": "Respiratory", "requiredSignals": ["hypoxemia", "oxygenRequirement"], "weight": 3},
    {"category": "Imaging", "requiredSignals": ["imagingFindings"], "weight": 2},
    {"category": "Laboratory", "requiredSignals": ["labs"], "weight": 2},
    {"category": "Outpatient", "requiredSignals": ["outpatientFailure"], "weight": 2},
    {"category": "Comorbidity", "requiredSignals": ["comorbidities"], "weight": 1},
]