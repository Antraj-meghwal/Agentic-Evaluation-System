import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Central configuration loaded from
    environment variables.
    """

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/gradeops"
    )

    # JWT / Auth
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "CHANGE_THIS_IN_PRODUCTION"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60"
        )
    )

    # Hugging Face
    HF_TOKEN: str = os.getenv(
        "HF_TOKEN", ""
    )

    # Celery / Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # ChromaDB
    CHROMA_PATH: str = os.getenv(
        "CHROMA_PATH",
        "data/chroma"
    )

    # File uploads
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        "uploads"
    )
    PROCESSED_DIR: str = os.getenv(
        "PROCESSED_DIR",
        "uploads/processed"
    )
    MAX_FILE_SIZE: int = int(
        os.getenv(
            "MAX_FILE_SIZE",
            str(5 * 1024 * 1024)
        )
    )

    # Grading thresholds
    ESCALATION_CONFIDENCE_THRESHOLD: float = float(
        os.getenv(
            "ESCALATION_CONFIDENCE_THRESHOLD",
            "0.6"
        )
    )
    ESCALATION_DISAGREEMENT_THRESHOLD: float = float(
        os.getenv(
            "ESCALATION_DISAGREEMENT_THRESHOLD",
            "0.3"
        )
    )

    # Plagiarism
    PLAGIARISM_SIMILARITY_THRESHOLD: float = float(
        os.getenv(
            "PLAGIARISM_SIMILARITY_THRESHOLD",
            "0.92"
        )
    )


settings = Settings()
