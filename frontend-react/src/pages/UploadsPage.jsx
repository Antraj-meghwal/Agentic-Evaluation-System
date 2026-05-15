import {

    useEffect,

    useState

} from "react"

import {

    useNavigate

} from "react-router-dom"

import Navbar from "../components/Navbar"

import API from "../services/api"

import StatusBadge from "../components/StatusBadge"

import LoadingSpinner from "../components/LoadingSpinner"


export default function UploadsPage() {

    const navigate = useNavigate()

    const [uploads, setUploads]
        = useState([])

    const [loading, setLoading]
        = useState(true)


    async function fetchUploads() {

        try {

            const response =
                await API.get("/uploads")

            setUploads(response.data)

        } catch (error) {

            console.log(error)

        } finally {

            setLoading(false)
        }
    }


    useEffect(() => {

        fetchUploads()

    }, [])


    return (

        <div className="min-h-screen bg-slate-950 text-white">

            <Navbar />

            <div className="p-10">

                <h1 className="text-5xl font-bold mb-10">

                    My Uploads

                </h1>

                {loading ? (

                    <LoadingSpinner />

                ) : (

                    <div className="grid gap-6">

                        {uploads.map((upload) => (

                            <div

                                key={upload.id}

                                onClick={() =>
                                    navigate(`/uploads/${upload.id}`)
                                }

                                className="bg-slate-900 border border-slate-800 rounded-2xl p-6 cursor-pointer hover:border-blue-500 transition-all"
                            >

                                <h2 className="text-2xl font-semibold">

                                    {upload.filename}

                                </h2>

                                <div className="mt-4">

                                    <StatusBadge
                                        status={upload.status}
                                    />

                                </div>

                                <p className="text-slate-500 mt-4 text-sm">

                                    Uploaded:
                                    {" "}
                                    {new Date(
                                        upload.created_at
                                    ).toLocaleString()}

                                </p>

                            </div>
                        ))}

                    </div>
                )}

            </div>

        </div>
    )
}
