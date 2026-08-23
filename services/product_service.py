import sqlite3
import sys
import os
from services import logs_services
import datetime
from sqlalchemy import update , select
from sqlalchemy.exc import IntegrityError , SQLAlchemyError
from db import db_connection,get_db_connection , Users,Products



def add_product(name, user,price, quantity, purchase_price,
                 category_id, min_stock,reason):

    if purchase_price < 0 or price < 0 or quantity < 0 :

        raise ValueError("price and quantity can't be negative ")
    session = db_connection()
    try:

        products_detail = Products(name=name,purchase_price = purchase_price
                                   ,price=price,quantity=quantity,
                                   min_stock=min_stock,category_id=category_id)   

        session.add(products_detail)
        session.flush()
        product_id = products_detail.id
        
        logs_services.log_stock_movement(product_id=product_id,user_id=user,action="add_product"
                                             ,reason=reason,change_quantity=quantity
                                             ,quantity_after=quantity,session=session)
        session.commit()
        return True
    
    except IntegrityError as e:
        session.rollback()
        # 👈 چاپ کردن orig یا e باعث می‌شود متن دقیق دیتابیس را ببینی
        print(f"❌ Integrity Error Detail: {e.orig}") 
        return False
    except SQLAlchemyError as e:
        session.rollback()
        print("Database Error ")
        return False
    
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected Error: {e}")
        return False
    
    finally:

        session.close()

def update_quantity_product(product_id,user_id,action,reason,change_quantity):
    session = db_connection()
    try:
        existing_product = session.query(Products).filter(Products.id == product_id).first()
        if not existing_product:
            raise ValueError("product not found")

        quantity = existing_product.quantity
        quantity_after = quantity + change_quantity 
        if quantity_after <0:
            raise ValueError("quantity can't be negative")
        existing_product.quantity = quantity_after
        
        logs_services.log_stock_movement(product_id=product_id,user_id=user_id
                                         ,action=action,reason=reason,
                                         change_quantity=change_quantity,
                                         quantity_after=quantity_after,session=session)
        session.commit()
        return True

    except IntegrityError as e:
        session.rollback()
        # 👈 چاپ کردن orig یا e باعث می‌شود متن دقیق دیتابیس را ببینی
        print(f"❌ Integrity Error Detail: {e.orig}") 
        return False
    except SQLAlchemyError as e:
        session.rollback()
        print("Database Error ")
        return False
    
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected Error: {e}")
        return False
    
    finally:

        session.close()    
#i have to creat log table and log function for delete
def delete_product(product_id):
    session = db_connection()
    try:
        row=session.query(Products).filter(Products.id == product_id).first()
        if not row:
            raise ValueError("product not founded")
        if row.quantity != 0:
            raise ValueError("product have to zero quantity to be delete")
        row.is_deleted = 1
        session.commit()
        return True
        
    except IntegrityError as e:
        session.rollback()
        # 👈 چاپ کردن orig یا e باعث می‌شود متن دقیق دیتابیس را ببینی
        print(f"❌ Integrity Error Detail: {e.orig}") 
        return False
    except SQLAlchemyError as e:
        session.rollback()
        print("Database Error ")
        return False
    
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected Error: {e}")
        return False
    
    finally:

        session.close()   
def sell_product(product_id,user_id,quantity):
    session = db_connection()
    try:
        
        if quantity <= 0:
            raise ValueError("quantity could not be zero or negative")
        
        row = session.query(Products).filter(Products.id == product_id,
                                             Products.is_deleted == 0).first()
        if not row:
            raise ValueError("product not found")

        current_quantity = row.quantity
        unit_price = row.price
        if quantity > current_quantity:
            raise ValueError("product's quantity can't be negative")
        total_price = quantity * unit_price
        new_quantity = current_quantity - quantity
        row.quantity = new_quantity
        logs_services.sell_product_log(product_id=product_id,user_id=user_id
                            ,quantity = quantity,unit_price = unit_price
                            ,total_price = total_price,session=session)
        session.commit()
        return True
    except ValueError as e:
        session.rollback()
        return False, str(e)
    except IntegrityError as e:
            session.rollback()
            # 👈 چاپ کردن orig یا e باعث می‌شود متن دقیق دیتابیس را ببینی
            print(f"❌ Integrity Error Detail: {e.orig}") 
            return False
    except SQLAlchemyError as e:
        session.rollback()
        print("Database Error ")
        return False
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return False
    
    finally:

        session.close()   
    
def get_product_by_id(product_id):
    session = db_connection()
    try:
        result = session.query(Products.name , Products.quantity, Products.price).filter(Products.id==product_id
                                                                                         ,Products.is_deleted == 0).first()
        if not result :
            return None
        
        return dict(result._mapping)
    except SQLAlchemyError as e:
        print("Database Error ")
        return None
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return None
    
    finally:

        session.close()


