import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import API from "../services/api";

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        upload_count: 0,
        pending_reviews: 0,
        avg_class_score_pct: 0,
        recent_uploads: [],
    });

    useEffect(() => {
        async function fetchData() {
            try {
                const res = await API.get("/api/dashboard/professor");
                setStats(res.data);
            } catch (error) {
                console.log(error);
            }
        }
        fetchData();
    }, []);

    return (
        <div className="page-bg">
            <Navbar />
            <div className="max-w-7xl mx-auto p-6 md:p-10">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-800 mb-2">
                            Professor Dashboard
                        </h1>
                        <p className="text-muted">Manage and review AI evaluations efficiently.</p>
                    </div>
                    <button type="button" onClick={() => navigate("/upload")} className="btn-primary">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                        </svg>
                        New Upload
                    </button>
                </div>

                <div className="grid md:grid-cols-3 gap-5 mb-10">
                    <StatCard
                        title="Total Uploads"
                        value={stats.upload_count}
                        subtitle="Answer sheets processed"
                        onClick={() => navigate("/uploads")}
                        accent="teal"
                    />
                    <StatCard
                        title="Pending Reviews"
                        value={stats.pending_reviews}
                        subtitle="Requires human validation"
                        onClick={() => navigate("/review")}
                        accent="violet"
                    />
                    <StatCard
                        title="Avg. Class Score"
                        value={stats.avg_class_score_pct ? `${stats.avg_class_score_pct}%` : "—"}
                        subtitle="Across graded questions"
                        onClick={() => navigate("/uploads")}
                        accent="orange"
                    />
                </div>

                <div className="card-lg">
                    <h2 className="text-xl font-bold text-slate-800 mb-4">Recent Uploads</h2>
                    {stats.recent_uploads?.length === 0 ? (
                        <p className="text-muted text-sm">
                            No uploads yet. Upload an exam PDF to start the Tribunal pipeline.
                        </p>
                    ) : (
                        <div className="flex flex-col gap-3">
                            {stats.recent_uploads.map((item) => (
                                <div
                                    key={item.upload_id}
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => navigate(`/uploads/${item.upload_id}`)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") navigate(`/uploads/${item.upload_id}`);
                                    }}
                                    className="list-item"
                                >
                                    <div className="w-11 h-11 bg-gradient-to-br from-teal-100 to-violet-100 rounded-xl flex items-center justify-center text-teal-600 shrink-0">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                        </svg>
                                    </div>
                                    <div>
                                        <p className="font-semibold text-slate-800">{item.filename}</p>
                                        <p className="text-xs text-muted mt-0.5">
                                            {item.status} ·{" "}
                                            {item.created_at
                                                ? new Date(item.created_at).toLocaleString()
                                                : "—"}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
