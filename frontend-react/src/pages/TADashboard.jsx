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
        <div className="page-bg">
            <Navbar />
            <div className="max-w-7xl mx-auto p-6 md:p-10">
                <div className="mb-10">
                    <h1 className="text-3xl md:text-4xl font-extrabold heading-gradient-warm mb-2">
                        TA Dashboard
                    </h1>
                    <p className="text-muted">
                        Review AI evaluations and provide human verification.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-5 mb-10">
                    <StatCard
                        title="Pending Reviews"
                        value={loading ? "…" : stats.pending_reviews}
                        subtitle="Papers requiring validation"
                        onClick={() => navigate("/review")}
                        accent="orange"
                    />
                    <StatCard
                        title="Total Graded"
                        value={loading ? "…" : stats.total_graded}
                        subtitle="Tribunal results in DB"
                        onClick={() => navigate("/uploads")}
                        accent="teal"
                    />
                    <StatCard
                        title="Low Confidence"
                        value={loading ? "…" : stats.low_confidence}
                        subtitle="Below 60% confidence"
                        onClick={() => navigate("/review")}
                        accent="violet"
                    />
                </div>

                <div className="card-lg">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-slate-800">Review Queue</h2>
                        <button
                            type="button"
                            onClick={() => navigate("/review")}
                            className="btn-ghost text-orange-600 hover:bg-orange-50 hover:text-orange-700"
                        >
                            Open full queue →
                        </button>
                    </div>

                    {loading ? (
                        <p className="text-muted">Loading…</p>
                    ) : queue.length === 0 ? (
                        <p className="text-muted">
                            No pending reviews. Professors can run Tribunal grading from upload
                            details.
                        </p>
                    ) : (
                        <div className="space-y-3">
                            {queue.map((item) => (
                                <div
                                    key={item.grading_result_id}
                                    className="flex items-center justify-between p-5 bg-orange-50/50 rounded-xl border border-orange-100 hover:border-orange-300 hover:shadow-md transition-all cursor-pointer"
                                    onClick={() => navigate("/review")}
                                >
                                    <div>
                                        <h3 className="text-lg font-semibold text-slate-800">
                                            Upload #{item.upload_id} · Q{item.question_id}
                                        </h3>
                                        <p className="text-sm text-muted">
                                            Score {item.score}/{item.max_score} · conf{" "}
                                            {((item.confidence || 0) * 100).toFixed(0)}%
                                            {item.escalation_reasons?.length > 0 &&
                                                ` · ${item.escalation_reasons[0]}`}
                                        </p>
                                    </div>
                                    <button type="button" className="btn-warning btn-sm">
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
