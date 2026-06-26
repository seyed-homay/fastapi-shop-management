import sqlite3 
import os
import logging


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

logging.basicConfig(filename="logs/db.log",level=logging.INFO)

logging.info("order fetched succesfull")

def get_db_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")

    # print("Connected to Database Succesfully")
    logging.info("Connected to Database Succesfully")

    return conn 

def init_db():

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS  users(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            role TEXT DEFAULT 'user')""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS categories(category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL)""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS  products(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            price REAL NOT NULL,
                            quantity INTEGER NOT NULL,
                            category_id INTEGER ,
                            FOREIGN KEY (category_id) REFERENCES  categories(category_id))""")
        
        # cursor.execute("""ALTER TABLE products ADD COLUMN is_deleted INTEGER DEFAULT 0""")

        # cursor.execute("""
        #                     CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                     username TEXT UNIQUE NOT NULL,
        #                     password TEXT NOT NULL,
        #                     role TEXT DEFAULT "user")
        #             """)
        cursor.execute("""


                            CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            action TEXT ,
                            timestamp TEXT,
                            user_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(id))

                        """)
        cursor.execute("""
                           CREATE TABLE IF NOT EXISTS inventory_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            action  TEXT,
                            product_id INTEGER, 
                            old_quantity REAL,
                            new_quantity REAL,
                            old_price REAL,
                            new_price REAL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (product_id) REFERENCES products(id)
                        ) 

                            """)
        
        conn.commit()

        print("We Created Basic Tables successful")


    except Exception as e:
    
        print("ERROR : ",e)
    
    
    finally:
    
        conn.close()


if __name__ == '__main__':
    
    init_db()