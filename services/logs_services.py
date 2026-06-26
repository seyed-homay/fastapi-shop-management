from db import get_db_connection


def insert_user_logs(action,timestamp,user_id):
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO logs(action,timestamp,user_id) VALUES (?,?,?)

                        """,(action,timestamp,user_id))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR : " ,e )
        return False
    finally:
        conn.close()



def product_logs(action,product_id,old_quantity,new_quantity,old_price,new_price):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory_logs(action,product_id,old_quantity,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)""",
            (action,product_id,old_quantity,new_quantity,old_price,new_price))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR : ",e) 
        return False
    finally:
        conn.close()

def add_product(action,product_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO inventory_logs(action,product_id,old_quantity
                       ,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)"""
                       ,(action,product_id,
                       None,None,None,None))
        conn.commit()
        return True
    except Exception as e:
        print("ERROR : ",e)
        return False
    finally:
        conn.close()
def sell_product_log(action,product_id,old_quantity,new_quantity):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO inventory_logs(action,product_id,old_quantity
                       ,new_quantity,old_price,new_price) VALUES(?,?,?,?,?,?)"""
                       ,(action,product_id,old_quantity,new_quantity,None,None))
        print("solded product successfully add to log services")
        conn.commit()
        return True
    except Exception as e:
        print("ERROR : ",e)
        return False
    finally:
        conn.close()



