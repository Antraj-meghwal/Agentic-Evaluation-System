import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowedRoles }) {
    const { isAuthenticated, role } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/" />;
    }

    // Check if the route restricts access by role
    const effectiveRole = role === "instructor" ? "professor" : role;
    if (allowedRoles && !allowedRoles.includes(effectiveRole) && !allowedRoles.includes(role)) {
        // If user doesn't have the right role, bounce them to their specific dashboard
        return <Navigate to="/dashboard" />;
    }

    return children;
}