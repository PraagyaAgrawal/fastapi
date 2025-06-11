from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .test_db import Base

class Pad(Base):
    __tablename__ = "pads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    content = Column(String)

    def __repr__(self):
        return f"<Pad(id={self.id}, title={self.title})>"