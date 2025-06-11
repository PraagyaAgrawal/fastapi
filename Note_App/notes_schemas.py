from pydantic import BaseModel
from datetime import datetime

class PadBase(BaseModel):
    title: str
    content: str | None = None
class Pad(PadBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
class PadUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
