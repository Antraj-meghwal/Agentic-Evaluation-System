import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
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
                        <ProtectedRoute allowedRoles={["admin", "professor"]}>
                            <UploadPage />
                        </ProtectedRoute>
                    }
                />

                {/* Professors and TAs can view uploads and details */}
                <Route
                    path="/uploads"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "ta"]}>
                            <UploadsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/uploads/:id"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "ta"]}>
                            <UploadDetailsPage />
                        </ProtectedRoute>
                    }
                />

                {/* Professors and TAs can access the review queue */}
                <Route
                    path="/review"
                    element={
                        <ProtectedRoute allowedRoles={["admin", "professor", "ta"]}>
                            <ReviewPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}
