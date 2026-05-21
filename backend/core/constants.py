# -----------------------------------
# Allowed file extensions for upload
# -----------------------------------
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
}


# -----------------------------------
# Maximum file size (bytes)
# 5 MB default
# -----------------------------------
MAX_FILE_SIZE = 50 * 1024 * 1024


# -----------------------------------
# Upload directories
# -----------------------------------
UPLOAD_DIR = "uploads"
PROCESSED_DIR = "uploads/processed"


# -----------------------------------
# Supported user roles
# -----------------------------------
ROLE_ADMIN = "admin"
ROLE_PROFESSOR = "professor"
ROLE_INSTRUCTOR = "instructor"
ROLE_TA = "ta"
ROLE_STUDENT = "student"

ALL_ROLES = [
    ROLE_ADMIN,
    ROLE_PROFESSOR,
    ROLE_INSTRUCTOR,
    ROLE_TA,
    ROLE_STUDENT
]

GRADING_ROLES = [
    ROLE_ADMIN,
    ROLE_PROFESSOR,
    ROLE_INSTRUCTOR
]

REVIEW_ROLES = [
    ROLE_ADMIN,
    ROLE_PROFESSOR,
    ROLE_INSTRUCTOR,
    ROLE_TA
]


# -----------------------------------
# Escalation thresholds
# -----------------------------------
CONFIDENCE_THRESHOLD = 0.6
DISAGREEMENT_THRESHOLD = 0.3


# -----------------------------------
# Plagiarism detection
# -----------------------------------
PLAGIARISM_SIMILARITY_THRESHOLD = 0.92


# -----------------------------------
# RAG retrieval
# -----------------------------------
RAG_TOP_K = 3


# -----------------------------------
# Celery task retry config
# -----------------------------------
MAX_TASK_RETRIES = 3
RETRY_BACKOFF_MAX = 600
