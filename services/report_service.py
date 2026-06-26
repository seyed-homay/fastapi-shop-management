import csv 
import sqlite3
from db import get_db_connection



def export_product_to_csv(FILE_PATH):

    conn = get_db_connection()

    try:
        
        cursor = conn.cursor()

        cursor.execute("SELECT id,name,price,quantity FROM products")

        products = cursor.fetchall()


        with open(FILE_PATH,mode="w",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Name","Price","Quantity"])
            for row in products:
                print(row["id"])
                writer.writerow([row['id'],row['name'],row['price'],row['quantity']])

        print(f"File {FILE_PATH} created")


    except Exception as e :
        print("error : ",e)

    finally:
        conn.close()

def export_users_to_csv(FILE_PATH):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT username,role FROM users")

        rows = cursor.fetchall()

        with open(FILE_PATH,mode='w',newline='',encoding='utf-8') as file:
            # file.write("sep=;\n") 
            writer = csv.writer(file ,delimiter=';')
            writer.writerow(['UserName','Role'])
            
            for row in rows:
                writer.writerow([row['username'],row['role']])

        print(f"{FILE_PATH} IS CREATED ")
    except Exception as e:
        print("error : ",e)
    finally:
        conn.close()


def import_from_csv_(file):

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        with open(file,mode='r',encoding="utf-8") as f:

            reader =csv.DictReader(f,delimiter=';')
            for row in reader:
                name = row['name']
                price = float(row['price'])
                quantity = int(row['quantity'])
                category_id = int(row['category_id'])
                is_deleted = int(row['is_deleted'])
            cursor.execute("""INSERT INTO products(name,price,quantity,category_id,is_deleted)
                            VALUES (?,?,?,?,?)"""
                           ,(name,price,quantity,category_id,is_deleted))
            conn.commit()

    except sqlite3.IntegrityError:
        print("This item exit in file you can't add now")
    
    except Exception as e:
        print("Error : ",e)
    finally:
        conn.close()