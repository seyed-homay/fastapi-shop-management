from services import user_service
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt

router = APIRouter()


class RegisterUser(BaseModel):
    username : str
    password : str
    role : str = "user"

class LoginUser(BaseModel):
    username : str
    password : str

@router.post("/users")
def register_user(user_data : RegisterUser):
    try:

        new_user_list = user_data.dict()


        result = user_service.register_user(**new_user_list)
        
        if result:
            return {"status": "success", "message":"اکانت با موفقیت ساخته شد"}
        else:
            raise HTTPException(status_code=400, detail="ساخت اکانت موفق نبود")
        
    except HTTPException as http_err:
        raise http_err
    

    except Exception as e:

        print(f"Database Error: {e}")

        raise HTTPException(status_code=500, detail="خطای داخلی سرور در ثبت یوزر")

@router.post("/users/login")
def login(user_data : LoginUser):

    try:
        new_user_list = user_data.dict()

        result = user_service.login(**new_user_list)
        if result is not None:
            user_payload = {"role":result["role"]}
        else:
            raise HTTPException(status_code=500, detail="خطای داخلی سرور در ورود کاربر")
        SECRET_KEY = "my_secret_key_123"
        my_token = jwt.encode(user_payload,SECRET_KEY  ,algorithm="HS256")

        if result: 
            return {"status":"success","message":"وارد اکانت شدید","role":result["role"],"token":my_token}
        else:
            raise HTTPException(status_code=400,detail="یوزرنیم یا پسوورد اشتباه است")
        
    except HTTPException as http_err:
        raise http_err
    

    except Exception as e:

        print(f"Database Error: {e}")

        raise HTTPException(status_code=500, detail="خطای داخلی سرور در ورود اکانت")
        
        
