import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import UploadsPage from "./pages/UploadsPage";
import UploadDetailsPage from "./pages/UploadDetailsPage";
import ReviewPage from "./pages/ReviewPage";
import ProtectedRoute from "./routes/ProtectedRoute";

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Dashboard routes intelligently based on role */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />

                {/* Strict Role Guarding: Only Professor/Admin can upload */}
                <Route
                    path="/upload"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "instructor"]}>
                            <UploadPage />
                        </ProtectedRoute>
                    }
                />

                {/* Professors and TAs can view uploads and details */}
                <Route
                    path="/uploads"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "instructor", "ta"]}>
                            <UploadsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/uploads/:id"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "instructor", "ta"]}>
                            <UploadDetailsPage />
                        </ProtectedRoute>
                    }
                />

                {/* Professors and TAs can access the review queue */}
                <Route
                    path="/review"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "instructor", "ta"]}>
                            <ReviewPage />
                        </ProtectedRoute>
                    }
                />

                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
