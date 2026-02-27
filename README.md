# 🏥 clinicalNLP-deterministic  
### Deterministic Clinical Documentation Optimization & MCG Admission Engine  

A production-oriented deterministic clinical NLP system that transforms unstructured emergency department documentation into structured clinical intelligence and MCG-aligned admission reasoning.

This version removes probabilistic LLM dependence and implements a fully rule-based, severity-weighted, multi-domain clinical reasoning pipeline suitable for transparent clinical decision support simulation.

---

# 🚀 Core Capabilities

- PDF clinical document ingestion  
- Structured section parsing (HPI, Vitals, Labs, Imaging)  
- Deterministic clinical feature extraction (regex + structured signals)  
- Multi-organ dysfunction detection  
- Hypoxemia & respiratory severity detection  
- Renal dysfunction scoring (BUN, Creatinine, GFR)  
- Coagulation risk detection (INR)  
- Treatment escalation detection (IV antibiotics)  
- Functional / disposition risk detection (Assisted living, DNR/DNI)  
- Weighted MCG-aligned severity scoring engine  
- Deterministic criteria evaluator  
- Structured admission narrative generation  
- FastAPI backend with REST integration  

---

# 🧠 Architecture Overview

This system uses a pure deterministic symbolic reasoning pipeline:

PDF Upload  
↓  
pdf_section_parser.py  
↓  
note_extractor.py  
↓  
clinical_extractor.py  
↓  
criteria_evaluator.py  
↓  
determination_engine.py  
↓  
justification_builder.py  
↓  
Structured JSON Output  

No generative LLM is required.

---

# 🏗 System Design Principles

## 1️⃣ Deterministic Signal Construction

All clinical findings are extracted via structured pattern recognition:

- Regex-based numeric lab detection  
- Oxygen saturation normalization  
- Structured comorbidity parsing  
- Imaging keyword recognition  
- Treatment escalation detection  
- Functional risk extraction  

No hallucination. No probabilistic drift.

---

## 2️⃣ Multi-System Severity Model

Severity scoring is weighted across domains:

| Domain        | Examples                                                   |
|---------------|------------------------------------------------------------|
| Pulmonary     | Hypoxemia, tachypnea, bilateral pneumonia                  |
| Renal         | Elevated BUN, Creatinine, reduced GFR                      |
| Infectious    | Leukocytosis, radiographic pneumonia                       |
| Coagulation   | INR elevation                                              |
| Escalation    | IV broad-spectrum antibiotics                              |
| Functional    | Assisted living, DNR/DNI                                   |
| Risk          | Advanced age, comorbidities                                |

Final structured output includes:

- severityScore  
- riskScore  
- totalScore  
- unsafeDischarge  
- level (admission determination)  

---

## 3️⃣ Structured Admission Narrative Generation

justification_builder.py generates:

- Expanded clinical summary  
- Multi-organ medical necessity rationale  
- Risk stratification explanation  
- Deterministic admission conclusion  

This simulates real utilization review documentation.

---

# 📂 Project Structure

backend/

├── clinical_extractor.py        # Structured clinical feature extraction  
├── criteria_evaluator.py        # Deterministic MCG rule matching  
├── determination_engine.py      # Weighted severity scoring model  
├── justification_builder.py     # Structured admission narrative generation  
├── pdf_section_parser.py        # PDF clinical section parsing  
├── note_extractor.py            # Raw note extraction layer  
├── mcg_criteria.py              # MCG guideline representation  
├── rule_matrix.py               # Domain scoring logic  
├── alignment_engine.py          # Criteria alignment orchestration  
├── admission_scorer.py          # Scoring utilities  
├── templates.py                 # Output templates  
└── main.py                      # FastAPI entrypoint  

Frontend:

- React + Vite  
- TypeScript  
- TailwindCSS  
- REST integration  

---

# 🔬 Clinical Intelligence Examples

### Example Signals Automatically Detected

- SpO2 88% → Hypoxemia  
- O2 4L NC → Oxygen requirement  
- Bilateral infiltrates → Severe pulmonary involvement  
- BUN 49 → Renal dysfunction  
- GFR 40 → Reduced renal reserve  
- INR 2.1 → Elevated bleeding risk  
- Vancomycin + Cefepime → Broad-spectrum IV escalation  
- DNR/DNI → Advanced directive risk  
- Assisted living → Functional dependency  

---

# 📊 Severity Scoring Model

Weighted deterministic scoring example:

Hypoxemia +40  
Oxygen Requirement +25  
Bilateral Pneumonia +10  
Tachypnea +10  
Leukocytosis +10  
Elevated BUN +5  
Reduced GFR +5  
Elevated INR +5  
IV Antibiotics +15  
Advanced Age +5  
Comorbidities +5  
Functional Risk +3  

totalScore is capped at 100.

Admission levels:

- Inpatient – Unsafe for discharge  
- Inpatient – Strong MCG support  
- Inpatient – MCG supported  
- Inpatient – Consider admission  
- Observation / Outpatient  

---

# 🧪 Representative Test Cases

## Case 1 – Bilateral Pneumonia with Renal Dysfunction

- Hypoxemia 88%  
- Bilateral infiltrates  
- BUN 49  
- Creatinine 1.7  
- IV antibiotics  
- DNR/DNI  

System Output:

- Multi-organ severity detection  
- Unsafe discharge flagged  
- TotalScore > 80%  
- Inpatient – Strong MCG support  

---

## Case 2 – Progressive Hypoxia

- Right lower lobe pneumonia  
- WBC 12.4  
- Oxygen requirement 2L NC  
- Outpatient antibiotic failure  

System Output:

- Pulmonary severity detected  
- Escalation logic triggered  
- Structured admission rationale generated  

---

# 🛠 Tech Stack

## Backend

- Python 3.11+  
- FastAPI  
- Pydantic  
- Deterministic rule engine  
- Structured JSON output  

## Frontend

- React  
- Vite  
- TypeScript  
- TailwindCSS  

## PDF Processing

- pdfplumber  
- pypdfium2  

---

# ⚙️ Setup

git clone <repo-url>  
cd clinicalNLP-deterministic  

python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

uvicorn backend.main:app --reload  

Test endpoint:

curl -X POST http://127.0.0.1:8000/upload -F "file=@/path/to/ER_note.pdf"

---

# 🔎 Deterministic vs LLM-Based Approach

| LLM Version              | Deterministic Version         |
|--------------------------|------------------------------|
| Probabilistic reasoning  | Fully rule-based              |
| Possible hallucination   | No hallucination              |
| Model-dependent          | Model-independent             |
| Black-box inference      | Transparent scoring           |
| Non-reproducible outputs | Fully reproducible outputs    |

---

# 🎯 Intended Use Cases

- Clinical documentation optimization  
- Utilization review simulation  
- MCG admission support modeling  
- Deterministic severity stratification research  
- Hybrid symbolic clinical reasoning experiments  

---

clinicalNLP-deterministic demonstrates how structured clinical intelligence can be built without reliance on large language model inference, using a transparent, explainable, severity-weighted architecture suitable for regulated healthcare environments.