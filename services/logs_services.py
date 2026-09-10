from db import get_db_connection,db_connection,Products,Users,Logs,StockMovement,PriceHistory,Sales
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

def insert_user_logs(action,user_id):
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO logs(action,timestamp,user_id) VALUES (?,?,?)

                        """,(action,user_id))
        conn.commit()
        return True
       
    except Exception as e:
        print("ERROR : " ,e )
        return False
    finally:
        conn.close()

def insert_users_logs2(action:str,user_id : str) -> bool:
    session = db_connection()
    try:
        log_entry = Logs(action=action,user_id=user_id)
        session.add(log_entry)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()  
        print("Database Error:", e)
        return False

    except Exception as e:
        session.rollback() 
        print("Unexpected Error:", e)
        return False

    finally:
        session.close()
def log_stock_movement(
    product_id: int,
    user_id: int,
    action: str,
    change_quantity: int,
    quantity_after: int,
    reason: str | None = None,
    session: Session | None = None,
) -> bool:

    # ۱. مشخص می‌کنیم که سشن از بیرون آمده یا باید خودمان بسازیم
    is_external_session = session is not None
    local_session = session if is_external_session else db_connection()

    try:
        log_entry = StockMovement(
            product_id=product_id,
            user_id=user_id,
            action=action,
            reason=reason,
            change_quantity=change_quantity,
            quantity_after=quantity_after,
        )
        local_session.add(log_entry)

        if not is_external_session:
            local_session.commit()

        return True

    except Exception as e:
        if not is_external_session:
            local_session.rollback()
        print(f"Error logging stock movement: {e}")
        return False

    finally:
        if not is_external_session:
            local_session.close()

def change_price(product_id:int,
                 user_id:int
                 ,new_price:float
                 ,previous_price:float | None = None
                 ,reason:str | None=None ,
                 session: Session | None = None)->bool:
    is_external_session = session is not None
    local_session = session if is_external_session else db_connection()

    try:
        log_entry = PriceHistory(product_id=product_id,user_id=user_id,reason=reason,
                                 previous_price=previous_price,new_price=new_price)
        local_session.add(log_entry)

        if not is_external_session:
            local_session.commit()

        return True

    except Exception as e:
        if not is_external_session:
            local_session.rollback()
        print(f"Error logging stock movement: {e}")
        return False

    finally:
        if not is_external_session:
            local_session.close()
def sell_product_log(product_id:int
                     ,user_id:int
                     ,quantity:int
                     ,unit_price:float
                     ,total_price:float
                     ,session:Session | None = None):
    is_external_session = session is not None
    local_session = session if is_external_session else db_connection()

    try:
        log_entry = Sales(product_id=product_id,user_id=user_id,quantity=quantity,unit_price=unit_price
                          ,total_price=total_price)
        local_session.add(log_entry)

        if not is_external_session:
            local_session.commit()

        return True

    except Exception as e:
        if not is_external_session:
            local_session.rollback()
        print(f"Error logging stock movement: {e}")
        return False

    finally:
        if not is_external_session:
            local_session.close()

# def add_product(product_id,user_id,action,reason,change_quantity,quantity_after,session):
#     local_session = session if session else db_connection()
#     try:
#         log_entry = StockMovement(product_id=product_id,user_id=user_id,action=action,reason=reason
#                                   ,change_quantity=change_quantity,quantity_after=quantity_after)
#         local_session.add(log_entry)
#         if session is None:
#             local_session.commit()
#         return True
#     except Exception as e:
#         if session is None:
#             local_session.rollback()
#         print("Log Error:", e)
#         return False
#     finally:
#         if session is None:
#             local_session.close()
            

# def sell_product_log(action,product_id,old_quantity,new_quantity,buy_quantity,unit_price,total_price,purchase_price):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""INSERT INTO inventory_logs(action,product_id,old_quantity
#                        ,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)"""
#                        ,(action,product_id,old_quantity,new_quantity,None,None))
        
#         cursor.execute("""INSERT INTO sales(product_id,quantity,unit_price,total_price,purchase_price)    VALUES(?,?,?,?,?)""",
#                        (product_id,buy_quantity,unit_price,total_price,purchase_price))

#         print("solded product successfully add to log services")
#         conn.commit()
#         return True
#     except Exception as e:
#         print("ERROR : ",e)
#         return False
#     finally:
#         conn.close()



# def add_product(action,product_id):
#     conn = get_db_connection()
    
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""INSERT INTO inventory_logs(action,product_id,old_quantity
#                        ,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)"""
#                        ,(action,product_id,
#                        None,None,None,None))
#         conn.commit()
#         return True
#     except Exception as e:
#         print("ERROR : ",e)
#         return False
#     finally:
#         conn.close()



# def product_logs(action,product_id,old_quantity,new_quantity,old_price,new_price):
#     conn = get_db_connection()

#     try:
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO inventory_logs(action,product_id,old_quantity,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)""",
#             (action,product_id,old_quantity,new_quantity,old_price,new_price))
#         conn.commit()
#         return True
#     except Exception as e:
#         print("ERROR : ",e) 
#         return False
#     finally:
#         conn.close()
# def product_logs2(action,product_id,old_quantity,new_quantity,old_price,new_price):
#     session = db_connection()
#     try:
#         log_entry = inventory_logs(action=action,product_id=product_id,old_quantity=old_quantity,new_quantity=new_quantity,
#                                     old_price=old_price,new_price=new_price)
#         session.add(log_entry)
#         session.commit()
#         return True
#     except SQLAlchemyError as e:
#         session.rollback()  
#         print("Database Error:", e)
#         return False

#     except Exception as e:
#         session.rollback() 
#         print("Unexpected Error:", e)
#         return False

#     finally:
#         session.close()