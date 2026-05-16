import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";

export default function TADashboard() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="max-w-7xl mx-auto p-10">
                <div className="flex items-center justify-between mb-12">
                    <div>
                        <h1 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-amber-500">
                            TA Dashboard
                        </h1>
                        <p className="text-slate-400">Review AI evaluations and provide human verification.</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-10">
                    <StatCard
                        title="Pending Reviews"
                        value="12"
                        subtitle="Papers requiring validation"
                        onClick={() => navigate("/review")}
                    />
                    <StatCard
                        title="Reviewed Today"
                        value="34"
                        subtitle="Validated by you"
                        onClick={() => {}}
                    />
                    <StatCard
                        title="Discrepancies"
                        value="3"
                        subtitle="AI vs Human mismatches"
                        onClick={() => {}}
                    />
                </div>
                
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
                    <h2 className="text-2xl font-semibold mb-6">Review Queue</h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-orange-500/30 hover:border-orange-500/80 transition-all cursor-pointer">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center text-orange-400 font-bold text-xl">
                                    !
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">Data Structures Midterm - Student ID: 4920</h3>
                                    <p className="text-sm text-slate-400">Flagged: Low confidence in Q3</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <button onClick={() => navigate("/review")} className="bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 px-4 py-2 rounded-lg text-sm font-medium transition-all">Review Now</button>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-5 bg-slate-950/50 rounded-xl border border-slate-800/50 hover:border-orange-500/50 transition-all cursor-pointer">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-slate-800 rounded-xl flex items-center justify-center text-slate-400 font-bold text-xl">
                                    ?
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">Computer Networks Quiz - Student ID: 1104</h3>
                                    <p className="text-sm text-slate-400">Standard Verification</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <button onClick={() => navigate("/review")} className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm font-medium transition-all">Start</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
