from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class UploadedFile(BaseModel):
    _id: Optional[ObjectId] = None
    project_id: ObjectId
    original_file_name: str = Field(..., min_length=1)
    stored_file_name: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
