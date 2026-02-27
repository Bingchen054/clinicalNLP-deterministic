# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import logging
from typing import Dict, Any, Optional

# package-relative import (important: use relative imports when running as package)
from .alignment_engine import run_alignment_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinicalnlp.backend")

app = FastAPI(title="Clinical NLP Deterministic Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    note: str

def safe_parse_pdf(upload_file: Optional[UploadFile]) -> str:
    """
    Read uploaded PDF using pdfplumber. Return text or empty string on any error.
    """
    if upload_file is None:
        return ""
    try:
        # Ensure file pointer at start
        try:
            upload_file.file.seek(0)
        except Exception:
            pass
        text_accum = []
        with pdfplumber.open(upload_file.file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_accum.append(text)
        return "\n".join(text_accum) if text_accum else ""
    except Exception as e:
        logger.exception("PDF parsing failed: %s", e)
        return ""

def _normalize_engine_result(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize different possible engine outputs into the frontend-expected shape.
    """
    if not raw:
        raw = {}
    revised_notes = raw.get("revisedNotes") or raw.get("revised_note") or raw.get("revisedNoteText") or {}
    if isinstance(revised_notes, str):
        revised_notes_obj = {"clinicalSummary": revised_notes}
    else:
        revised_notes_obj = revised_notes or {}
    missing_criteria = raw.get("missingCriteria") or raw.get("missing_criteria") or raw.get("evaluated") or raw.get("criteria") or []
    if not isinstance(missing_criteria, list):
        try:
            missing_criteria = list(missing_criteria)
        except Exception:
            missing_criteria = []
    overall_score = raw.get("overallScore") or raw.get("percentage") or raw.get("score") or 0
    try:
        overall_score = float(overall_score)
    except Exception:
        overall_score = 0
    admission_recommended = bool(raw.get("admissionRecommended") or raw.get("admission_recommended") or raw.get("admit") or False)
    return {
        "ok": True,
        "status": 200,
        "revisedNotes": revised_notes_obj,
        "revisedNoteText": raw.get("revisedNoteText") or " ".join([revised_notes_obj.get(k,"") for k in ["clinicalSummary","medicalNecessityJustification","riskStratification","conclusion"] if revised_notes_obj.get(k)]).strip(),
        "missingCriteria": missing_criteria,
        "extractedCriteria": raw.get("extractedCriteria") or raw.get("extracted_criteria") or [],
        "overallScore": overall_score,
        "admissionRecommended": admission_recommended,
        "rawPdfSectionsPreview": raw.get("rawPdfSectionsPreview") or raw.get("rawPdfPreview") or "",
        "_raw": raw,
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(data: AnalyzeRequest) -> Dict[str, Any]:
    doctor_notes = (data.note or "").strip()
    logger.info("Received /analyze request (len=%d)", len(doctor_notes))
    try:
        raw_result = run_alignment_engine(doctor_notes=doctor_notes, pdf_text="")
        logger.info("run_alignment_engine returned keys=%s", list(raw_result.keys()) if isinstance(raw_result, dict) else "non-dict")
        return _normalize_engine_result(raw_result)
    except Exception as e:
        logger.exception("Error in /analyze: %s", e)
        return {"ok": False, "status": 500, "error": "internal_server_error", "message": str(e)}

@app.post("/analyze-with-guideline")
async def analyze_with_guideline(
    doctor_note: str = Form(...),
    guideline: UploadFile = File(None)
) -> Dict[str, Any]:
    """
    Form endpoint the frontend uses: fields (doctor_note, guideline).
    """
    doctor_note = (doctor_note or "").strip()
    logger.info("Received /analyze-with-guideline (note_len=%d, filename=%s)", len(doctor_note), getattr(guideline, "filename", None))
    pdf_text = safe_parse_pdf(guideline)
    try:
        raw_result = run_alignment_engine(doctor_notes=doctor_note, pdf_text=pdf_text)
        logger.info("run_alignment_engine returned keys=%s", list(raw_result.keys()) if isinstance(raw_result, dict) else "non-dict")
        return _normalize_engine_result(raw_result)
    except Exception as e:
        logger.exception("Error in /analyze-with-guideline: %s", e)
        return {"ok": False, "status": 500, "error": "internal_server_error", "message": str(e)}