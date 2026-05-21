import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import API from "../services/api";

export default function UploadPage() {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [rubricFile, setRubricFile] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleUpload(e) {
        e.preventDefault();
        if (!files.length) {
            setMessage("Select one or more PDF/image files.");
            return;
        }

        try {
            setLoading(true);
            const formData = new FormData();
            for (const f of files) {
                formData.append("files", f);
            }
            if (rubricFile) {
                formData.append("rubric", rubricFile);
            }

            const response = await API.post("/upload/bulk", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            const count = response.data.uploaded;
            setMessage(`Uploaded ${count} file(s) successfully.`);
            const items = response.data.items ?? [];
            const first = items[0];
            if (first?.id != null) {
                navigate(`/uploads/${first.id}`);
            } else if (items.length > 0) {
                navigate("/uploads");
            } else {
                setMessage("Upload completed but no file records were returned.");
            }
        } catch (err) {
            setMessage(err.response?.data?.detail || "Upload failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="page-bg">
            <Navbar />
            <div className="max-w-3xl mx-auto pt-12 md:pt-16 px-5 pb-16">
                <div className="card-lg">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-violet-500 flex items-center justify-center shadow-lg shadow-teal-500/25">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-3xl font-extrabold text-slate-800">Upload Exam Scans</h1>
                            <p className="text-muted text-sm mt-1">
                                Bulk upload PDFs and attach a JSON rubric for grading.
                            </p>
                        </div>
                    </div>

                    <form onSubmit={handleUpload} className="space-y-6">
                        <div>
                            <label className="label-text">
                                Exam files (PDF, PNG, JPG) — multiple allowed
                            </label>
                            <input
                                type="file"
                                multiple
                                accept=".pdf,.png,.jpg,.jpeg"
                                onChange={(e) => setFiles(Array.from(e.target.files || []))}
                                className="input-file"
                            />
                            {files.length > 0 && (
                                <p className="text-xs text-teal-600 font-medium mt-2">
                                    {files.length} file(s) selected
                                </p>
                            )}
                        </div>

                        <div>
                            <label className="label-text">Rubric JSON (optional)</label>
                            <input
                                type="file"
                                accept=".json,application/json"
                                onChange={(e) => setRubricFile(e.target.files?.[0] || null)}
                                className="input-file"
                            />
                            <p className="text-xs text-muted mt-2">
                                See <code className="text-violet-600 font-medium">examples/sample_rubric.json</code> in the repo.
                            </p>
                        </div>

                        <button type="submit" disabled={loading} className="btn-primary-full">
                            {loading ? "Uploading…" : "Upload & Continue"}
                        </button>
                    </form>

                    {message && (
                        <p className="mt-6 text-center text-slate-600 font-medium">{message}</p>
                    )}
                </div>
            </div>
        </div>
    );
}
