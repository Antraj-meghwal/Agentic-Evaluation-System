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
        <div className="auth-bg">
            <div className="auth-blob-teal top-0 right-10" />
            <div className="auth-blob-violet bottom-0 left-10" />

            <div className="card-auth relative z-10">
                <h1 className="text-3xl font-extrabold heading-gradient mb-2">Create account</h1>
                <p className="text-muted text-sm mb-8">
                    Instructors upload exams; TAs review AI grades in the queue.
                </p>

                <form onSubmit={handleRegister} className="space-y-5">
                    <div className="space-y-1.5">
                        <label className="label-text">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <div className="space-y-1.5">
                        <label className="label-text">Password</label>
                        <input
                            type="password"
                            required
                            minLength={6}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <div className="space-y-1.5">
                        <label className="label-text">Role</label>
                        <select
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            className="input-field"
                        >
                            <option value="instructor">Instructor (upload &amp; grade)</option>
                            <option value="professor">Professor (upload &amp; grade)</option>
                            <option value="ta">Teaching Assistant (review queue)</option>
                        </select>
                    </div>

                    {error && <div className="alert-error">{error}</div>}
                    {message && <p className="alert-success">{message}</p>}

                    <button type="submit" disabled={loading} className="btn-primary-full">
                        {loading ? "Creating…" : "Create Account"}
                    </button>
                </form>

                <p className="text-center text-slate-500 text-sm mt-6">
                    Already have an account?{" "}
                    <Link to="/" className="font-semibold text-violet-600 hover:underline">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}
