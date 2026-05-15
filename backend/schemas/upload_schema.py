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

    created_at: datetime

    class Config:

        from_attributes = True