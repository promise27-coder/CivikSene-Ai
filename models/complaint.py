from sqlalchemy import Column, Float, Integer, String
from database.database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    category = Column(String)
    priority = Column(String)
    status = Column(String, default="Pending")
    lat = Column(Float, nullable=True)
    long = Column(Float, nullable=True)
