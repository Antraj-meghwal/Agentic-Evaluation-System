# FastAPI core
from fastapi import FastAPI

# Static file serving
from fastapi.staticfiles import StaticFiles

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# Database setup
from database import engine
from database import Base

# Import models (legacy + tribunal schemas use separate declarative bases)
from models.user_model import User  # noqa: F401
from models.upload_model import UploadedFile  # noqa: F401
import models  # noqa: F401 — batch, submission, question_crop, grading_result, review_action

from db.base import Base as TribunalBase

# Create database tables for both metadata registries on the same engine
Base.metadata.create_all(bind=engine)
TribunalBase.metadata.create_all(bind=engine)

# Import routes
from routes.upload_routes import router as upload_router

from routes.grading_routes import router as grading_router
from routes.user_routes import router as user_router

# Import new API routes
from api.routes.auth_routes import (
    router as auth_api_router
)
from api.routes.batch_routes import (
    router as batch_api_router
)
from api.routes.review_routes import (
    router as review_api_router
)


# Create app
app = FastAPI(
    title="GradeOps API",
    description="AI-Assisted Academic Evaluation System",
    version="1.0.0"
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


# Register legacy routes
app.include_router(upload_router)
app.include_router(user_router)
app.include_router(
    grading_router,
    prefix="/grading",
    tags=["grading"]
)

# Register new API routes
app.include_router(
    auth_api_router,
    prefix="/api/auth",
    tags=["auth"]
)
app.include_router(
    batch_api_router,
    prefix="/api/batches",
    tags=["batches"]
)
app.include_router(
    review_api_router,
    prefix="/api/review",
    tags=["review"]
)


# Home route
@app.get("/")
def home():

    return {

        "message": "GradeOps Backend Running"
    }


@app.get("/test-db")
def test_db():

    return {
        "message": "DB working"
    }