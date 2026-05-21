import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import API from "../services/api";
import StatusBadge from "../components/StatusBadge";
import LoadingSpinner from "../components/LoadingSpinner";

export default function UploadsPage() {
    const navigate = useNavigate();
    const [uploads, setUploads] = useState([]);
    const [loading, setLoading] = useState(true);

    async function fetchUploads() {
        try {
            const response = await API.get("/uploads");
            setUploads(response.data);
        } catch (error) {
            console.log(error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchUploads();
    }, []);

    return (
        <div className="page-bg">
            <Navbar />
            <div className="max-w-4xl mx-auto p-6 md:p-10">
                <h1 className="text-3xl md:text-4xl font-extrabold heading-gradient mb-8">My Uploads</h1>

                {loading ? (
                    <LoadingSpinner />
                ) : uploads.length === 0 ? (
                    <div className="card-lg text-center py-12">
                        <p className="text-muted">No uploads yet. Head to Upload to add exam scans.</p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {uploads.map((upload) => (
                            <div
                                key={upload.id}
                                onClick={() => navigate(`/uploads/${upload.id}`)}
                                className="card p-6 cursor-pointer hover:border-teal-300 hover:shadow-lg hover:-translate-y-0.5 transition-all group"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex items-center gap-4">
                                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-100 to-violet-100 flex items-center justify-center text-teal-600 group-hover:scale-105 transition-transform shrink-0">
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h2 className="text-lg font-bold text-slate-800 group-hover:text-teal-700 transition-colors">
                                                {upload.filename}
                                            </h2>
                                            <p className="text-muted text-sm mt-1">
                                                {new Date(upload.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                    <StatusBadge status={upload.status} />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
