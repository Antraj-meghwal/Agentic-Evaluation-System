# Pydantic model tools
from pydantic import BaseModel

# Date/time support
from datetime import datetime


# -----------------------------------
# Upload response schema
# -----------------------------------
class UploadResponse(BaseModel):

    id: int

    filename: str

    file_url: str

    status: str

    rubric_path: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True


class BulkUploadResponse(BaseModel):
    uploaded: int
    items: list[UploadResponse]