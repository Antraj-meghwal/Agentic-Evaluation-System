import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

// Helper to decode JWT without external libraries
function decodeJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [role, setRole] = useState(localStorage.getItem("role") || null);
    const [isAuthenticated, setIsAuthenticated] = useState(!!token);

    function login(jwtToken) {
        const decoded = decodeJwt(jwtToken);
        // Backend may use "instructor"; UI routes use "professor"
        const rawRole = decoded?.role || "student";
        const userRole = rawRole === "instructor" ? "professor" : rawRole;
        
        localStorage.setItem("token", jwtToken);
        localStorage.setItem("role", userRole);
        setToken(jwtToken);
        setRole(userRole);
        setIsAuthenticated(true);
    }

    function logout() {
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        setToken(null);
        setRole(null);
        setIsAuthenticated(false);
    }

    useEffect(() => {
        const storedToken = localStorage.getItem("token");
        if (storedToken) {
            setIsAuthenticated(true);
            const decoded = decodeJwt(storedToken);
            if (decoded && decoded.role) {
                const normalized =
                    decoded.role === "instructor" ? "professor" : decoded.role;
                setRole(normalized);
                localStorage.setItem("role", normalized);
            }
        }
    }, []);

    return (
        <AuthContext.Provider value={{ token, role, login, logout, isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}