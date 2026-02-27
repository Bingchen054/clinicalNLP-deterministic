"""
note_extractor.py

Deterministic clinical feature extractor for physician notes.
"""

import re
from typing import Optional, Dict, Any


# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("SpO 2", "SpO2")
    text = text.replace("O 2", "O2")
    return text.strip()


# =====================================================
# AGE
# =====================================================

def extract_age(text: str) -> Optional[int]:
    patterns = [
        r"(\d{2,3})[- ]?year[- ]?old",
        r"\bAge[:\s]+(\d{1,3})\b",
        r"\bage\s+(\d{1,3})\b"
    ]

    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except:
                continue

    return None


# =====================================================
# OXYGEN SATURATION (IMPROVED)
# =====================================================

def extract_spo2(text: str) -> Optional[int]:
    patterns = [
        r"(?:SpO2|SPO2|O2 sat|oxygen saturation)[^\d]{0,20}(\d{2,3})\s*%?",
        r"\boxygen saturation.*?(\d{2,3})\s*%?",
        r"\bdesaturat(?:ed|ion).*?(\d{2,3})\s*%?",
        r"\bsaturation.*?(\d{2,3})\s*%?",
        r"\b(\d{2,3})\s*%\b"
    ]

    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            try:
                val = int(m.group(1))
                if 40 <= val <= 100:
                    return val
            except:
                continue

    return None


# =====================================================
# OXYGEN FLOW
# =====================================================

def extract_oxygen_flow(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:L|liters|liter)", text, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return None


def detect_supplemental_o2(text: str) -> bool:
    patterns = [
        r"\bplaced on\b.*(nasal cannula|oxygen)",
        r"\brequiring supplemental oxygen\b",
        r"\bon .*L nasal cannula\b",
        r"\bon oxygen\b"
    ]

    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True

    if extract_oxygen_flow(text) is not None:
        return True

    return False


# =====================================================
# VITALS
# =====================================================

def extract_bp(text: str) -> tuple[Optional[int], Optional[int]]:
    m = re.search(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b", text)
    if m:
        try:
            return int(m.group(1)), int(m.group(2))
        except:
            pass
    return None, None


def extract_wbc(text: str) -> Optional[float]:
    m = re.search(r"\bWBC\b[^0-9]{0,10}(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return None


# =====================================================
# IMAGING
# =====================================================

def detect_pneumonia(text: str) -> bool:
    patterns = [
        r"\bpneumonia\b",
        r"\binfiltrate\b",
        r"\bconsolidation\b",
        r"\bright lower lobe\b",
        r"\brll\b"
    ]

    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True

    return False


# =====================================================
# RESPIRATORY FAILURE
# =====================================================

def detect_respiratory_failure(text: str) -> bool:
    if re.search(r"\brespiratory failure\b", text, flags=re.IGNORECASE):
        return True

    spo2 = extract_spo2(text)
    supp_o2 = detect_supplemental_o2(text)

    if spo2 is not None and spo2 < 90 and supp_o2:
        return True

    return False


# =====================================================
# ANTIBIOTICS
# =====================================================

def detect_iv_antibiotics(text: str) -> bool:
    patterns = [
        r"\bIV antibiotics\b",
        r"\bintravenous antibiotics\b",
        r"\bzosyn\b",
        r"\bvancomycin\b",
        r"\bceftriaxone\b",
        r"\bcefepime\b",
        r"\bpiperacillin\b"
    ]

    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True

    return False


# =====================================================
# FAILED OUTPATIENT
# =====================================================

def detect_failed_outpatient(text: str) -> bool:
    patterns = [
        r"\bfailed outpatient\b",
        r"\bfailure of outpatient\b",
        r"\bworsen(?:ed|ing).*antibiotic\b",
        r"\bfailed.*azithromycin\b"
    ]

    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True

    return False


# =====================================================
# MAIN FEATURE ASSEMBLER
# =====================================================

def extract_patient_features(raw_text: str) -> Dict[str, Any]:

    text = normalize_text(raw_text)

    spo2 = extract_spo2(text)
    oxygen_flow = extract_oxygen_flow(text)
    supplemental_o2 = detect_supplemental_o2(text)

    features: Dict[str, Any] = {
        "age": extract_age(text),
        "o2_sat": spo2,
        "oxygen_flow_lpm": oxygen_flow,
        "supplemental_o2": supplemental_o2,
        "sbp": extract_bp(text)[0],
        "wbc": extract_wbc(text),
        "pneumonia": detect_pneumonia(text),
        "respiratory_failure": detect_respiratory_failure(text),
        "iv_abx": detect_iv_antibiotics(text),
        "failed_outpatient": detect_failed_outpatient(text)
    }

    return features


# =====================================================
# LOCAL TEST
# =====================================================

if __name__ == "__main__":
    sample = (
        "Patient is a 82-year-old female. Oxygen saturation dropped to 89%. "
        "Placed on 2 L nasal cannula. WBC 12.4. "
        "Chest x-ray demonstrates right lower lobe pneumonia. "
        "Started on IV Zosyn. Failed outpatient azithromycin."
    )

    import json
    print(json.dumps(extract_patient_features(sample), indent=2))