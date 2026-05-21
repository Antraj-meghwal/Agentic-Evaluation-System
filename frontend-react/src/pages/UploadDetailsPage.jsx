import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import API from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function UploadDetailsPage() {
    const { id } = useParams();
    const [upload, setUpload] = useState(null);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState("");
    const [rubricFile, setRubricFile] = useState(null);
    const [pipelineResult, setPipelineResult] = useState(null);
    const [error, setError] = useState("");

    async function fetchUpload() {
        try {
            const response = await API.get("/uploads");
            const found = response.data.find((item) => item.id === Number(id));
            setUpload(found);
        } catch {
            setError("Could not load upload.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchUpload();
    }, [id]);

    async function runExtract() {
        setBusy("extract");
        setError("");
        try {
            let res;
            if (rubricFile) {
                const fd = new FormData();
                fd.append("rubric", rubricFile);
                res = await API.post(`/grading/extract/${id}/rubric`, fd, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
            } else {
                res = await API.post(`/grading/extract/${id}`);
            }
            setPipelineResult(res.data);
            await fetchUpload();
        } catch (e) {
            setError(e.response?.data?.detail || "Extract failed.");
        } finally {
            setBusy("");
        }
    }

    async function runTribunal() {
        setBusy("tribunal");
        setError("");
        try {
            if (rubricFile) {
                const fd = new FormData();
                fd.append("rubric", rubricFile);
                await API.post(`/grading/run-async/${id}/rubric`, fd, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
            } else {
                await API.post(`/grading/run-async/${id}`);
            }
            await fetchUpload();
        } catch (e) {
            setError(e.response?.data?.detail || "Queueing tribunal grading failed.");
        } finally {
            setBusy("");
        }
    }

    useEffect(() => {
        let interval;
        if (upload && upload.status === "processing") {
            interval = setInterval(async () => {
                try {
                    const response = await API.get("/uploads");
                    const found = response.data.find((item) => item.id === Number(id));
                    setUpload(found);

                    if (found && found.status !== "processing") {
                        clearInterval(interval);
                        if (found.status === "graded") {
                            loadResults();
                        } else if (found.status === "failed") {
                            setError("Background processing failed.");
                        }
                    }
                } catch {
                    // Ignore errors during polling
                }
            }, 2000);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [upload?.status, id]);

    async function loadResults() {
        setBusy("results");
        try {
            const res = await API.get(`/grading/results/${id}`);
            setPipelineResult(res.data);
        } catch {
            setError("No grading results yet.");
        } finally {
            setBusy("");
        }
    }

    async function downloadExport(type) {
        try {
            setBusy(`export-${type}`);
            const response = await API.get(`/api/export/${type}/${id}`, {
                responseType: "blob",
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;
            const extension = type === "json" ? "json" : "csv";
            link.setAttribute("download", `gradebook_upload_${id}.${extension}`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (e) {
            let detail = e.response?.data?.detail;
            if (!detail && e.response?.data instanceof Blob) {
                try {
                    detail = await e.response.data.text();
                } catch {
                    detail = null;
                }
            }
            setError(detail || `Failed to download ${type} export.`);
        } finally {
            setBusy("");
        }
    }

    if (loading) {
        return (
            <div className="page-bg flex items-center justify-center min-h-screen">
                <div className="w-10 h-10 border-4 border-teal-200 border-t-teal-500 rounded-full animate-spin" />
            </div>
        );
    }

    if (!upload) {
        return (
            <div className="page-bg flex items-center justify-center min-h-screen">
                <p className="text-muted font-medium">Upload not found</p>
            </div>
        );
    }

    return (
        <div className="page-bg">
            <Navbar />
            <div className="p-6 md:p-10 max-w-6xl mx-auto">
                <h1 className="text-3xl md:text-4xl font-extrabold heading-gradient mb-8">Upload Details</h1>

                <div className="card-lg">
                    <h2 className="text-2xl font-bold text-slate-800">{upload.filename}</h2>
                    <div className="mt-4">
                        <StatusBadge status={upload.status} />
                    </div>
                    <p className="mt-4 text-muted">
                        Uploaded: {new Date(upload.created_at).toLocaleString()}
                    </p>
                    <a
                        href={upload.file_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 mt-4 font-semibold text-teal-600 hover:text-teal-700 hover:underline"
                    >
                        Open file →
                    </a>

                    <div className="mt-8 border-t border-slate-100 pt-8">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Grading rubric (JSON)</h3>
                        <input
                            type="file"
                            accept=".json,application/json"
                            onChange={(e) => setRubricFile(e.target.files[0] || null)}
                            className="input-file"
                        />
                        <p className="text-muted text-sm mt-2">
                            Optional. Uses sample rubric if omitted.
                        </p>
                    </div>

                    <div className="mt-8 flex flex-wrap gap-3">
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={runExtract}
                            className="btn-secondary"
                        >
                            {busy === "extract" ? "Extracting…" : "1. Extract (OCR)"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy || upload?.status === "processing"}
                            onClick={runTribunal}
                            className="btn-primary"
                        >
                            {upload?.status === "processing"
                                ? "Processing…"
                                : busy === "tribunal"
                                  ? "Queueing…"
                                  : "2. Run Tribunal"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={loadResults}
                            className="btn-secondary"
                        >
                            View results
                        </button>
                    </div>

                    <div className="mt-8 border-t border-slate-100 pt-8">
                        <h3 className="text-lg font-bold text-slate-800 mb-4">Export Gradebook</h3>
                        <div className="flex flex-wrap gap-3">
                            <button
                                type="button"
                                disabled={!!busy}
                                onClick={() => downloadExport("csv")}
                                className="btn-secondary btn-sm"
                            >
                                {busy === "export-csv" ? "Exporting..." : "Standard CSV"}
                            </button>
                            <button
                                type="button"
                                disabled={!!busy}
                                onClick={() => downloadExport("canvas-csv")}
                                className="btn-secondary btn-sm"
                            >
                                {busy === "export-canvas-csv" ? "Exporting..." : "Canvas LMS CSV"}
                            </button>
                            <button
                                type="button"
                                disabled={!!busy}
                                onClick={() => downloadExport("json")}
                                className="btn-secondary btn-sm"
                            >
                                {busy === "export-json" ? "Exporting..." : "JSON File"}
                            </button>
                        </div>
                    </div>

                    {error && <p className="mt-4 text-rose-600 text-sm font-medium">{error}</p>}

                    {pipelineResult && (
                        <div className="mt-10 bg-slate-50 border border-slate-200 rounded-2xl p-6">
                            <h2 className="text-xl font-bold text-slate-800 mb-4">Pipeline output</h2>
                            {pipelineResult.results && (
                                <div className="space-y-3 mb-6">
                                    {pipelineResult.results.map((r) => (
                                        <div
                                            key={r.grading_result_id || r.question_id}
                                            className="p-4 bg-white rounded-xl border border-slate-100"
                                        >
                                            <p className="font-semibold text-slate-800">
                                                {r.question_id}: {r.score}/{r.max_score}
                                                {r.requires_human_review && (
                                                    <span className="ml-2 text-orange-600 text-sm font-medium">
                                                        → needs review
                                                    </span>
                                                )}
                                            </p>
                                            <p className="text-muted text-sm mt-1">{r.feedback}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {pipelineResult.plagiarism_flags?.length > 0 && (
                                <p className="text-amber-700 text-sm font-medium mb-4">
                                    Plagiarism flags:{" "}
                                    {JSON.stringify(pipelineResult.plagiarism_flags)}
                                </p>
                            )}
                            <pre className="whitespace-pre-wrap text-slate-500 text-xs overflow-auto max-h-64 bg-white p-4 rounded-xl border border-slate-100">
                                {JSON.stringify(pipelineResult, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
