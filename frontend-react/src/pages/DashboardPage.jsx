import { useAuth } from "../context/AuthContext";
import AdminDashboard from "./AdminDashboard";
import StudentDashboard from "./StudentDashboard";
import TADashboard from "./TADashboard";

export default function DashboardPage() {
    const { role } = useAuth();

    // Securely route based on role stored in JWT context
    if (role === "student") {
        return <StudentDashboard />;
    }
    
    if (role === "ta") {
        return <TADashboard />;
    }

    // professor, instructor, or admin
    if (role === "professor" || role === "instructor" || role === "admin") {
        return <AdminDashboard />;
    }

    return <StudentDashboard />;
}
