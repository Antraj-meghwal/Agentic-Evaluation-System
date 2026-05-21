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
        <div className="page-bg">
            <Navbar />
            <div className="max-w-7xl mx-auto p-6 md:p-10">
                <div className="mb-10">
                    <h1 className="text-3xl md:text-4xl font-extrabold heading-gradient-cool mb-2">
                        Student Portal
                    </h1>
                    <p className="text-muted">View your graded assignments and AI feedback.</p>
                </div>

                <div className="grid md:grid-cols-3 gap-5 mb-10">
                    <StatCard
                        title="Average Score"
                        value={loading ? "…" : data.avg_score_pct ? `${data.avg_score_pct}%` : "—"}
                        subtitle="Across graded questions"
                        accent="teal"
                    />
                    <StatCard
                        title="Questions Graded"
                        value={loading ? "…" : data.total_questions_graded}
                        subtitle="With AI feedback"
                        accent="violet"
                    />
                    <StatCard
                        title="Pending Review"
                        value={loading ? "…" : data.pending_count}
                        subtitle="Awaiting TA approval"
                        accent="orange"
                    />
                </div>

                <div className="card-lg">
                    <h2 className="text-xl font-bold text-slate-800 mb-6">Your Results</h2>
                    {loading ? (
                        <p className="text-muted">Loading…</p>
                    ) : data.results.length === 0 ? (
                        <p className="text-muted text-sm">
                            No graded work linked to your account yet. Grades appear when your
                            instructor assigns submissions using your email as the student ID.
                        </p>
                    ) : (
                        <div className="space-y-3">
                            {data.results.map((item) => (
                                <div
                                    key={`${item.submission_id}-${item.question_id}`}
                                    className="flex items-center justify-between p-5 bg-slate-50 rounded-xl border border-slate-100"
                                >
                                    <div>
                                        <h3 className="text-lg font-semibold text-slate-800">
                                            Question {item.question_id}
                                        </h3>
                                        <p className="text-sm text-muted mt-1">
                                            {item.feedback || "No feedback yet."}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-2xl font-extrabold text-teal-600">
                                            {item.score}/{item.max_score}
                                        </p>
                                        {item.requires_human_review && (
                                            <p className="text-xs font-semibold text-amber-600 mt-1">
                                                Under review
                                            </p>
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
