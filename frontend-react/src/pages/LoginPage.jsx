import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleLogin(e) {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const response = await API.post("/login", { email, password });
            login(response.data.access_token);
            navigate("/dashboard");
        } catch {
            setError("Invalid credentials. Please check your email and password.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="auth-bg">
            <div className="auth-blob-teal top-0 -left-10" />
            <div className="auth-blob-violet top-10 -right-10" />
            <div className="auth-blob-coral -bottom-10 left-1/4" />

            <div className="card-auth">
                <div className="text-center mb-8">
                    <div className="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500 to-violet-500 items-center justify-center mb-4 shadow-lg shadow-teal-500/30">
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <h1 className="text-4xl font-extrabold heading-gradient mb-2">GRADEOPS</h1>
                    <p className="text-slate-500 text-sm font-medium tracking-wide">
                        AI-Assisted Academic Evaluation
                    </p>
                </div>

                <form onSubmit={handleLogin} className="space-y-5">
                    <div className="space-y-1.5">
                        <label className="label-text">Email</label>
                        <input
                            type="email"
                            placeholder="user@university.edu"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input-field"
                        />
                    </div>

                    <div className="space-y-1.5">
                        <label className="label-text">Password</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                        />
                    </div>

                    {error && <div className="alert-error">{error}</div>}

                    <button type="submit" disabled={loading} className="btn-primary-full">
                        {loading ? (
                            <span className="flex items-center justify-center">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Authenticating...
                            </span>
                        ) : (
                            "Sign In"
                        )}
                    </button>
                </form>

                <p className="text-center text-slate-500 text-sm mt-6">
                    New user?{" "}
                    <Link to="/register" className="font-semibold text-violet-600 hover:text-violet-700 hover:underline">
                        Register as Instructor or TA
                    </Link>
                </p>
            </div>
        </div>
    );
}
