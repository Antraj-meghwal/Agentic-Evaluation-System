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
            const first = response.data.items?.[0];
            if (first?.id) {
                navigate(`/uploads/${first.id}`);
            } else {
                navigate("/uploads");
            }
        } catch (err) {
            setMessage(err.response?.data?.detail || "Upload failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="max-w-3xl mx-auto pt-20 px-5">
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl">
                    <h1 className="text-4xl font-bold mb-2">Upload Exam Scans</h1>
                    <p className="text-slate-400 mb-8">
                        Bulk upload PDF answer sheets and attach a JSON rubric for granular grading criteria.
                    </p>

                    <form onSubmit={handleUpload} className="space-y-6">
                        <div>
                            <label className="text-sm text-slate-400 font-medium">
                                Exam files (PDF, PNG, JPG) — multiple allowed
                            </label>
                            <input
                                type="file"
                                multiple
                                accept=".pdf,.png,.jpg,.jpeg"
                                onChange={(e) => setFiles(Array.from(e.target.files || []))}
                                className="w-full mt-2 p-4 rounded-2xl bg-slate-800 border border-slate-700"
                            />
                            {files.length > 0 && (
                                <p className="text-xs text-slate-500 mt-2">
                                    {files.length} file(s) selected
                                </p>
                            )}
                        </div>

                        <div>
                            <label className="text-sm text-slate-400 font-medium">
                                Rubric JSON (optional)
                            </label>
                            <input
                                type="file"
                                accept=".json,application/json"
                                onChange={(e) => setRubricFile(e.target.files?.[0] || null)}
                                className="w-full mt-2 p-4 rounded-2xl bg-slate-800 border border-slate-700"
                            />
                            <p className="text-xs text-slate-500 mt-2">
                                See <code className="text-indigo-400">examples/sample_rubric.json</code> in the repo.
                            </p>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded-2xl font-semibold disabled:opacity-50"
                        >
                            {loading ? "Uploading…" : "Upload & continue"}
                        </button>
                    </form>

                    {message && (
                        <p className="mt-6 text-center text-slate-300">{message}</p>
                    )}
                </div>
            </div>
        </div>
    );
}
