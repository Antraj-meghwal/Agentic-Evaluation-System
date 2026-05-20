import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import API from "../services/api";

export default function TADashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        pending_reviews: 0,
        total_graded: 0,
        overrides: 0,
        low_confidence: 0,
    });
    const [queue, setQueue] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const [statsRes, queueRes] = await Promise.all([
                    API.get("/api/review/stats"),
                    API.get("/api/review/review-queue"),
                ]);
                setStats(statsRes.data);
                setQueue(queueRes.data.slice(0, 5));
            } catch (e) {
                console.log(e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="max-w-7xl mx-auto p-10">
                <div className="mb-12">
                    <h1 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-500">
                        TA Dashboard
                    </h1>
                    <p className="text-slate-400">
                        Review AI evaluations and provide human verification.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-10">
                    <StatCard
                        title="Pending Reviews"
                        value={loading ? "…" : stats.pending_reviews}
                        subtitle="Papers requiring validation"
                        onClick={() => navigate("/review")}
                    />
                    <StatCard
                        title="Total Graded"
                        value={loading ? "…" : stats.total_graded}
                        subtitle="Tribunal results in DB"
                        onClick={() => navigate("/uploads")}
                    />
                    <StatCard
                        title="Low Confidence"
                        value={loading ? "…" : stats.low_confidence}
                        subtitle="Below 60% confidence"
                        onClick={() => navigate("/review")}
                    />
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-semibold">Review Queue</h2>
                        <button
                            type="button"
                            onClick={() => navigate("/review")}
                            className="text-orange-400 hover:text-orange-300 text-sm font-medium"
                        >
                            Open full queue →
                        </button>
                    </div>

                    {loading ? (
                        <p className="text-slate-500">Loading…</p>
                    ) : queue.length === 0 ? (
                        <p className="text-slate-500">
                            No pending reviews. Professors can run Tribunal grading from upload
                            details.
                        </p>
                    ) : (
                        <div className="space-y-4">
                            {queue.map((item) => (
                                <div
                                    key={item.grading_result_id}
                                    className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-orange-500/30 hover:border-orange-500/80 transition-all cursor-pointer"
                                    onClick={() => navigate("/review")}
                                >
                                    <div>
                                        <h3 className="text-lg font-medium">
                                            Upload #{item.upload_id} · Q{item.question_id}
                                        </h3>
                                        <p className="text-sm text-slate-400">
                                            Score {item.score}/{item.max_score} · conf{" "}
                                            {((item.confidence || 0) * 100).toFixed(0)}%
                                            {item.escalation_reasons?.length > 0 &&
                                                ` · ${item.escalation_reasons[0]}`}
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        className="bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 px-4 py-2 rounded-lg text-sm font-medium"
                                    >
                                        Review
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
