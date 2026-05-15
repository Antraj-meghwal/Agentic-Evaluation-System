import {

    useNavigate

} from "react-router-dom"

import {

    useAuth

} from "../context/AuthContext"


export default function Navbar() {

    const navigate = useNavigate()

    const { logout } = useAuth()


    function handleLogout() {

        logout()

        navigate("/")
    }


    return (

        <nav className="w-full bg-slate-900 border-b border-slate-800 px-10 py-5 flex items-center justify-between">

            <h1 className="text-3xl font-bold text-white">

                GRADEOPS

            </h1>

            <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 px-5 py-2 rounded-xl text-white font-semibold transition-all"
            >

                Logout

            </button>

        </nav>
    )
}