import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import API from "../services/api";

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [uploadCount, setUploadCount] = useState(0);

    const [pendingReviews, setPendingReviews] = useState(0);

    useEffect(() => {
        async function fetchData() {
            try {
                const [uploadsRes, statsRes] = await Promise.all([
                    API.get("/uploads"),
                    API.get("/api/review/stats"),
                ]);
                setUploadCount(uploadsRes.data.length);
                setPendingReviews(statsRes.data.pending_reviews);
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
                        onClick={() => navigate("/upload")}
                        className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded-xl font-medium transition-all shadow-lg shadow-indigo-500/30 flex items-center gap-2"
                    >
                        <span>+ New Upload</span>
                    </button>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-10">
                    <StatCard
                        title="Total Uploads"
                        value={uploadCount}
                        subtitle="Answer sheets processed"
                        onClick={() => navigate("/uploads")}
                    />
                    <StatCard
                        title="Pending Reviews"
                        value={pendingReviews}
                        subtitle="Requires human validation"
                        onClick={() => navigate("/review")}
                    />
                    <StatCard
                        title="Avg. Class Score"
                        value="78%"
                        subtitle="Based on latest grading"
                        onClick={() => {}}
                    />
                </div>
                
                {/* Advanced functionality section for future */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h2 className="text-2xl font-semibold mb-4">Recent Activity</h2>
                    <div className="text-slate-500 text-sm flex flex-col gap-4">
                        <div className="flex items-center gap-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800/50">
                            <div className="w-10 h-10 bg-indigo-500/20 rounded-full flex items-center justify-center text-indigo-400">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            </div>
                            <div>
                                <p className="text-white font-medium">Batch CS101 Midterms Processed</p>
                                <p className="text-xs">2 hours ago • 45 papers graded by AI</p>
                            </div>
                        </div>
                        {/* More mock activity items can be added here */}
                        <div className="flex items-center gap-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800/50">
                            <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center text-blue-400">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                            </div>
                            <div>
                                <p className="text-white font-medium">New Rubric Uploaded: Math 202</p>
                                <p className="text-xs">Yesterday • Uploaded by Prof. Smith</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
