import { useState } from "react"
import { useNavigate } from "react-router-dom"

import Navbar from "../components/Navbar"

import API from "../services/api"


export default function UploadPage() {

    const navigate = useNavigate()
    const [file, setFile] = useState(null)

    const [message, setMessage] = useState("")

    const [loading, setLoading] = useState(false)


    async function handleUpload(e) {

        e.preventDefault()

        if (!file) {

            setMessage("Please select a file")

            return
        }

        try {

            setLoading(true)

            const formData = new FormData()

            formData.append("file", file)

            const response = await API.post(

                "/upload",

                formData,

                {
                    headers: {

                        "Content-Type":
                            "multipart/form-data"
                    }
                }
            )

            setMessage(
                "File uploaded successfully"
            )

            if (response.data?.id) {
                navigate(`/uploads/${response.data.id}`)
            }

        } catch {

            setMessage("Upload failed")

        } finally {

            setLoading(false)
        }
    }


    return (

        <div className="min-h-screen bg-slate-950 text-white">

            <Navbar />

            <div className="max-w-3xl mx-auto pt-20 px-5">

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl">

                    <h1 className="text-5xl font-bold mb-10">

                        Upload Answer Sheets

                    </h1>

                    <form
                        onSubmit={handleUpload}
                        className="space-y-8"
                    >

                        <input
                            type="file"
                            onChange={(e) =>
                                setFile(
                                    e.target.files[0]
                                )
                            }
                            className="w-full p-5 rounded-2xl bg-slate-800 border border-slate-700"
                        />

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 p-5 rounded-2xl font-semibold text-lg transition-all"
                        >

                            {loading
                                ? "Uploading..."
                                : "Upload File"}

                        </button>

                    </form>

                    {message && (

                        <p className="mt-8 text-lg text-center">

                            {message}

                        </p>
                    )}

                </div>

            </div>

        </div>
    )
}
