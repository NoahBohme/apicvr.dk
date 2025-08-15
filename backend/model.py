from sqlalchemy import Column, Integer, String,DateTime
from .database import Base
from datetime import datetime

class Accessor(Base):
    __tablename__ = "accessors"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    origin = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    method = Column(String)
    url = Column(String)
    country = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)