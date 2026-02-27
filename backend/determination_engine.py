"""
determination_engine.py

Deterministic MCG Admission Determination Engine
Enhanced Severity + Multi-System + Escalation Model
"""

from typing import Dict, Any, List


def evaluate_mcg_pneumonia(features: Dict[str, Any]) -> Dict[str, Any]:

    triggers: List[str] = []
    checklist: List[Dict[str, Any]] = []

    age = features.get("age")
    lowest_spo2 = features.get("lowest_spo2")
    hypoxemia = features.get("hypoxemia")
    oxygen_required = features.get("oxygenRequirement")
    tachypnea = features.get("tachypnea")
    bilateral_pna = features.get("bilateral_pneumonia")

    labs = features.get("labs") or {}
    imaging = features.get("imagingFindings") or []
    comorbs = features.get("comorbidities") or []

    iv_abx = features.get("iv_antibiotics")
    dnr_dni = features.get("dnr_dni")
    assisted_living = features.get("assisted_living")

    # =====================================================
    # SEVERITY SCORE
    # =====================================================

    severity_score = 0

    # Hypoxemia
    if hypoxemia:
        triggers.append("Hypoxemia")
        severity_score += 40

    # Oxygen requirement
    if oxygen_required:
        triggers.append("Oxygen requirement")
        severity_score += 25

    # Tachypnea
    if tachypnea:
        triggers.append("Tachypnea")
        severity_score += 10

    # Pneumonia imaging
    if any(x in imaging for x in ["pneumonia", "infiltrate", "consolidation"]):
        triggers.append("Radiographic pneumonia")
        severity_score += 15

    # Bilateral involvement
    if bilateral_pna:
        triggers.append("Bilateral pneumonia")
        severity_score += 10

    # Leukocytosis
    if labs.get("wbc") and labs["wbc"] >= 12:
        triggers.append("Leukocytosis")
        severity_score += 10

    # Renal dysfunction
    if labs.get("bun") and labs["bun"] > 40:
        triggers.append("Elevated BUN")
        severity_score += 5

    if labs.get("gfr") and labs["gfr"] < 60:
        triggers.append("Reduced GFR")
        severity_score += 5

    if labs.get("creatinine") and labs["creatinine"] > 1.5:
        triggers.append("Elevated creatinine")
        severity_score += 5

    # Coagulation risk
    if labs.get("inr") and labs["inr"] > 2:
        triggers.append("Elevated INR")
        severity_score += 5

    # IV antibiotic escalation
    if iv_abx:
        triggers.append("IV antibiotic therapy")
        severity_score += 15

    # =====================================================
    # RISK SCORE
    # =====================================================

    risk_score = 0
    risk_factors = []

    if age and age >= 75:
        risk_score += 5
        risk_factors.append("Advanced age ≥ 75")
    elif age and age >= 65:
        risk_score += 3
        risk_factors.append("Age ≥ 65")

    if comorbs:
        risk_score += 5
        risk_factors.append("Multiple comorbidities")

    if assisted_living:
        risk_score += 3
        risk_factors.append("Assisted living residency")

    if dnr_dni:
        risk_score += 3
        risk_factors.append("DNR/DNI status")

    # =====================================================
    # UNSAFE DISCHARGE LOGIC
    # =====================================================

    unsafe_discharge = False
    unsafe_reasons = []

    if hypoxemia:
        unsafe_discharge = True
        unsafe_reasons.append("Hypoxemia")

    if oxygen_required and lowest_spo2 and lowest_spo2 < 92:
        unsafe_discharge = True
        unsafe_reasons.append("Oxygen dependency")

    if bilateral_pna and tachypnea:
        unsafe_discharge = True
        unsafe_reasons.append("High respiratory burden")

    # =====================================================
    # FINAL SCORING
    # =====================================================

    total_score = min(severity_score + risk_score, 100)

    if unsafe_discharge:
        level = "Inpatient - Unsafe for discharge"
    elif total_score >= 70:
        level = "Inpatient - Strong MCG support"
    elif total_score >= 50:
        level = "Inpatient - MCG supported"
    elif total_score >= 35:
        level = "Inpatient - Consider admission"
    else:
        level = "Observation / outpatient"

    return {
        "triggers": triggers,
        "severityScore": severity_score,
        "riskScore": risk_score,
        "totalScore": total_score,
        "riskFactors": risk_factors,
        "unsafeDischarge": unsafe_discharge,
        "unsafeReasons": unsafe_reasons,
        "level": level
    }