# backend/justification_builder.py

from typing import Dict, List, Any, Union
from alignment_types import ClinicalData, EvaluatedCriterion


def _get(d: Union[dict, object], name: str, default=None):
    if d is None:
        return default
    if isinstance(d, dict):
        return d.get(name, default)
    return getattr(d, name, default)


def _format_list(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def build_justification(
    clinical_data: ClinicalData,
    evaluated: List[EvaluatedCriterion],
    decision: Dict[str, Any]
) -> Dict[str, str]:

    age = _get(clinical_data, "age")
    gender = _get(clinical_data, "gender")
    symptoms = _get(clinical_data, "symptoms") or []
    duration = _get(clinical_data, "symptom_duration_days")
    vitals = _get(clinical_data, "vitals") or {}
    labs = _get(clinical_data, "labs") or {}
    imaging = _get(clinical_data, "imagingFindings") or []
    comorbs = _get(clinical_data, "comorbidities") or []

    hypox = _get(clinical_data, "hypoxemia", False)
    lowest_spo2 = _get(clinical_data, "lowest_spo2")
    oxyreq = _get(clinical_data, "oxygenRequirement", False)
    tachypnea = _get(clinical_data, "tachypnea", False)
    distress = _get(clinical_data, "distress", False)
    crackles = _get(clinical_data, "crackles", False)
    bilateral_pna = _get(clinical_data, "bilateral_pneumonia", False)

    dnr_dni = _get(clinical_data, "dnr_dni", False)
    assisted_living = _get(clinical_data, "assisted_living", False)
    iv_abx = _get(clinical_data, "iv_antibiotics", False)

    total_score = decision.get("totalScore") if isinstance(decision, dict) else None

    # =====================================================
    # CLINICAL SUMMARY
    # =====================================================

    summary_parts: List[str] = []

    # Demographics
    if age and gender:
        summary_parts.append(
            f"The patient is an {age}-year-old {gender} presenting with acute respiratory illness."
        )
    elif age:
        summary_parts.append(
            f"The patient is an {age}-year-old individual presenting with acute respiratory illness."
        )
    else:
        summary_parts.append(
            "The patient presented with acute respiratory illness."
        )

    # Symptoms
    if symptoms:
        symptom_text = _format_list(symptoms)
        if duration:
            summary_parts.append(
                f"Symptoms including {symptom_text} had been present for approximately {duration} days prior to admission and progressively worsened."
            )
        else:
            summary_parts.append(
                f"Reported symptoms included {symptom_text} with clinical progression."
            )

    # Respiratory severity
    if hypox:
        summary_parts.append(
            f"Initial oxygen saturation was documented as low as {lowest_spo2}%, consistent with hypoxemia."
        )

    if tachypnea:
        summary_parts.append(
            "Objective tachypnea was noted, reflecting increased work of breathing."
        )

    if crackles:
        summary_parts.append(
            "Physical examination revealed bilateral crackles consistent with lower respiratory tract involvement."
        )

    if distress:
        summary_parts.append(
            "The patient appeared clinically ill with signs of respiratory distress."
        )

    if oxyreq:
        summary_parts.append(
            "Supplemental oxygen therapy was required to maintain adequate oxygenation."
        )

    # Imaging
    if imaging:
        summary_parts.append(
            f"Chest imaging demonstrated findings consistent with {_format_list(imaging)}."
        )

    if bilateral_pna:
        summary_parts.append(
            "Bilateral pulmonary involvement further increases severity of illness."
        )

    # Laboratory abnormalities
    lab_details = []
    if labs.get("wbc") is not None:
        lab_details.append(f"leukocytosis (WBC {labs.get('wbc')})")
    if labs.get("bun") is not None and labs.get("bun") > 40:
        lab_details.append(f"elevated BUN ({labs.get('bun')})")
    if labs.get("creatinine") is not None:
        lab_details.append(f"creatinine {labs.get('creatinine')}")
    if labs.get("gfr") is not None and labs.get("gfr") < 60:
        lab_details.append(f"reduced GFR ({labs.get('gfr')})")
    if labs.get("inr") is not None and labs.get("inr") > 2:
        lab_details.append(f"elevated INR ({labs.get('inr')})")

    if lab_details:
        summary_parts.append(
            "Laboratory evaluation revealed " + _format_list(lab_details) + ", indicating multi-system involvement."
        )

    clinical_summary = " ".join(summary_parts).strip()

    # =====================================================
    # MEDICAL NECESSITY
    # =====================================================

    med_reasons: List[str] = []

    if hypox:
        med_reasons.append(
            "Documented hypoxemia represents objective respiratory compromise requiring inpatient monitoring."
        )

    if bilateral_pna:
        med_reasons.append(
            "Bilateral pneumonia increases risk of rapid clinical deterioration."
        )

    if labs.get("bun") and labs.get("bun") > 40:
        med_reasons.append(
            "Elevated BUN suggests renal dysfunction contributing to systemic illness."
        )

    if labs.get("gfr") and labs.get("gfr") < 60:
        med_reasons.append(
            "Reduced glomerular filtration rate indicates impaired renal reserve."
        )

    if labs.get("inr") and labs.get("inr") > 2:
        med_reasons.append(
            "Supratherapeutic INR increases bleeding risk and complicates management."
        )

    if iv_abx:
        med_reasons.append(
            "Initiation of broad-spectrum intravenous antibiotics reflects escalation of care."
        )

    if not med_reasons:
        medical_necessity = "No major inpatient-level triggers identified."
    else:
        medical_necessity = " ".join(med_reasons)

    # =====================================================
    # RISK STRATIFICATION
    # =====================================================

    risk_parts: List[str] = []

    if comorbs:
        risk_parts.append(
            f"Comorbid conditions including {_format_list(comorbs)} increase baseline vulnerability."
        )

    if assisted_living:
        risk_parts.append(
            "Residence in an assisted living facility suggests baseline functional dependency."
        )

    if dnr_dni:
        risk_parts.append(
            "Documented DNR/DNI status reflects advanced directive considerations in the setting of acute illness."
        )

    risk_stratification = " ".join(risk_parts).strip()

    # =====================================================
    # CONCLUSION
    # =====================================================

    conclusion_parts: List[str] = []

    if total_score is not None:
        conclusion_parts.append(
            f"Overall admission severity score is estimated at {total_score}%."
        )

    conclusion_parts.append(
        "Given the combination of respiratory compromise, radiographic pneumonia, laboratory abnormalities, and comorbid risk factors, inpatient-level care is medically appropriate."
    )

    conclusion = " ".join(conclusion_parts)

    return {
        "clinicalSummary": clinical_summary,
        "medicalNecessityJustification": medical_necessity,
        "riskStratification": risk_stratification,
        "conclusion": conclusion,
    }