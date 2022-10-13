import sqlite3

conn = sqlite3.connect('inventory.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE merch_inventory
          (SKU VARCHAR(20) NOT NULL, 
           merchPrice FLOAT NOT NULL,
           merchQuantity INTEGER NOT NULL,
           merchName VARCHAR(100) NOT NULL,
           date_added DATETIME NOT NULL,
           trace_id VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE food_inventory
          (foodName VARCHAR(20) NOT NULL, 
           foodPrice FLOAT NOT NULL,
           foodQuantity INTEGER NOT NULL,
           expirationDate VARCHAR(100) NOT NULL,
           date_added DATETIME NOT NULL,
           trace_id VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
