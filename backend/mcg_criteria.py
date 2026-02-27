# backend/mcg_criteria.py

MCG_CRITERIA = [

    {
        "order": 1,
        "id": "MCG-R1",
        "text": "Hypoxemia (SpO2 < 90%) or need for supplemental oxygen",
        "category": "Respiratory",
        "keywords": [
            "hypoxemia", "spo2", "o2 sat", "oxygen saturation",
            "supplemental oxygen", "nasal cannula", "desaturat"
        ],
        "action": "Document lowest SpO2 value and oxygen support requirement."
    },

    {
        "order": 2,
        "id": "MCG-H1",
        "text": "Hemodynamic instability (systolic BP < 90 or need for vasopressors)",
        "category": "Hemodynamic",
        "keywords": [
            "sbp < 90", "hypotension", "vasopressor"
        ],
        "action": "Document persistent hypotension or vasopressor requirement."
    },

    {
        "order": 3,
        "id": "MCG-N1",
        "text": "Altered mental status that is severe or persistent",
        "category": "Neurologic",
        "keywords": [
            "altered mental", "confusion", "lethargy",
            "somnolent", "disoriented", "coma"
        ],
        "action": "Document severity and persistence of altered mental status."
    },

    {
        "order": 4,
        "id": "MCG-D1",
        "text": "Dehydration that is severe or persistent",
        "category": "Other",
        "keywords": [
            "dehydration", "orthostasis", "dry mucosa"
        ],
        "action": "Document severity of dehydration and need for IV fluids."
    },

    {
        "order": 5,
        "id": "MCG-R2",
        "text": "Ventilatory assistance needed (eg mechanical ventilation, noninvasive ventilation)",
        "category": "Respiratory",
        "keywords": [
            "intubation", "mechanical ventilation",
            "bipap", "cpap", "ventilator"
        ],
        "action": "Document requirement for mechanical or noninvasive ventilatory support."
    },

    {
        "order": 6,
        "id": "MCG-B1",
        "text": "Bacteremia (if blood cultures performed)",
        "category": "Laboratory",
        "keywords": [
            "positive blood culture", "bacteremia"
        ],
        "action": "Document positive blood culture if obtained."
    },

    {
        "order": 7,
        "id": "MCG-R3",
        "text": "Moderate-risk-category or high-risk-category patient (PSI IV/V or CURB-65 ≥ 3)",
        "category": "RiskScore",
        "keywords": [
            "psi iv", "psi v", "curb-65", "curb 65"
        ],
        "action": "Document PSI class IV/V or CURB-65 score ≥ 3."
    },

    {
        "order": 8,
        "id": "MCG-R4",
        "text": "Respiratory finding (eg tachypnea) that persists despite observation care",
        "category": "Respiratory",
        "keywords": [
            "tachypnea", "respiratory rate", "respiratory distress"
        ],
        "action": "Document respiratory findings persisting despite observation."
    },

    {
        "order": 9,
        "id": "MCG-C1",
        "text": "Complicated pleural effusions (eg empyema, loculated)",
        "category": "Imaging",
        "keywords": [
            "pleural effusion", "empyema", "loculated"
        ],
        "action": "Document complicated pleural effusion findings."
    },

    {
        "order": 10,
        "id": "MCG-R6",
        "text": "Presence of risk factor for poor outcome (eg gross hemoptysis, cavitary infiltrate, neuromuscular weakness, cystic fibrosis)",
        "category": "RiskFactor",
        "keywords": [
            "hemoptysis", "cavitary infiltrate",
            "neuromuscular weakness", "cystic fibrosis"
        ],
        "action": "Document risk factors associated with poor outcome."
    }

]

# Stable mapping by id
MCG_CRITERIA_MAP = {c["id"]: c for c in MCG_CRITERIA}

# Optional: canonical ordered list helper
MCG_CRITERIA_SORTED = sorted(MCG_CRITERIA, key=lambda x: x["order"])