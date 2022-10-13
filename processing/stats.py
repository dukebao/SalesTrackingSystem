from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
from sqlalchemy import Float

class SalesStats(Base):
    __tablename__ = 'SalesStats'
    trace_id = Column(String(250), primary_key=True)
    merchSales = Column(Float, nullable=False)
    foodSales = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, trace_id, merchSales, foodSales, timestamp):
        self.trace_id = trace_id
        self.merchSales = merchSales
        self.foodSales = foodSales
        self.timestamp = timestamp
        

    def __repr__(self):
        return f'SalesStats(trace_id={self.trace_id}, merchSales={self.merchSales}, foodSales={self.foodSales}, timestamp={self.timestamp})'