import {

    useEffect,

    useState

} from "react"

import {

    useParams

} from "react-router-dom"

import Navbar from "../components/Navbar"

import API from "../services/api"

import StatusBadge from "../components/StatusBadge"


export default function UploadDetailsPage() {

    const { id } = useParams()

    const [upload, setUpload]
        = useState(null)

    const [loading, setLoading]
        = useState(true)

    const [grading, setGrading]
        = useState(false)

    const [gradingResult, setGradingResult]
        = useState(null)


    async function fetchUpload() {

        try {

            const response =
                await API.get("/uploads")

            const foundUpload =
                response.data.find(

                    (item) =>
                        item.id === Number(id)
                )

            setUpload(foundUpload)

        } catch (error) {

            console.log(error)

        } finally {

            setLoading(false)
        }
    }


    async function handleGrading() {

        try {

            setGrading(true)

            const response =
                await API.post(
                    `/grading/grade/${id}`
                )

            setGradingResult(
                response.data
            )

        } catch (error) {

            console.log(error)

        } finally {

            setGrading(false)
        }
    }


    useEffect(() => {

        fetchUpload()

    }, [])


    if (loading) {

        return (

            <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">

                Loading...

            </div>
        )
    }


    if (!upload) {

        return (

            <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">

                Upload not found

            </div>
        )
    }


    return (

        <div className="min-h-screen bg-slate-950 text-white">

            <Navbar />

            <div className="p-10 max-w-6xl mx-auto">

                <h1 className="text-5xl font-bold mb-10">

                    Upload Details

                </h1>

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">

                    <h2 className="text-3xl font-semibold">

                        {upload.filename}

                    </h2>

                    <div className="mt-5">

                        <StatusBadge
                            status={upload.status}
                        />

                    </div>

                    <p className="mt-5 text-slate-500">

                        Uploaded:
                        {" "}
                        {new Date(
                            upload.created_at
                        ).toLocaleString()}

                    </p>

                    <a
                        href={upload.file_url}
                        target="_blank"
                        className="inline-block mt-6 text-blue-400 hover:underline"
                    >

                        Open File

                    </a>

                    <div className="mt-10">

                        <button
                            onClick={handleGrading}
                            disabled={grading}
                            className="bg-blue-600 hover:bg-blue-700 px-6 py-4 rounded-2xl font-semibold transition-all"
                        >

                            {grading
                                ? "Running AI Grading..."
                                : "Start AI Grading"}

                        </button>

                    </div>

                    {gradingResult && (

                        <div className="mt-10 bg-slate-800 border border-slate-700 rounded-2xl p-6">

                            <h2 className="text-3xl font-bold mb-6">

                                AI Grading Result

                            </h2>

                            <pre className="whitespace-pre-wrap text-slate-300 overflow-auto">

                                {JSON.stringify(

                                    gradingResult,

                                    null,

                                    2
                                )}

                            </pre>

                        </div>
                    )}

                </div>

            </div>

        </div>
    )
}
