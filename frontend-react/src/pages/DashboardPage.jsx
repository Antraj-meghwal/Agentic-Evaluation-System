import {

    useEffect,

    useState

} from "react"

import {

    useNavigate

} from "react-router-dom"

import Navbar from "../components/Navbar"

import StatCard from "../components/StatCard"

import API from "../services/api"


export default function DashboardPage() {

    const navigate = useNavigate()

    const [uploadCount, setUploadCount]
        = useState(0)


    useEffect(() => {

        async function fetchUploads() {

            try {

                const response =
                    await API.get("/uploads")

                setUploadCount(
                    response.data.length
                )

            } catch (error) {

                console.log(error)
            }
        }

        fetchUploads()

    }, [])


    return (

        <div className="min-h-screen bg-slate-950 text-white">

            <Navbar />

            <div className="p-10">

                <h1 className="text-6xl font-bold mb-3">

                    Dashboard

                </h1>

                <p className="text-slate-400 text-lg mb-12">

                    AI Evaluation Workflow Overview

                </p>

                <div className="grid md:grid-cols-3 gap-6">

                    <StatCard
                        title="Uploads"
                        value={uploadCount}
                        subtitle="Uploaded answer sheets"
                        onClick={() =>
                            navigate("/uploads")
                        }
                    />

                    <StatCard
                        title="Upload"
                        value="+"
                        subtitle="Upload new answer sheets"
                        onClick={() =>
                            navigate("/upload")
                        }
                    />

                    <StatCard
                        title="Reviews"
                        value="0"
                        subtitle="Pending human reviews"
                        onClick={() =>
                            navigate("/review")
                        }
                    />

                </div>

            </div>

        </div>
    )
}
