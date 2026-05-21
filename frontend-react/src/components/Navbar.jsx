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
        <nav className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-xl border-b border-slate-200/80 px-6 md:px-10 py-3.5 flex items-center justify-between shadow-sm">
            <div
                className="flex items-center gap-3 cursor-pointer group"
                onClick={() => navigate("/dashboard")}
            >
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 via-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 group-hover:scale-105 transition-all">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                    </svg>
                </div>
                <h1 className="text-xl font-extrabold heading-gradient tracking-tight">GRADEOPS</h1>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
                {["ta", "professor", "instructor", "admin"].includes(role) && (
                    <button type="button" onClick={() => navigate("/review")} className="nav-link">
                        Review queue
                    </button>
                )}
                {["professor", "instructor", "admin"].includes(role) && (
                    <button type="button" onClick={() => navigate("/upload")} className="nav-link">
                        Upload
                    </button>
                )}
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-semibold text-emerald-700 capitalize">
                        {role || "Admin"} Portal
                    </span>
                </div>
                <div className="h-6 w-px bg-slate-200 hidden md:block" />
                <button onClick={handleLogout} className="btn-danger-ghost btn-sm">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                </button>
            </div>
        </nav>
    );
}
