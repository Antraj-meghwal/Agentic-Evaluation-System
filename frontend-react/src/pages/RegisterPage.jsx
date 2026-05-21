import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../services/api";

export default function RegisterPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("instructor");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    async function handleRegister(e) {
        e.preventDefault();
        setLoading(true);
        setError("");
        setMessage("");
        try {
            await API.post("/register", { email, password, role });
            setMessage("Account created. Sign in to continue.");
            setTimeout(() => navigate("/"), 1500);
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-5">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-10 w-full max-w-lg">
                <h1 className="text-3xl font-bold mb-2">Create account</h1>
                <p className="text-slate-400 text-sm mb-8">
                    Instructors upload exams; TAs review AI grades in the queue.
                </p>

                <form onSubmit={handleRegister} className="space-y-5">
                    <div>
                        <label className="text-sm text-slate-400">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full mt-1 p-3 rounded-xl bg-slate-950 border border-slate-700"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-slate-400">Password</label>
                        <input
                            type="password"
                            required
                            minLength={6}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full mt-1 p-3 rounded-xl bg-slate-950 border border-slate-700"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-slate-400">Role</label>
                        <select
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            className="w-full mt-1 p-3 rounded-xl bg-slate-950 border border-slate-700"
                        >
                            <option value="instructor">Instructor (upload &amp; grade)</option>
                            <option value="professor">Professor (upload &amp; grade)</option>
                            <option value="ta">Teaching Assistant (review queue)</option>
                        </select>
                    </div>

                    {error && <p className="text-red-400 text-sm">{error}</p>}
                    {message && <p className="text-emerald-400 text-sm">{message}</p>}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl font-semibold disabled:opacity-50"
                    >
                        {loading ? "Creating…" : "Register"}
                    </button>
                </form>

                <p className="text-center text-slate-500 text-sm mt-6">
                    Already have an account?{" "}
                    <Link to="/" className="text-indigo-400 hover:underline">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}
