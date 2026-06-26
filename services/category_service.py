import sqlite3
import sys
import os

current_file_path = os.path.abspath(__file__)
services_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(services_dir) # اینجا میشه پوشه inventory_manager

if project_root not in sys.path:
    sys.path.append(project_root)

from db import get_db_connection


def add_category(name):

    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories(name) VALUES (?) ",(name,))
        conn.commit()
        print(f"{name} added to categories successfully")
        return True
    
    except sqlite3.IntegrityError:
        print(f"{name} add to categories unsuccessfull")
        return False
    
    except Exception as e:
        print("We have error : ",e)
        return False 

    finally:

        conn.close()        


def get_all_categories():

    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")
        return cursor.fetchall()
    except Exception as e:
        print("we have error :",e)

    finally:
        conn.close()
def delete_category(category_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        print(f"{category_id}  has been deleted")
        conn.commit()
        
        return True
    
    except Exception as e:

        print(f"we have error : {e} \nyou have to first delete product ",)

        return False
    
    finally:
        conn.close()

        