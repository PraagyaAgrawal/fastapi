from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .notes_db import Base

class Pad(Base):
    __tablename__ = "pads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime, default = func.now())
    updated_at = Column(DateTime, default = func.now(), onupdate = func.now())
