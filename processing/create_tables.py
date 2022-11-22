import sqlite3

"""
    merchSales = Column(Float, nullable=False)
    foodSales = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    trace_id = Column(String(250), primary_key=True)

"""

conn = sqlite3.connect('data/processing_storage.sqlite')

c = conn.cursor()

c.execute('''
          CREATE TABLE SalesStats
          (trace_id VARCHAR(250) NOT NULL, 
           merchSales FLOAT NOT NULL,
           foodSales FLOAT NOT NULL,
           timestamp DATETIME NOT NULL)
          ''')

conn.commit()
conn.close()
