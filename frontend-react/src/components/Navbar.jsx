import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
    const navigate = useNavigate();
    const { logout, role } = useAuth();

    function handleLogout() {
        logout();
        navigate("/");
    }

    return (
        <nav className="sticky top-0 z-50 w-full bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50 px-10 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer group" onClick={() => navigate("/dashboard")}>
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
                </div>
                <h1 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500 tracking-tight">
                    GRADEOPS
                </h1>
            </div>
            
            <div className="flex items-center gap-6">
                <div className="hidden md:flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.8)]"></div>
                    <span className="text-sm font-medium text-slate-300 capitalize">{role || "Admin"} Portal</span>
                </div>
                <div className="h-6 w-px bg-slate-800 hidden md:block"></div>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 bg-slate-900 hover:bg-red-500/10 border border-slate-800 hover:border-red-500/50 hover:text-red-400 px-4 py-2 rounded-xl text-slate-300 font-medium transition-all group"
                >
                    <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                    Logout
                </button>
            </div>
        </nav>
    );
}