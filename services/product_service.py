import sqlite3
import sys
import os
from services import logs_services
import datetime

from db import get_db_connection



def add_product(name,price,quantity,category_id,purchase_price):

    if price < 0 or quantity < 0 :

        raise ValueError("price and quantity can't be negative ")
    
    conn = get_db_connection()
    try:


        cursor = conn.cursor()

        cursor.execute("INSERT INTO products(name, price, quantity, category_id,purchase_price) VALUES (?,?,?,?,?)"
                       
                       ,(name,price,quantity,category_id,purchase_price))
        product_id =cursor.lastrowid
        conn.commit()
        logs_services.add_product("add_product",product_id)
        return True
    
    except sqlite3.IntegrityError:

        print(f"{name} add to categories unsuccessfull")
        
        return False
    
    except Exception as e:

        print("We have error : ",e)

        return False 
    
    finally:

        conn.close()
    

def get_product_by_id(product_id):

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products  WHERE id = ? ",(product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    except Exception as e:
        print("ERROR",e)
    finally:
        conn.close()

def get_all_product():
    conn  = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE is_deleted = 0")
        rows = cursor.fetchall()
        return rows if rows else []
        
    except Exception as e:
        print("ERROR",e)
    finally:
        conn.close()

def add_multiple_products(products):
    conn = get_db_connection()
    try:

        cursor = conn.cursor()
        formatted_products = []
        for p in products:
            if isinstance(p, dict):
                formatted_products.append((
                    p["name"],
                    p["price"],
                    p["quantity"],
                    p["category_id"]
                ))
            else:
                formatted_products.append(p)

        cursor.executemany("INSERT INTO products(name,price,quantity,category_id,purchase_price) VALUES (?,?,?,?,?)",products)

        print("Insert into product is succesfull")

        conn.commit()

        return True
    
    except sqlite3.IntegrityError as e:

        print("Failed to insert products due to integrity error:", e)
        
        return False
    
    except Exception as e:
        print("Unexpected error:", e)
        return False


    finally:

        conn.close()
    
# def update_pdoduct(product_id,new_price,new_quantity):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         query = "UPDATE products SET price =?,quantity = ? WHERE id = ?"
#         cursor.execute(query,(new_price,new_quantity,product_id))
#         if cursor.rowcount == 0:
#             raise ValueError("product not found")
#         print("update database succesfull")
#         conn.commit()
#     except Exception as e:
#         print("ERROR : ",e)
#     finally:
        conn.close()
def update_product(product_id, new_price, new_quantity):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        old_quantity = cursor.execute("SELECT quantity FROM products WHERE id = ?",(product_id,)).fetchone()[0]
        old_price = cursor.execute("SELECT price FROM products WHERE id = ?",(product_id,)).fetchone()[0]

        query = "UPDATE products SET price = ?, quantity = ? WHERE id = ?"
        cursor.execute(query, (new_price, new_quantity, product_id))
        
        # اگر ردیفی تغییر نکرده باشد یعنی آیدی اشتباه است
        if cursor.rowcount == 0:
            
            return False
        conn.commit()
        print("update database succesfull")
        logs_services.product_logs("update",product_id,old_quantity,new_quantity,old_price,new_price)    
        return True # حتماً این را ریترن کن
        
    except Exception as e:
        print("ERROR : ", e)
        return False
    finally:
        conn.close()

def delete_product(product_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?",(product_id,))
        row = cursor.fetchone()
        if row is None:
            return "not_found"
        if row["quantity"] > 0:
            return "has_quantity"
        
        cursor.execute("UPDATE products  SET is_deleted = ? WHERE id = ?",(1,product_id))
        print("item is deleted now")
        conn.commit()
        logs_services.product_logs("DEL Product",product_id,None,None,None,None)  
        return "success"
        
    except Exception as e:
        print("Error in soft delete:", e)
        return "error"
    finally:
        conn.close()

    

def search_product(keyword):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
                SELECT p.id , p.name , c.name as category ,p.price , p.quantity
                FROM products p join categories c ON p.category_id = c.category_id
                WHERE p.name LIKE ? AND p.is_deleted = 0
                 """
        cursor.execute(query,(f"%{keyword}%",))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]
         
    except Exception as e:
        print("ERROR = ",e)
    finally:
        conn.close()


def get_product_price_filter(number):
    conn = get_db_connection()
    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products WHERE quantity <  ?
            """,(number,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:

        print("ERROR ",e)

    finally:
        conn.close()

def get_category_total_value():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
    categories.name AS category_name,
    SUM(products.price * products.quantity) AS total_value
    FROM products join categories ON categories.category_id = products.category_id


    WHERE products.is_deleted != 1

    GROUP BY categories.category_id

    ORDER BY total_value DESC

        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()
    
               
def sell_product(product_id,buy_quantity):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        old_quantity = cursor.execute("""SELECT quantity FROM products WHERE id = ?"""
                                      ,(product_id,)).fetchone()[0]
        if old_quantity<=0 :
            raise ValueError("این کالا در انبار موجود نیست")
        elif buy_quantity > old_quantity:
            raise ValueError("تعداد موجودی کمتر از درخواست شماست")
        # price = cursor.execute("""SELECT price FROM products WHERE id = ?"""
        #                                ,(product_id,)).fetchone()[0]
        query = "UPDATE products SET quantity =? WHERE id = ?"
        new_quantity = old_quantity - buy_quantity
        price_row = cursor.execute("SELECT price FROM products WHERE id = ?",(product_id,))
        price = price_row.fetchone()[0]
        total_price = buy_quantity * price
        cursor.execute(query,(new_quantity,product_id))
        purchase_price = cursor.execute("SELECT purchase_price FROM products WHERE id =?",(product_id,))
        purchase=purchase_price.fetchone()[0]
        conn.commit()
        print("product successfully was sold ")
        logs_services.sell_product_log("sold",product_id,old_quantity,new_quantity,buy_quantity,price,total_price,purchase)
        return True

    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()
def get_today_total_sales():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        today_total_prices = cursor.execute("""SELECT SUM(total_price) FROM sales WHERE DAtE(timestamp) = DATE(current_timestamp)""")
        today_total = today_total_prices.fetchone()[0]
        if today_total == None or today_total == "null":
            return {"total_sales" : 0} 
        return {"total_sales":today_total[0]}
    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()
def get_total_sales_with_time(first_date:str,second_date:str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        total_price = cursor.execute("""SELECT SUM(total_price) FROM sales WHERE DAtE(timestamp) BETWEEN ? AND ?""",
                                     (first_date,second_date))
        total = total_price.fetchone()
        if total[0] == "null" or total[0] == None:
            return {"total_sales":0}
        return {"total_sales":total[0]}
    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()

def get_profit_of_sales(time):
    # print(time)
    profit = 0
    sum_profit=0
    conn = get_db_connection()
    try:
        
        cursor = conn.cursor()
        sales_rows = cursor.execute("""SELECT * FROM sales WHERE DATE(timestamp)  = ?""",(time,))
        rows=sales_rows.fetchall()
        if rows == []:
            return {"error":"nothing in database for this time"}
        for row in rows:
            
            profit = row["total_price"] - (row["purchase_price"]*row["quantity"] )
            sum_profit += profit

        return sum_profit
            



    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()
        