import Navbar from "../components/Navbar"
export default function DashboardPage() {

return (

    <div className="min-h-screen bg-slate-950 text-white">

        <Navbar />

        <div className="p-10">

            <h1 className="text-5xl font-bold mb-10">

                Dashboard

            </h1>

            <div className="grid grid-cols-3 gap-6">

                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">

                    <h2 className="text-2xl font-semibold">

                        Uploads

                    </h2>

                    <p className="text-slate-400 mt-2">

                        Track uploaded answer sheets.

                    </p>

                </div>

                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">

                    <h2 className="text-2xl font-semibold">

                        AI Grading

                    </h2>

                    <p className="text-slate-400 mt-2">

                        Monitor grading pipeline.

                    </p>

                </div>

                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">

                    <h2 className="text-2xl font-semibold">

                        Reviews

                    </h2>

                    <p className="text-slate-400 mt-2">

                        Human-in-the-loop approvals.

                    </p>

                </div>

            </div>

        </div>

    </div>
)
}