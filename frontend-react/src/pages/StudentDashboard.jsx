import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";

export default function StudentDashboard() {
    const navigate = useNavigate();

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
                        title="Total Scored"
                        value="85%"
                        subtitle="Across 4 assignments"
                        onClick={() => {}}
                    />
                    <StatCard
                        title="Assignments Graded"
                        value="4"
                        subtitle="All feedback available"
                        onClick={() => {}}
                    />
                    <StatCard
                        title="Pending"
                        value="1"
                        subtitle="Currently under AI review"
                        onClick={() => {}}
                    />
                </div>
                
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h2 className="text-2xl font-semibold mb-6">Recent Results</h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-slate-800/50 hover:border-emerald-500/50 transition-all cursor-pointer">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 font-bold text-xl">
                                    A
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">Computer Networks Midterm</h3>
                                    <p className="text-sm text-slate-400">Graded on Oct 12, 2023</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-bold text-emerald-400">92/100</p>
                                <button className="text-sm text-slate-400 hover:text-white underline mt-1">View AI Feedback</button>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-slate-800/50 hover:border-emerald-500/50 transition-all cursor-pointer">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-400 font-bold text-xl">
                                    B
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">Data Structures Quiz</h3>
                                    <p className="text-sm text-slate-400">Graded on Oct 5, 2023</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-bold text-blue-400">85/100</p>
                                <button className="text-sm text-slate-400 hover:text-white underline mt-1">View AI Feedback</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
