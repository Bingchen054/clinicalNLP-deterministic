import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Download, Printer, Save, ChevronDown, ChevronRight } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import html2pdf from "html2pdf.js";
import { saveAs } from "file-saver";

interface CriteriaRow {
  criteria: string;
  status: "Met" | "Missing" | "Partial";
  evidence: string;
  guideline: string;
  action: string;
}

const StatusBadge = ({ status }: { status: CriteriaRow["status"] }) => {
  const styles = {
    Met: "bg-green-100 text-green-700",
    Missing: "bg-red-100 text-red-700",
    Partial: "bg-yellow-100 text-yellow-700",
  };

  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${
        styles[status] || "bg-gray-200 text-gray-700"
      }`}
    >
      {status}
    </span>
  );
};

const OutputPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  // The router state may contain { analysis } or the analysis object itself
  const stateData = (location.state as any) ?? {};
  const dataCandidate = stateData.analysis ?? stateData;

  useEffect(() => {
  // 序列化快照，避免引用导致的“展开时是空”的问题
  try {
    const snapshot = JSON.parse(JSON.stringify(location.state ?? {}));
    console.log("OutputPage location.state (snapshot):", snapshot);
    // 存到 window 下，方便手动访问
    (window as any).__lastLocationStateSnapshot = snapshot;
    // 也存个 shorter alias 以保险
    (window as any).__lastLocationState = snapshot;
  } catch (err) {
    console.warn("Failed to stringify location.state; logging raw object:", err);
    console.log("Raw location.state:", location.state);
    (window as any).__lastLocationStateSnapshot = location.state;
  }
}, [location.state]);

  // If nothing passed, show friendly message
  if (!dataCandidate || Object.keys(dataCandidate).length === 0) {
    return (
      <div className="flex min-h-screen flex-col bg-background">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-semibold">No Analysis Data Found</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              The output page expects analysis data passed via navigation state.
            </p>
            <div className="mt-4">
              <button
                onClick={() => navigate("/input")}
                className="px-4 py-2 bg-purple-600 text-white rounded-md"
              >
                Go Back to Input
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Normalize keys (support several possible API shapes)
  // Step 1: 优先使用 revisedNote
  let revisedNote: string = dataCandidate?.revisedNote ?? "";

  // Step 2: 如果没有，用 revisedNoteText
  if (!revisedNote) {
    revisedNote = dataCandidate?.revisedNoteText ?? "";
  }

  // Step 3: 如果还没有，用 revisedNotes 结构拼接
  if (!revisedNote && dataCandidate?.revisedNotes) {
    const rn = dataCandidate.revisedNotes;
    revisedNote = [
      rn.clinicalSummary,
      rn.medicalNecessityJustification,
      rn.riskStratification,
      rn.conclusion,
    ]
      .filter(Boolean)
      .join("\n\n");
  }

  // 原始 missing / evaluated 列表
  const rawMissing = dataCandidate.missingCriteria ?? dataCandidate.missing ?? dataCandidate.evaluated ?? [];

  // 归一化映射：优先显示 guideline（后端 canonical text），并保证列表标题有短文本
  const missingCriteria: CriteriaRow[] = Array.isArray(rawMissing)
    ? rawMissing.map((e: any, idx: number) => {
        // guideline（canonical full text）优先
// guideline (canonical full text) 优先
        const guidelineFull =
          e?.guideline ??
          e?.criterionText ??
          e?.criterion ??
          e?.text ??
          (
            (e?.criterionId ? `Guideline ${e.criterionId}` : "") ||
            `Criterion ${idx + 1}`
          );

        // 短标题优先：title/label/短版 guideline / first 80 chars
        const criterionTitle =
          e?.title ??
          e?.label ??
          (typeof guidelineFull === "string" && guidelineFull.length > 0
            ? guidelineFull.split("\n")[0].slice(0, 120)
            : `Criterion ${idx + 1}`);

        // evidence 可能在不同字段
        const evidence =
          e?.evidenceFound ??
          e?.evidence ??
          e?.evidenceText ??
          e?.evidence_found ??
          "";

        // action / suggested language (UI hint)
        const suggested =
          e?.action ??
          e?.suggestedLanguage ??
          e?.suggested ??
          "";

        // 状态标准化处理
        const statusRaw = String(e?.status ?? "").toLowerCase();
        let status: CriteriaRow["status"] = "Missing";
        if (statusRaw === "met" || statusRaw === "yes" || statusRaw === "satisfied") status = "Met";
        else if (statusRaw.includes("part")) status = "Partial";
        else status = "Missing";

        return {
          criteria: criterionTitle,
          status,
          evidence,
          guideline: guidelineFull,
          action: suggested,
        } as CriteriaRow;
      })
    : [];

  // provide fallback for extracted criteria (not used in UI here, but kept)
  const extractedCriteria = dataCandidate.extractedCriteria ?? dataCandidate.criteria ?? [];

  const toggleRow = (index: number) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const handleExportPDF = () => {
    const element = document.getElementById("print-area");
    if (!element) return;

    html2pdf()
      .from(element)
      .set({
        margin: 10,
        filename: "Clinical_Analysis.pdf",
        html2canvas: { scale: 2 },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
      })
      .save();
  };

  const handleExportWord = () => {
    const element = document.getElementById("print-area");
    if (!element) return;

    const content = element.innerHTML;
    const blob = new Blob(
      [
        `
        <html>
        <head><meta charset="utf-8"></head>
        <body>${content}</body>
        </html>
        `,
      ],
      { type: "application/msword" }
    );

    saveAs(blob, "Clinical_Analysis.doc");
  };

  const handleSave = () => {
    try {
      localStorage.setItem("lastClinicalAnalysis", JSON.stringify(dataCandidate));
      alert("Saved locally.");
    } catch (err) {
      console.error("Failed to save:", err);
      alert("Save failed (see console).");
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />

      <main id="print-area" className="flex-1 px-8 py-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Analysis Results</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Documentation review completed — review suggestions below.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExportPDF}
                className="px-4 py-2 border rounded-md hover:bg-gray-100 text-sm flex items-center"
              >
                <Download className="mr-1.5 h-4 w-4" />
                Export PDF
              </button>

              <button
                onClick={handleExportWord}
                className="px-4 py-2 border rounded-md hover:bg-gray-100 text-sm flex items-center"
              >
                <Download className="mr-1.5 h-4 w-4" />
                Export Word
              </button>

              <button
                onClick={() => window.print()}
                className="px-4 py-2 border rounded-md hover:bg-gray-100 text-sm flex items-center"
              >
                <Printer className="mr-1.5 h-4 w-4" />
                Print
              </button>

              <button
                onClick={handleSave}
                className="px-4 py-2 bg-purple-600 text-white rounded-md text-sm flex items-center"
              >
                <Save className="mr-1.5 h-4 w-4" />
                Save
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
            <div className="xl:col-span-3">
              <div className="rounded-lg border bg-card p-6 shadow-card">
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-sm font-semibold uppercase tracking-wide">Revised Doctor Notes</h2>
                </div>

                <div className="rounded-md border bg-background p-5 text-sm whitespace-pre-line min-h-[400px]">
                  {revisedNote && revisedNote.trim() ? revisedNote : "No revised note generated."}
                </div>
              </div>
            </div>

            <div className="xl:col-span-2">
              <div className="rounded-lg border bg-card p-6 shadow-card">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide">Missing Criteria Analysis</h2>

                {missingCriteria && missingCriteria.length > 0 ? (
                  <div className="divide-y">
                    {missingCriteria.map((row: CriteriaRow, index: number) => (
                      <div key={index}>
                        <button
                          onClick={() => toggleRow(index)}
                          className="flex w-full items-start gap-3 py-3 text-left"
                        >
                          <span className="mt-0.5">
                            {expandedRows.has(index) ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                          </span>

                          <div className="flex-1">
                            <p className="text-sm font-medium">{row.criteria}</p>
                            <div className="mt-1.5 flex items-center gap-2">
                              <StatusBadge status={row.status} />
                            </div>
                          </div>
                        </button>

                        {expandedRows.has(index) && (
                          <div className="ml-7 mb-3 p-4 text-sm space-y-2">
                            <p><strong>Evidence:</strong> {row.evidence || "—"}</p>
                            <p><strong>Guideline:</strong> {row.guideline || "—"}</p>
                            <p><strong>Action:</strong> {row.action || "—"}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No criteria analysis available.</p>
                )}
              </div>
            </div>
          </div>

          {/* Optionally show some meta/debug info */}
          {process.env.NODE_ENV === "development" && (
            <div className="mt-6 text-xs text-muted-foreground">
              <strong>Debug:</strong> raw API response is logged to console.
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default OutputPage;