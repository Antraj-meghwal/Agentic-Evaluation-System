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

from routes.upload_routes import router as upload_router
from routes.grading_routes import router as grading_router
from routes.user_routes import router as user_router

from api.routes.review_routes import router as review_api_router
from api.routes.export_routes import router as export_api_router
from api.routes.dashboard_routes import router as dashboard_api_router


app = FastAPI(
    title="GradeOps API",
    description="AI-Assisted Academic Evaluation System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.include_router(upload_router)
app.include_router(user_router)
app.include_router(grading_router, prefix="/grading", tags=["grading"])
app.include_router(review_api_router, prefix="/api/review", tags=["review"])
app.include_router(export_api_router, prefix="/api/export", tags=["export"])
app.include_router(dashboard_api_router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
def home():
    return {"message": "GradeOps Backend Running"}
