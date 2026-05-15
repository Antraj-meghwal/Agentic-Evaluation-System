import {

    Navigate

} from "react-router-dom"

import {

    useAuth

} from "../context/AuthContext"


export default function ProtectedRoute({

    children
}) {

    const {

        isAuthenticated

    } = useAuth()


    // Not logged in
    if (!isAuthenticated) {

        return <Navigate to="/" />
    }

    // Logged in
    return children
}