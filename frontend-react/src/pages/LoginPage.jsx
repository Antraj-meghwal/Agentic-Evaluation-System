import { useState } from "react"

import { useNavigate } from "react-router-dom"

import API from "../services/api"


export default function LoginPage() {

    const navigate = useNavigate()

    const [email, setEmail] = useState("")

    const [password, setPassword] = useState("")

    const [loading, setLoading] = useState(false)

    const [error, setError] = useState("")


    // -----------------------------------
    // Handle login
    // -----------------------------------
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

            // Save JWT token
            localStorage.setItem(

                "token",

                response.data.access_token
            )

            // Redirect
            navigate("/dashboard")

        } catch (err) {

            setError(
                "Invalid credentials"
            )

        } finally {

            setLoading(false)
        }
    }


    return (

        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">

            <div className="bg-slate-900 p-10 rounded-2xl w-[400px] shadow-2xl border border-slate-800">

                <h1 className="text-4xl font-bold mb-8 text-center">

                    GRADEOPS

                </h1>

                <form
                    onSubmit={handleLogin}
                    className="space-y-5"
                >

                    <div>

                        <label className="block mb-2 text-sm text-slate-400">

                            Email

                        </label>

                        <input
                            type="email"
                            placeholder="Enter email"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                            className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none"
                        />

                    </div>

                    <div>

                        <label className="block mb-2 text-sm text-slate-400">

                            Password

                        </label>

                        <input
                            type="password"
                            placeholder="Enter password"
                            value={password}
                            onChange={(e) =>
                                setPassword(e.target.value)
                            }
                            className="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none"
                        />

                    </div>

                    {error && (

                        <p className="text-red-400 text-sm">

                            {error}

                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 transition-all p-3 rounded-xl font-semibold"
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