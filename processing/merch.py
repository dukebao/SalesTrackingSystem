from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
from sqlalchemy import Float

class Merch(Base):
    __tablename__ = 'merch_inventory'

    SKU = Column(String(250), primary_key=True)
    merchPrice = Column(Float, nullable=False)
    merchQuantity = Column(Integer, nullable=False)
    merchName = Column(String(250), nullable=False)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    trace_id = Column(String(250), nullable=False)
    def __init__(self, SKU, merchPrice, merchQuantity,merchName,trace_id):
        self.SKU = SKU
        self.merchPrice = merchPrice
        self.merchQuantity = merchQuantity
        self.merchName = merchName
        self.date_added = datetime.datetime.utcnow()
        self.trace_id = trace_id

    def __repr__(self):
        return f'Merch(SKU={self.SKU}, merchPrice={self.merchPrice}, merchQuantity={self.merchQuantity}, merchName={self.merchName},trace_id={self.trace_id})'