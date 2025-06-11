from pydantic import BaseModel

class PadBase(BaseModel):
    title: str
    content: str | None = None
class Pad(PadBase):
    id: int

    class Config:
        from_attributes = True
class PadUpdate(PadBase):
    title: str | None = None
    content: str | None = None
    content_add: str | None = None
    backspace_num: int | None = None
