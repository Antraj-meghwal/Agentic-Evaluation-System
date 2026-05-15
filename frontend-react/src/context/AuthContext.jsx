import {

    createContext,

    useContext,

    useEffect,

    useState

} from "react"


const AuthContext = createContext()


export function AuthProvider({ children }) {

    const [token, setToken] = useState(

        localStorage.getItem("token")
    )


    const [isAuthenticated, setIsAuthenticated]
        = useState(!!token)


    function login(jwtToken) {

        localStorage.setItem(
            "token",
            jwtToken
        )

        setToken(jwtToken)

        setIsAuthenticated(true)
    }


    function logout() {

        localStorage.removeItem("token")

        setToken(null)

        setIsAuthenticated(false)
    }


    useEffect(() => {

        const storedToken =
            localStorage.getItem("token")

        if (storedToken) {

            setIsAuthenticated(true)
        }

    }, [])


    return (

        <AuthContext.Provider
            value={{

                token,

                login,

                logout,

                isAuthenticated
            }}
        >

            {children}

        </AuthContext.Provider>
    )
}


export function useAuth() {

    return useContext(AuthContext)
}