// frontend/src/services/api.ts

const BASE_URL = "https://clinicalnlp-backend.onrender.com";

type ApiResult = {
  ok: boolean;
  status: number;
  data?: any;
  revisedNoteText?: string;
  extractedCriteria?: any[];
  missingCriteria?: any[];
  overallScore?: number;
  admissionRecommended?: boolean;
  rawPdfPreview?: string;
  error?: string;
};

async function _safeJson(resp: Response) {
  try {
    return await resp.json();
  } catch (e) {
    return null;
  }
}

function _normalize(json: any): Partial<ApiResult> {
  if (!json) return {};

  const revisedNotesObj = json?.revisedNotes ?? {};

  const revisedNoteText =
    json?.revisedNoteText ??
    (revisedNotesObj && typeof revisedNotesObj === "object"
      ? [
          revisedNotesObj.clinicalSummary,
          revisedNotesObj.medicalNecessityJustification,
          revisedNotesObj.riskStratification,
          revisedNotesObj.conclusion,
        ]
          .filter(Boolean)
          .join("\n\n")
      : "");

  const overallScore =
    Number(json?.overallScore ?? json?.percentage ?? 0) || 0;

  const admissionRecommended = Boolean(json?.admissionRecommended);

  return {
    data: json,
    revisedNoteText,
    extractedCriteria: json?.extractedCriteria ?? [],
    missingCriteria: json?.missingCriteria ?? [],
    overallScore,
    admissionRecommended,
    rawPdfPreview:
      json?.rawPdfSectionsPreview ?? json?.rawPdfPreview ?? "",
  };
}

export async function analyzeNote(
  note: string
): Promise<ApiResult> {
  try {
    const res = await fetch(`${BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note }),
    });

    const json = await _safeJson(res);

    if (!res.ok) {
      return {
        ok: false,
        status: res.status,
        error: json?.message ?? res.statusText,
      };
    }

    return {
      ok: true,
      status: res.status,
      ...(_normalize(json) as any),
    };
  } catch (err: any) {
    console.error("analyzeNote error", err);
    return {
      ok: false,
      status: 0,
      error: String(err),
    };
  }
}

export async function uploadAndAnalyze(
  doctorNote: string,
  guidelineFile: File
): Promise<ApiResult> {
  try {
    const form = new FormData();
    form.append("doctor_note", doctorNote);
    form.append("guideline", guidelineFile);

    const res = await fetch(
      `${BASE_URL}/analyze-with-guideline`,
      {
        method: "POST",
        body: form,
      }
    );

    const json = await _safeJson(res);

    if (!res.ok) {
      return {
        ok: false,
        status: res.status,
        error: json?.message ?? res.statusText,
      };
    }

    return {
      ok: true,
      status: res.status,
      ...(_normalize(json) as any),
    };
  } catch (err: any) {
    console.error("uploadAndAnalyze error", err);
    return {
      ok: false,
      status: 0,
      error: String(err),
    };
  }
}

export const analyzeWithGuideline = uploadAndAnalyze;