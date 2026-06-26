import bcrypt
import sqlite3
import datetime
from db import get_db_connection
from services import logs_services




def register_user(username,password,role='user'):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO users(username,password_hash,role) VALUES (?,?,?)
                        """,(username,hashed_pw,role))
        user =  cursor.lastrowid
        logs_services.insert_user_logs("Register",datetime.datetime.now().strftime("%d.%m.%Y"),user)
        print("The user is added")
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Username is duplicated")
        return False
    finally:
        conn.close()
    

def login(username,password):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        
        user =  cursor.fetchone()
        
        
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            print("[Login success ")
            print(f"[role is {user['role']}]")
            logs_services.insert_user_logs("Login",datetime.datetime.now().strftime("%d.%m.%Y"),user["id"])
            print("succesfully loged in")
            return user
            
        print("[Login Failed]")

        return None
    
    except Exception as e:
        print("nonon",e)
    finally:
        conn.close()


def changepassword(user,user_password,new_password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?",(user,))
        current_password = cursor.fetchone()
        if current_password is None:
            print("User not found")
            return False
        else:
            if bcrypt.checkpw(user_password.encode('utf-8'),current_password['password_hash'] ):
                
                hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'),bcrypt.gensalt())
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ? ",(hashed_pw,user))
                if cursor.rowcount == 0:
                    raise ValueError("user not found")
                print("update password succesfull")
                conn.commit()
                return True

            else:
                return False
    except Exception as e:
        print("vay vay : ",e)

    finally:
        conn.close()



