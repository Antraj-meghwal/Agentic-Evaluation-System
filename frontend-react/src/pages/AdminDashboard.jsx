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
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="max-w-7xl mx-auto p-10">
                <div className="flex items-center justify-between mb-12">
                    <div>
                        <h1 className="text-4xl font-bold mb-2">Professor Dashboard</h1>
                        <p className="text-slate-400">Manage and review AI evaluations efficiently.</p>
                    </div>
                    <button
                        type="button"
                        onClick={() => navigate("/upload")}
                        className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded-xl font-medium transition-all shadow-lg shadow-indigo-500/30 flex items-center gap-2"
                    >
                        <span>+ New Upload</span>
                    </button>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-10">
                    <StatCard
                        title="Total Uploads"
                        value={stats.upload_count}
                        subtitle="Answer sheets processed"
                        onClick={() => navigate("/uploads")}
                    />
                    <StatCard
                        title="Pending Reviews"
                        value={stats.pending_reviews}
                        subtitle="Requires human validation"
                        onClick={() => navigate("/review")}
                    />
                    <StatCard
                        title="Avg. Class Score"
                        value={stats.avg_class_score_pct ? `${stats.avg_class_score_pct}%` : "—"}
                        subtitle="Across graded questions"
                        onClick={() => navigate("/uploads")}
                    />
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h2 className="text-2xl font-semibold mb-4">Recent Uploads</h2>
                    {stats.recent_uploads?.length === 0 ? (
                        <p className="text-slate-500 text-sm">
                            No uploads yet. Upload an exam PDF to start the Tribunal pipeline.
                        </p>
                    ) : (
                        <div className="text-slate-500 text-sm flex flex-col gap-4">
                            {stats.recent_uploads.map((item) => (
                                <div
                                    key={item.upload_id}
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => navigate(`/uploads/${item.upload_id}`)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") navigate(`/uploads/${item.upload_id}`);
                                    }}
                                    className="flex items-center gap-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800/50 cursor-pointer hover:border-indigo-500/50 transition-all"
                                >
                                    <div className="w-10 h-10 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                        </svg>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium">{item.filename}</p>
                                        <p className="text-xs">
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
