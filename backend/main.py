# Import FastAPI framework
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# Used to copy uploaded files
import shutil

# Used for serving static files
from fastapi.staticfiles import StaticFiles


# Create FastAPI app
app = FastAPI()


# -----------------------------------
# Enable CORS
# -----------------------------------
# Allows frontend to talk to backend

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Home route
@app.get("/")
def home():

    return {
        "message": "GradeOps Backend Running"
    }


# Upload route
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):

    # Path where file will be saved
    file_location = f"uploads/{file.filename}"

    # Open file in write-binary mode
    with open(file_location, "wb") as buffer:

        # Copy uploaded file into uploads folder
        shutil.copyfileobj(file.file, buffer)

    # Return response
    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "file_url": f"http://127.0.0.1:8000/uploads/{file.filename}"
    }