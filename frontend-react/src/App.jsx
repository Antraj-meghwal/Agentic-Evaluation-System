import {

    BrowserRouter,

    Routes,

    Route

} from "react-router-dom"


import LoginPage from "./pages/LoginPage"

import DashboardPage from "./pages/DashboardPage"

import UploadPage from "./pages/UploadPage"

import UploadsPage from "./pages/UploadsPage"

import UploadDetailsPage from "./pages/UploadDetailsPage"

import ReviewPage from "./pages/ReviewPage"

import ProtectedRoute from "./routes/ProtectedRoute"


export default function App() {

    return (

        <BrowserRouter>

            <Routes>

                <Route
                    path="/"
                    element={<LoginPage />}
                />

                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/upload"
                    element={
                        <ProtectedRoute>
                            <UploadPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/uploads"
                    element={
                        <ProtectedRoute>
                            <UploadsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/uploads/:id"
                    element={
                        <ProtectedRoute>
                            <UploadDetailsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/review"
                    element={
                        <ProtectedRoute>
                            <ReviewPage />
                        </ProtectedRoute>
                    }
                />

            </Routes>

        </BrowserRouter>
    )
}
