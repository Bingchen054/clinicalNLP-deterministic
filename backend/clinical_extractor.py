# backend/clinical_extractor.py

import re
from typing import Dict, Any, List, Optional


def _to_float(s: Optional[str]) -> Optional[float]:
    try:
        return float(s) if s is not None else None
    except Exception:
        return None


def _to_int(s: Optional[str]) -> Optional[int]:
    try:
        return int(float(s)) if s is not None else None
    except Exception:
        return None



#age Text Normalization 

def _normalize_text(notes: Optional[str]) -> str:
    if not notes:
        return ""
    txt = notes.replace("\r\n", " ").replace("\n", " ")
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()


def extract_clinical_data(notes: str) -> Dict[str, Any]:

    text = _normalize_text(notes or "")
    lower = text.lower()

    age = None
    m = re.search(r"\b(\d{2,3})[- ]?year[- ]?old\b", lower)
    if m:
        age = _to_int(m.group(1))

    gender = None
    if " female" in lower:
        gender = "female"
    elif " male" in lower:
        gender = "male"

    symptoms = []
    for term in ["cough", "shortness of breath", "fever", "chills", "chest pain"]:
        if term in lower:
            symptoms.append(term)

    duration = None
    m = re.search(r"x\s*(\d+)\s*week", lower)
    if m:
        duration = int(m.group(1)) * 7
    m = re.search(r"x\s*(\d+)\s*day", lower)
    if m:
        duration = int(m.group(1))

    vitals = {"bp": None, "hr": None, "rr": None}

    m = re.search(r"(\d{2,3}/\d{2,3})", lower)
    if m:
        vitals["bp"] = m.group(1)

    m = re.search(r"heart rate\s*(\d{2,3})", lower)
    if m:
        vitals["hr"] = _to_int(m.group(1))

    m = re.search(r"\b(?:respiratory rate|rr)\s*(\d{2})", lower)
    if m:
        vitals["rr"] = _to_int(m.group(1))

    # detect tachypnea from RR table
    rr_values = [int(x) for x in re.findall(r"\b(\d{2})\s*%", lower) if 10 < int(x) < 40]
    tachypnea = any(v >= 22 for v in rr_values)


    spo2_values = [int(x) for x in re.findall(r"(\d{2,3})\s*%", lower) if 30 <= int(x) <= 100]
    lowest_spo2 = min(spo2_values) if spo2_values else None
    hypoxemia = lowest_spo2 is not None and lowest_spo2 < 90

    oxygen_requirement = "l nasal cannula" in lower or "placed on" in lower or "o2 supplement" in lower

    # ===============================
    # LABS
    # ===============================
    labs: Dict[str, Optional[float]] = {}

    patterns = {
        "wbc": r"\bwbc.*?(\d{1,3}\.\d+|\d{1,3})",
        "bun": r"\bbun.*?(\d{1,3})",
        "creatinine": r"\bcreatinine.*?(\d{1,3}\.\d+)",
        "gfr": r"\bgfr.*?(\d{1,3})",
        "inr": r"\binr.*?(\d\.\d+)",
        "sodium": r"\bsodium.*?(\d{2,3})",
        "potassium": r"\bpotassium.*?(\d\.\d+)",
        "calcium": r"\bcalcium.*?(\d\.\d+)",
        "ast": r"\bast.*?(\d{1,3})",
        "alt": r"\balt.*?(\d{1,3})",
        "lactate": r"\blactic acid.*?(\d\.\d+)"
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, lower)
        if m:
            labs[key] = _to_float(m.group(1))

    # ===============================
    # IMAGING
    # ===============================
    imaging = []
    if "pneumonia" in lower:
        imaging.append("pneumonia")
    if "infiltrate" in lower:
        imaging.append("infiltrate")
    if "bilateral" in lower:
        imaging.append("bilateral")

    bilateral_pneumonia = "bilateral" in lower and "pneumonia" in lower

    # ===============================
    # PHYSICAL EXAM FLAGS
    # ===============================
    distress = "moderate distress" in lower or "chronically ill" in lower
    crackles = "crackles" in lower
    dnr_dni = "dnr" in lower or "dni" in lower
    assisted_living = "assisted living" in lower

    # ===============================
    # TREATMENT ESCALATION
    # ===============================
    iv_antibiotics = any(x in lower for x in ["vancomycin", "cefepime", "iv piggy", "iv push"])

    # ===============================
    # COMORBIDITIES
    # ===============================
    comorbidities = []
    for term in ["hypertension", "afib", "ckd", "aki", "dvt", "hypothyroidism"]:
        if term in lower:
            comorbidities.append(term)

    # ===============================
    # RETURN STRUCTURE
    # ===============================
    return {
        "raw_text": text,
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "symptom_duration_days": duration,
        "vitals": vitals,
        "tachypnea": tachypnea,
        "spo2_values": spo2_values,
        "lowest_spo2": lowest_spo2,
        "hypoxemia": hypoxemia,
        "oxygenRequirement": oxygen_requirement,
        "labs": labs,
        "imagingFindings": imaging,
        "bilateral_pneumonia": bilateral_pneumonia,
        "distress": distress,
        "crackles": crackles,
        "dnr_dni": dnr_dni,
        "assisted_living": assisted_living,
        "iv_antibiotics": iv_antibiotics,
        "comorbidities": comorbidities,
    }