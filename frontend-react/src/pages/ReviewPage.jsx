import Navbar from "../components/Navbar"


export default function ReviewPage() {

    return (

        <div className="min-h-screen bg-slate-950 text-white">

            <Navbar />

            <div className="p-10">

                <h1 className="text-5xl font-bold mb-6">

                    Human Review Queue

                </h1>

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-10">

                    <p className="text-slate-400 text-lg">

                        Reviewer workflow coming next.

                    </p>

                </div>

            </div>

        </div>
    )
}
