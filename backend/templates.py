

from typing import Dict, Any, List


def _get(d: Dict[str, Any], key: str, default=None):
    if not d:
        return default
    return d.get(key, default)


# =====================================================
# PRIMARY TEMPLATE – NARRATIVE STYLE
# =====================================================
def generate_revised_hpi(original_note: str,
                         features: Dict[str, Any],
                         results: Dict[str, Any]) -> str:
    """
    Deterministic reconstruction of HPI aligned to MCG admission criteria.
    Uses keys produced by clinical_extractor/determination_engine:
      - features: raw_text, age, vitals {lowest_spo2, spo2_values}, oxygenRequirement (bool),
                  oxygen_flow_lpm, imagingFindings (list), labs (dict), outpatientFailure (bool),
                  comorbidities (list), iv_abx (bool)
      - results: triggers (list), severityScore (int), riskFactors (list), level (str), percentage (optional)
    """

    paragraphs: List[str] = []

    # 1) Intro / demographics
    age = _get(features, "age")
    if age:
        paragraphs.append(f"The patient is an {age}-year-old individual who presented to the emergency department with progressive respiratory symptoms.")
    else:
        paragraphs.append("The patient presented to the emergency department with progressive respiratory symptoms.")

    # 2) Symptom course / outpatient therapy
    # prefer evidence in raw_text for verbatim quoting if needed
    outpatient_fail = bool(_get(features, "outpatientFailure", False))
    raw = _get(features, "raw_text", "") or ""
    if outpatient_fail:
        # if text contains 'failed' phrase, echo it
        paragraphs.append("Per documentation, symptoms worsened despite recent outpatient therapy.")
    else:
        # keep a generic symptom course if original note contains some history lines
        # attempt to pull a short HPI line from original raw text (first 200 chars)
        snippet = (raw.splitlines()[0].strip() if raw else "")[:200]
        if snippet:
            paragraphs.append(snippet)
        else:
            paragraphs.append("Symptoms were reported to be progressive over several days and associated with shortness of breath.")

    # 3) ED findings: SpO2 / oxygen support / vitals
    vitals = _get(features, "vitals", {}) or {}
    lowest_spo2 = vitals.get("lowest_spo2") if isinstance(vitals, dict) else None
    oxygen_req = bool(_get(features, "oxygenRequirement", False))
    oxygen_flow = _get(features, "oxygen_flow_lpm", None)

    ed_lines = []
    if lowest_spo2 is not None:
        ed_lines.append(f"Emergency department monitoring demonstrated oxygen desaturation to {lowest_spo2}%.")
    elif oxygen_req:
        ed_lines.append("Emergency department monitoring documented an oxygen requirement.")

    if oxygen_req or oxygen_flow:
        if oxygen_flow:
            ed_lines.append(f"Patient required supplemental oxygen via {oxygen_flow} L/min nasal cannula to maintain saturations.")
        else:
            ed_lines.append("Patient required supplemental oxygen to maintain adequate saturations.")

    # 4) Imaging
    imaging = _get(features, "imagingFindings", []) or []
    if imaging:
        # join imaging findings
        ed_lines.append("Chest imaging demonstrated findings consistent with pneumonia.")
    # 5) Labs
    labs = _get(features, "labs", {}) or {}
    wbc = labs.get("wbc")
    if wbc is not None:
        try:
            ed_lines.append(f"Laboratory evaluation revealed WBC {float(wbc)}.")
        except Exception:
            ed_lines.append(f"Laboratory evaluation notable for WBC: {wbc}.")

    if _get(features, "iv_abx", False):
        ed_lines.append("Broad-spectrum intravenous antibiotics were initiated in the emergency department.")

    if ed_lines:
        paragraphs.append(" ".join(ed_lines))

    # 6) Comorbidities / risk factors
    comorbs = _get(features, "comorbidities", []) or []
    if comorbs:
        paragraphs.append(f"Relevant comorbidities include: {', '.join(comorbs)}.")

    # 7) Determination summary (use results from determination_engine)
    triggers = results.get("triggers", []) or []
    severity_score = results.get("severityScore", results.get("severityScore", None))
    level = results.get("level", results.get("level", "Undetermined"))
    risk_factors = results.get("riskFactors", []) or []
    pct = results.get("percentage", None) or results.get("severityScore", None)  # fallback

    summary_components: List[str] = []
    # map triggers to readable phrases if present
    if "Hypoxemia" in triggers or (lowest_spo2 is not None and lowest_spo2 < 90):
        summary_components.append("documented hypoxemia requiring supplemental oxygen")
    if imaging:
        summary_components.append("radiographic evidence of pneumonia")
    if outpatient_fail:
        summary_components.append("failure of outpatient therapy")
    if wbc is not None and float(wbc) >= 10:
        summary_components.append("laboratory evidence suggestive of infection")

    if summary_components:
        paragraphs.append("In summary, this patient demonstrates " + ", ".join(summary_components) + ", supporting inpatient-level management.")

    # include explicit risk factors & severity
    if risk_factors:
        paragraphs.append("Risk factors for severe disease include: " + ", ".join(risk_factors) + ".")
    if severity_score is not None:
        paragraphs.append(f"Severity score: {severity_score}.")

    # admission determination statement
    if pct is not None and isinstance(pct, (int, float)):
        pct_text = f"{pct}%" if isinstance(pct, (int, float)) and pct <= 100 else str(pct)
        paragraphs.append(f"Admission determination: {level} (score {pct_text}).")
    else:
        paragraphs.append(f"Admission determination: {level}.")

    # 8) Append short original HPI for auditability
    if raw:
        paragraphs.append("--- Original Documentation excerpt ---")
        excerpt = raw.strip()
        if len(excerpt) > 800:
            excerpt = excerpt[:800].rsplit(".", 1)[0] + "..."
        paragraphs.append(excerpt)

    revised_hpi = "\n\n".join(paragraphs)

    return f"""
Revised HPI

{revised_hpi}

--- Original Documentation ---
{original_note}
"""


# =====================================================
# COMPACT SUMMARY VERSION (Optional for UI)
# =====================================================
def generate_compact_summary(features: Dict[str, Any],
                             results: Dict[str, Any]) -> str:
    triggers = results.get("triggers", []) or []
    severity = results.get("severityScore", "N/A")
    level = results.get("level", "Undetermined")
    return f"""
MCG Admission Summary

Triggers Met: {", ".join(triggers) if triggers else "None"}
Severity Score: {severity}
Determination: {level}
"""


# =====================================================
# SAFE FALLBACK TEMPLATE
# =====================================================
def generate_safe_output(original_note: str) -> str:
    return f"""
Clinical Documentation Summary

No structured admission triggers identified.

--- Original Documentation ---
{original_note}
"""