# def get_all_product():
#     conn  = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM products WHERE is_deleted = 0")
        
#         rows = cursor.fetchall()
#         return rows if rows else []
    
        
#     except Exception as e:
#         print("ERROR",e)
#     finally:
#         conn.close()
def get_all_product():
    session = db_connection()
    try:
        result = session.query(Products.name,Products.price,Products.quantity).filter(Products.is_deleted == 0).all()
        if not result :
            return []
        return [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        print("Database Error ")
        return []
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return []
    

def get_minstocks_items():
    session = db_connection()
    try:
        results = session.query(Products.name,Products.price,Products.quantity).filter(
            Products.quantity <= Products.min_stock ,Products.quantity != 0
        ).all()
        if not results:
            return []
        return [dict(row._mapping) for row in results]
    except SQLAlchemyError as e:
        print("Database Error ")
        return []
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return []
    

def get_zerostocks_items():
    session = db_connection()
    try:
        stmt = select(Products.name,Products.price,Products.quantity).where(
            Products.quantity==0)
        results = session.execute(stmt).mappings().all()
        if not results:
            return []
        return results
    except SQLAlchemyError as e:
        print("Database Error ")
        return []
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return []


def add_multiple_products(products,user,reason):
    session = db_connection()
    try:
        formatted_products = []
        
        for row in products:
            if isinstance(row,dict):
                new_row =Products(**row)
                purchase_price = row.get("purchase_price", 0)
                price = row.get("price", 0)
                quantity = row.get("quantity", 0)
                if (new_row.purchase_price < 0 
                    or new_row.price < 0 
                    or new_row.quantity <0):
                    raise ValueError("price and quantity can't be negative ")
                formatted_products.append(new_row)
            else:
                session.rollback()
                print("input data error ")
                return False
        session.add_all(formatted_products)
        session.flush()
        for row in formatted_products:
            product_id = row.id
            quantity = row.quantity
            logs_services.log_stock_movement(product_id=product_id,user_id=user,action="add_product"
                                     ,reason=reason,change_quantity=quantity
                                     ,quantity_after=quantity,session=session)

        session.commit()
        return True
        
    except IntegrityError as e:
        session.rollback()
        # 👈 چاپ کردن orig یا e باعث می‌شود متن دقیق دیتابیس را ببینی
        print(f"❌ Integrity Error Detail: {e.orig}") 
        return False
    except SQLAlchemyError as e:
        session.rollback()
        print("Database Error ")
        return False
    
    except Exception as e:
        session.rollback()
        print(f"❌ Unexpected Error: {e}")
        return False
    
    finally:

        session.close()



                

# def search_product(keyword):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         query = """
#                 SELECT p.id , p.name , c.name as category ,p.price , p.quantity
#                 FROM products p join categories c ON p.category_id = c.category_id
#                 WHERE p.name LIKE ? AND p.is_deleted = 0
#                  """
#         cursor.execute(query,(f"%{keyword}%",))

#         rows = cursor.fetchall()

#         return [dict(row) for row in rows]
         
#     except Exception as e:
#         print("ERROR = ",e)
#     finally:
#         conn.close()

def search_product(keyword):
    session = db_connection()
    try:
        stmt = select(Products.id,Products.name,Products.price,Products.quantity).where(Products.name.like(f"%{keyword}%"),Products.is_deleted == 0)
        results = session.execute(stmt).mappings().all()
        if not results:
            return []
        return [dict(row) for row in results]
    except SQLAlchemyError as e:
        print("Database Error ")
        return []
    
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Unexpected Error: {e}")
        return []
    finally:
        session.close()
        
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
            return 0
        for row in rows:
            
            profit = row["total_price"] - (row["purchase_price"]*row["quantity"] )
            sum_profit += profit

        return sum_profit

    except Exception as e:
        print("ERROR : ",e)
    finally:
        conn.close()


# def get_product_by_id(product_id):

#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM products  WHERE id = ? ",(product_id,))
#         row = cursor.fetchone()
#         #آیتم مورد نظر رو پیدا میکنه و کل ردیف رو به صورت دیکشنری برمیگردونه
#         return dict(row) if row else None
    
#     except Exception as e:
#         print("ERROR",e)
#     finally:
#         conn.close()

# def update_product(product_id, new_price, new_quantity):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         old_quantity = cursor.execute("SELECT quantity FROM products WHERE id = ?",(product_id,)).fetchone()[0]
#         old_price = cursor.execute("SELECT price FROM products WHERE id = ?",(product_id,)).fetchone()[0]

#         query = "UPDATE products SET price = ?, quantity = ? WHERE id = ?"
#         cursor.execute(query, (new_price, new_quantity, product_id))
        
#         # اگر ردیفی تغییر نکرده باشد یعنی آیدی اشتباه است
#         if cursor.rowcount == 0:
            
#             return False
#         conn.commit()
#         print("update database succesfull")
#         logs_services.product_logs("update",product_id,old_quantity,new_quantity,old_price,new_price)    
#         return True # حتماً این را ریترن کن
        
#     except Exception as e:
#         print("ERROR : ", e)
#         return False
#     finally:
#         conn.close()
# def get_zerostocks_items():
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         rows = cursor.execute("SELECT * FROM products WHERE quantity = 0").fetchall()
#         #گرفتن ایتم هایی که موجودیشون صفر شده
#         return rows if rows else []
#     except Exception as e:
#         return e
#     finally:
#         conn.close()

# def delete_product(product_id):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM products WHERE id = ?",(product_id,))
#         row = cursor.fetchone()
#         if row is None:
#             return "not_found"
#         if row["quantity"] > 0:
#             return "has_quantity"
        
#         cursor.execute("UPDATE products  SET is_deleted = ? WHERE id = ?",(1,product_id))
#         print("item is deleted now")
#         conn.commit()
#         logs_services.product_logs("DEL Product",product_id,None,None,None,None)  
#         return "success"
        
#     except Exception as e:
#         print("Error in soft delete:", e)
#         return "error"
#     finally:
#         conn.close()


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
        # conn.close()
# def get_minstocks_items():
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         rows = cursor.execute("SELECT * FROM products WHERE quantity <= min_stock AND quantity != 0").fetchall()
#         #اینجا فقط ردیف هایی که تعدادشون کمتر از حد هشدار هست رو رو برمیگردونیم به غیر از اونایی که مقدارشون صفر
#         return rows if rows else []
#     except Exception as e:
#         return "error",e
#     finally:
#         conn.close()
    # def sell_product(product_id,buy_quantity):
#     conn = get_db_connection()
#     alert = None
#     try:
#         cursor = conn.cursor()
#         product_row = cursor.execute("""SELECT name,quantity,price,purchase_price,min_stock FROM products
#                                      WHERE id = ?""",(product_id,)).fetchone()
#         old_quantity = product_row['quantity']
#         name = product_row['name']
#         min_stock = product_row['min_stock']
#         price = product_row['price']
#         purchase_price = product_row['purchase_price']
#         if old_quantity<=0 :
#             raise ValueError("این کالا در انبار موجود نیست")
#         elif buy_quantity > old_quantity:
#             raise ValueError("تعداد موجودی کمتر از درخواست شماست")
#         # old_quantity = cursor.execute("""SELECT quantity FROM products WHERE id = ?"""
#         #                               ,(product_id,)).fetchone()[0]
#         # price = cursor.execute("""SELECT price FROM products WHERE id = ?"""
#         #                                ,(product_id,)).fetchone()[0]
#         # min_stock = cursor.execute("SELECT min_stock FROM products WHERE id = ?",(product_id,)).fetchone()[0]
#         # name = cursor.execute("SELECT name FROM products WHERE id = ?",(product_id,)).fetchone()[0]
#         # price_row = cursor.execute("SELECT price FROM products WHERE id = ?",(product_id,))
#         # price = price_row.fetchone()[0]
#         # purchase_price = cursor.execute("SELECT purchase_price FROM products WHERE id =?",(product_id,))
#         # purchase=purchase_price.fetchone()[0]
#         query = "UPDATE products SET quantity =? WHERE id = ?"
#         new_quantity = old_quantity - buy_quantity
#         if new_quantity <=min_stock:
#             alert = f"this porduct {name} quantity is lower than {min_stock}"
#         total_price = buy_quantity * price
#         cursor.execute(query,(new_quantity,product_id))
#         conn.commit()
#         print("product successfully was sold ")
#         logs_services.sell_product_log("sold",product_id,old_quantity,new_quantity,buy_quantity,price,total_price,purchase_price)
#         return True

#     except Exception as e:
#         print("ERROR : ",e)
#     finally:
#         conn.close()
        
    
# def add_multiple_products(products):
#     conn = get_db_connection()
#     try:

#         cursor = conn.cursor()
#         formatted_products = []
#         for p in products:
#             if isinstance(p, dict):
#                 #چک کردن اینکه ایا 
#                 formatted_products.append((
#                     p["name"],
#                     p["price"],
#                     p["quantity"],
#                     p["category_id"],
#                     p["purchase_price"],
#                     p["min_stock"]
#                 ))
#             else:
#                 formatted_products.append(p)

#         cursor.executemany("INSERT INTO products(name,price,quantity,category_id,purchase_price,min_stock) VALUES (?,?,?,?,?)",formatted_products)

#         print("Insert into product is succesfull")

#         conn.commit()

#         return True
    
#     except sqlite3.IntegrityError as e:

#         print("Failed to insert products due to integrity error:", e)
        
#         return False
    
#     except Exception as e:
#         print("Unexpected error:", e)
#         return False


#     finally:

#         conn.close()