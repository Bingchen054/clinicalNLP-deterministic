# backend/pdf_section_parser.py
from typing import Dict, List, Tuple

def parse_pdf_sections(pdf_text: str) -> Dict[str, List[str]]:

    sections: Dict[str, List[str]] = {}
    lines = [l.strip() for l in pdf_text.splitlines() if l.strip()]
    current_section = "general"
    sections[current_section] = []

    for i, line in enumerate(lines):
        low = line.lower()
        if "admission criteria" in low or low.startswith("criteria") or "clinical indications" in low or "indications for admission" in low or ("criteria" in low and ("pneumonia" in low or "admission" in low)):
            current_section = "admissionCriteria"
            sections.setdefault(current_section, [])
            # don't append the header line itself as content
            continue

        if low.endswith(":") or low.isupper() and len(low.split()) < 6:
            # start a new generic section name
            current_section = low.replace(" ", "_")[:40]
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    # ensure admissionCriteria exists (may be empty)
    sections.setdefault("admissionCriteria", [])
    # also include full raw text lines for fallback/debug
    sections.setdefault("raw_all_lines", lines)

    return sections