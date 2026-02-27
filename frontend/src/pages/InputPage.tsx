// frontend/src/pages/InputPage.tsx
import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { analyzeWithGuideline } from "@/services/api";

/**
 * InputPage
 * - 负责上传 doctor notes + guideline PDF
 * - 调用后端 API，然后把结果规范化为 OutputPage 期待的 shape 并 navigate
 */

const InputPage: React.FC = () => {
  const navigate = useNavigate();

  const [notes, setNotes] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const fileObj = e.dataTransfer.files[0];
    if (fileObj && fileObj.type === "application/pdf") {
      setFileName(fileObj.name);
      setFile(fileObj);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileObj = e.target.files?.[0];
    if (fileObj && fileObj.type === "application/pdf") {
      setFileName(fileObj.name);
      setFile(fileObj);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      if (!notes.trim()) {
        alert("Please enter Doctor Raw Notes.");
        setLoading(false);
        return;
      }

      if (!file) {
        alert("Please upload MCG Guideline PDF.");
        setLoading(false);
        return;
      }

      // call API (analyzeWithGuideline 已在 frontend/services/api.ts 中封装)
      const result = await analyzeWithGuideline(notes, file);

      console.log("Raw API wrapper result:", result);

      // wrapper signals error
      if (result && (result as any).ok === false) {
        const errMsg = (result as any).error || "Analyze API returned error";
        console.error("API Error:", errMsg, result);
        alert(`Analysis failed: ${errMsg}`);
        setLoading(false);
        return;
      }

      // apiJson may be in result.data (wrapper) or the result itself
      const apiJson = (result as any)?.data ?? result;

      // build revised note text robustly
      const revisedNoteText =
        apiJson?.revisedNoteText ??
        (apiJson?.revisedNotes
          ? [
              apiJson.revisedNotes.clinicalSummary,
              apiJson.revisedNotes.medicalNecessityJustification,
              apiJson.revisedNotes.riskStratification,
              apiJson.revisedNotes.conclusion,
            ]
              .filter(Boolean)
              .join("\n\n")
          : "");

      // --- Robust selection of missingCriteria source ---
      // 1) prefer wrapper-top-level normalized missingCriteria (some wrappers put normalized fields top-level)
      const topMissingFromWrapper = (result as any)?.missingCriteria;
      // 2) fallback to backend payload fields
      const rawMissing =
        topMissingFromWrapper ??
        apiJson?.missingCriteria ??
        apiJson?.evaluated ??
        apiJson?._rawEvaluatedPreview ??
        [];

      // Normalize each criterion: preserve guideline & action if present (these come from backend canonical)
      const missingCriteria = Array.isArray(rawMissing)
        ? rawMissing.map((e: any, idx: number) => {
            // normalize status
            let status: "Met" | "Missing" | "Partial" = "Missing";
            const st = String(e?.status ?? "").toLowerCase();
            if (st === "met" || st === "yes" || st === "satisfied" || st === "true") status = "Met";
            else if (st.includes("part") || st.includes("partial")) status = "Partial";
            else status = "Missing";

            // title precedence: explicit title/label -> guideline/criterionText -> id fallback
            const criteriaTitle =
              e?.title ??
              e?.label ??
              e?.criterionText ??
              e?.guideline ??
              e?.criterion ??
              e?.text ??
              (e?.criterionId ? `Criterion ${e.criterionId}` : `Criterion ${idx + 1}`);

            const evidence = e?.evidenceFound ?? e?.evidence ?? e?.evidenceText ?? "";

            // prefer canonical 'guideline' provided by backend; fallback to text fields
            const guideline = e?.guideline ?? e?.criterionText ?? e?.criterion ?? e?.text ?? "";

            // actions: action / suggestedLanguage / suggested
            const action = e?.action ?? e?.suggestedLanguage ?? e?.suggested ?? "";

            return {
              criteria: criteriaTitle,
              status,
              evidence,
              guideline,
              action,
            };
          })
        : [];

      // extracted criteria fallback
      const extractedCriteria = apiJson?.extractedCriteria ?? [];

      // final analysis object that OutputPage currently expects
      const analysis = {
        revisedNote: revisedNoteText || "",
        missingCriteria,
        extractedCriteria,
        overallScore: apiJson?.overallScore ?? apiJson?.percentage ?? 0,
        admissionRecommended: apiJson?.admissionRecommended ?? false,
        rawPdfPreview: apiJson?.rawPdfSectionsPreview ?? apiJson?.rawPdfPreview ?? "",
        _rawApiResponse: apiJson, // optional, keep for debugging in OutputPage
      };

      console.log("Normalized analysis to pass to OutputPage:", analysis);

      // Pass full analysis object into router state
      navigate("/output", { state: { analysis } });
    } catch (err) {
      console.error("API error:", err);
      alert("Analysis failed. Please check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />

      <main className="flex-1 px-8 py-8">
        <div className="mx-auto max-w-6xl">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-foreground">
              Clinical Documentation Optimization
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              AI-powered documentation enhancement.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Left - Doctor Notes */}
            <div className="rounded-lg border border-border bg-card p-6 shadow-card">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide">
                Doctor Raw Notes
              </h2>

              <div className="relative">
                <Textarea
                  placeholder="Paste physician documentation here..."
                  className="min-h-[320px] resize-none text-sm"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
                <span className="absolute bottom-3 right-3 text-xs text-muted-foreground">
                  {notes.length} characters
                </span>
              </div>
            </div>

            {/* Right - PDF Upload (Optional UI only) */}
            <div className="rounded-lg border border-border bg-card p-6 shadow-card">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-wide">
                  MCG Guideline PDF
                </h2>
              </div>

              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                className={`flex min-h-[320px] flex-col items-center justify-center rounded-md border-2 border-dashed transition-colors ${
                  dragOver ? "border-primary bg-accent" : "border-border bg-background"
                }`}
              >
                {fileName ? (
                  <div className="flex flex-col items-center gap-3 text-center">
                    <FileText className="h-10 w-10 text-primary" />
                    <div>
                      <p className="text-sm font-medium">{fileName}</p>
                      <p className="text-xs text-muted-foreground">PDF uploaded</p>
                    </div>

                    <button
                      onClick={() => {
                        setFileName(null);
                        setFile(null);
                      }}
                      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <X className="h-3 w-3" /> Remove
                    </button>
                  </div>
                ) : (
                  <label className="flex cursor-pointer flex-col items-center gap-3 text-center">
                    <Upload className="h-10 w-10 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Drop PDF here or click to upload</p>
                      <p className="text-xs text-muted-foreground">Optional</p>
                    </div>

                    <input type="file" accept=".pdf" className="hidden" onChange={handleFileSelect} />
                  </label>
                )}
              </div>
            </div>
          </div>

          {/* Analyze Button */}
          <div className="mt-8 flex justify-center">
            <Button size="lg" className="px-12" onClick={handleAnalyze} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Documentation"}
            </Button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default InputPage;