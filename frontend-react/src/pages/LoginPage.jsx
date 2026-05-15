import { useState } from "react"

import { useNavigate } from "react-router-dom"

import API from "../services/api"

import { useAuth } from "../context/AuthContext"


export default function LoginPage() {

    const navigate = useNavigate()

    const { login } = useAuth()


    const [email, setEmail] = useState("")

    const [password, setPassword] = useState("")

    const [loading, setLoading] = useState(false)

    const [error, setError] = useState("")


    async function handleLogin(e) {

        e.preventDefault()

        setLoading(true)

        setError("")

        try {

            const response = await API.post(

                "/login",

                {

                    email,

                    password
                }
            )

            login(response.data.access_token)

            navigate("/dashboard")

        } catch {

            setError("Invalid credentials")

        } finally {

            setLoading(false)
        }
    }


    return (

        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-5">

            <div className="bg-slate-900 p-10 rounded-3xl w-full max-w-md border border-slate-800 shadow-2xl">

                <h1 className="text-5xl font-bold text-center mb-3">

                    GRADEOPS

                </h1>

                <p className="text-slate-400 text-center mb-10">

                    AI-Assisted Academic Evaluation

                </p>

                <form
                    onSubmit={handleLogin}
                    className="space-y-5"
                >

                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) =>
                            setEmail(e.target.value)
                        }
                        className="w-full p-4 rounded-xl bg-slate-800 border border-slate-700 outline-none"
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) =>
                            setPassword(e.target.value)
                        }
                        className="w-full p-4 rounded-xl bg-slate-800 border border-slate-700 outline-none"
                    />

                    {error && (

                        <p className="text-red-400">

                            {error}

                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded-xl font-semibold transition-all"
                    >

                        {loading
                            ? "Logging in..."
                            : "Login"}

                    </button>

                </form>

            </div>

        </div>
    )
}
