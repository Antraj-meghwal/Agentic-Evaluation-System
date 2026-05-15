# FastAPI core
from fastapi import FastAPI

# Static file serving
from fastapi.staticfiles import StaticFiles

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# Database setup
from database import engine
from database import Base

# Import routes
from routes.upload_routes import router as upload_router


# Create DB tables
Base.metadata.create_all(bind=engine)


# Create app
app = FastAPI()


# Enable CORS
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# Serve uploads folder
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# Register upload routes
app.include_router(upload_router)


# Home route
@app.get("/")
def home():

    return {

        "message": "GradeOps Backend Running"
    }