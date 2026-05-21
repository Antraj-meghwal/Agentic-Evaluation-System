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
            let res;
            if (rubricFile) {
                const fd = new FormData();
                fd.append("rubric", rubricFile);
                res = await API.post(`/grading/run/${id}/rubric`, fd, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
            } else {
                res = await API.post(`/grading/run/${id}`);
            }
            setPipelineResult(res.data);
            await fetchUpload();
        } catch (e) {
            setError(e.response?.data?.detail || "Tribunal grading failed.");
        } finally {
            setBusy("");
        }
    }

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
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const extension = type === 'json' ? 'json' : 'csv';
            link.setAttribute('download', `gradebook_upload_${id}.${extension}`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (e) {
            setError(
                e.response?.data?.detail || 
                (e.response?.data instanceof Blob ? await e.response.data.text() : `Failed to download ${type} export.`)
            );
        } finally {
            setBusy("");
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
                Loading…
            </div>
        );
    }

    if (!upload) {
        return (
            <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
                Upload not found
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="p-10 max-w-6xl mx-auto">
                <h1 className="text-5xl font-bold mb-10">Upload Details</h1>

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">
                    <h2 className="text-3xl font-semibold">{upload.filename}</h2>
                    <div className="mt-5">
                        <StatusBadge status={upload.status} />
                    </div>
                    <p className="mt-5 text-slate-500">
                        Uploaded: {new Date(upload.created_at).toLocaleString()}
                    </p>
                    <a
                        href={upload.file_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-block mt-6 text-blue-400 hover:underline"
                    >
                        Open file
                    </a>

                    <div className="mt-8 border-t border-slate-800 pt-8">
                        <h3 className="text-xl font-semibold mb-4">Grading rubric (JSON)</h3>
                        <input
                            type="file"
                            accept=".json,application/json"
                            onChange={(e) => setRubricFile(e.target.files[0] || null)}
                            className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700"
                        />
                        <p className="text-slate-500 text-sm mt-2">
                            Optional. Uses sample rubric if omitted.
                        </p>
                    </div>

                    <div className="mt-8 flex flex-wrap gap-4">
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={runExtract}
                            className="bg-slate-700 hover:bg-slate-600 px-6 py-4 rounded-2xl font-semibold disabled:opacity-50"
                        >
                            {busy === "extract" ? "Extracting…" : "1. Extract (OCR)"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={runTribunal}
                            className="bg-indigo-600 hover:bg-indigo-500 px-6 py-4 rounded-2xl font-semibold disabled:opacity-50"
                        >
                            {busy === "tribunal" ? "Grading…" : "2. Run Tribunal"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={loadResults}
                            className="bg-blue-600 hover:bg-blue-500 px-6 py-4 rounded-2xl font-semibold disabled:opacity-50"
                        >
                            View results
                        </button>
                    </div>

                    <div className="mt-8 flex flex-wrap gap-4 border-t border-slate-800 pt-8">
                        <h3 className="text-xl font-semibold w-full">Export Gradebook</h3>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={() => downloadExport("csv")}
                            className="bg-slate-700 hover:bg-slate-600 px-5 py-3 rounded-xl font-medium disabled:opacity-50"
                        >
                            {busy === "export-csv" ? "Exporting..." : "Standard CSV"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={() => downloadExport("canvas-csv")}
                            className="bg-slate-700 hover:bg-slate-600 px-5 py-3 rounded-xl font-medium disabled:opacity-50"
                        >
                            {busy === "export-canvas-csv" ? "Exporting..." : "Canvas LMS CSV"}
                        </button>
                        <button
                            type="button"
                            disabled={!!busy}
                            onClick={() => downloadExport("json")}
                            className="bg-slate-700 hover:bg-slate-600 px-5 py-3 rounded-xl font-medium disabled:opacity-50"
                        >
                            {busy === "export-json" ? "Exporting..." : "JSON File"}
                        </button>
                    </div>

                    {error && (
                        <p className="mt-4 text-red-400 text-sm">{error}</p>
                    )}

                    {pipelineResult && (
                        <div className="mt-10 bg-slate-800 border border-slate-700 rounded-2xl p-6">
                            <h2 className="text-2xl font-bold mb-4">Pipeline output</h2>
                            {pipelineResult.results && (
                                <div className="space-y-4 mb-6">
                                    {pipelineResult.results.map((r) => (
                                        <div
                                            key={r.grading_result_id || r.question_id}
                                            className="p-4 bg-slate-900 rounded-xl border border-slate-700"
                                        >
                                            <p className="font-medium">
                                                {r.question_id}: {r.score}/{r.max_score}
                                                {r.requires_human_review && (
                                                    <span className="ml-2 text-orange-400 text-sm">
                                                        → needs review
                                                    </span>
                                                )}
                                            </p>
                                            <p className="text-slate-400 text-sm mt-1">
                                                {r.feedback}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {pipelineResult.plagiarism_flags?.length > 0 && (
                                <p className="text-amber-400 text-sm mb-4">
                                    Plagiarism flags:{" "}
                                    {JSON.stringify(pipelineResult.plagiarism_flags)}
                                </p>
                            )}
                            <pre className="whitespace-pre-wrap text-slate-400 text-xs overflow-auto max-h-64">
                                {JSON.stringify(pipelineResult, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
