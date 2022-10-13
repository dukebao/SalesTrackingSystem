from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
from sqlalchemy import Float

class Food(Base):
    __tablename__ = 'food_inventory'
    foodName = Column(String(250), primary_key=True)
    foodPrice = Column(Float, nullable=False)
    foodQuantity = Column(Integer, nullable=False)
    expirationDate = Column(String(250), nullable=False)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    trace_id = Column(String(250), nullable=False)
    
    def __init__(self, foodName, foodPrice, foodQuantity, expirationDate, trace_id):
        self.foodName = foodName
        self.foodPrice = foodPrice
        self.foodQuantity = foodQuantity
        self.expirationDate = expirationDate
        self.date_added = datetime.datetime.utcnow()
        self.trace_id = trace_id
    def __repr__(self):
        return f'Food(foodName={self.foodName}, foodPrice={self.foodPrice}, foodQuantity={self.foodQuantity}), expirationDate={self.expirationDate}, trace_id={self.trace_id})'