# FastAPI core
from fastapi import FastAPI

# Static file serving
from fastapi.staticfiles import StaticFiles

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# Database setup
from database import engine
from database import Base

# Import models
from models.user_model import User
from models.upload_model import UploadedFile

# Create database tables
Base.metadata.create_all(bind=engine)

# Import routes
from routes.upload_routes import router as upload_router

from routes.grading_routes import (
    router as grading_router
)

from api.routes.grading_routes import (
    router as grading_router
)
from api.routes.status_routes import (
    router as status_router
)

from api.routes.review_routes import (
    router as review_router
)
# Create app
app = FastAPI()
app.include_router(
    grading_router,
    prefix="/grading",
    tags=["grading"]
)
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

app.include_router(
    status_router,
    prefix="/status",
    tags=["status"]
)

app.include_router(
    review_router,
    prefix="/review",
    tags=["review"]
)
# Home route
@app.get("/")
def home():

    return {

        "message": "GradeOps Backend Running"
    }



#import
from routes.user_routes import (
    router as user_router
)
app.include_router(user_router)






@app.get("/test-db")
def test_db():

    return {
        "message": "DB working"
    }