import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import API from "../services/api";

export default function StudentDashboard() {
    const [data, setData] = useState({
        assignments_graded: 0,
        total_questions_graded: 0,
        avg_score_pct: 0,
        pending_count: 0,
        results: [],
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const res = await API.get("/api/dashboard/student");
                if (!res.data.error) {
                    setData(res.data);
                }
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
                <div className="flex items-center justify-between mb-12">
                    <div>
                        <h1 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">
                            Student Portal
                        </h1>
                        <p className="text-slate-400">View your graded assignments and AI feedback.</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-10">
                    <StatCard
                        title="Average Score"
                        value={loading ? "…" : data.avg_score_pct ? `${data.avg_score_pct}%` : "—"}
                        subtitle="Across graded questions"
                    />
                    <StatCard
                        title="Questions Graded"
                        value={loading ? "…" : data.total_questions_graded}
                        subtitle="With AI feedback"
                    />
                    <StatCard
                        title="Pending Review"
                        value={loading ? "…" : data.pending_count}
                        subtitle="Awaiting TA approval"
                    />
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h2 className="text-2xl font-semibold mb-6">Your Results</h2>
                    {loading ? (
                        <p className="text-slate-500">Loading…</p>
                    ) : data.results.length === 0 ? (
                        <p className="text-slate-500 text-sm">
                            No graded work linked to your account yet. Grades appear when your
                            instructor assigns submissions using your email as the student ID.
                        </p>
                    ) : (
                        <div className="space-y-4">
                            {data.results.map((item) => (
                                <div
                                    key={`${item.submission_id}-${item.question_id}`}
                                    className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-slate-800/50"
                                >
                                    <div>
                                        <h3 className="text-lg font-medium text-white">
                                            Question {item.question_id}
                                        </h3>
                                        <p className="text-sm text-slate-400 mt-1">
                                            {item.feedback || "No feedback yet."}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-2xl font-bold text-emerald-400">
                                            {item.score}/{item.max_score}
                                        </p>
                                        {item.requires_human_review && (
                                            <p className="text-xs text-amber-400 mt-1">Under review</p>
                                        )}
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
