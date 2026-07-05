from fastapi import APIRouter, HTTPException , Depends
from pydantic import BaseModel
from services import product_service
from typing import List
import jwt
import datetime

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    category_id: int # اختیاری
    purchase_price: float
    

class InvoiceItem(BaseModel):
    product_id : int
    sold_quantity : int

def verify_admin(token:str):
    SECRET_KEY = "my_secret_key_123"
    payload = jwt.decode(token,SECRET_KEY,algorithms="HS256")
    user_status = payload["role"]
    if user_status !="admin":
          raise HTTPException(status_code=403,detail="شما دستری لازم برای این عملیات ندارید")   
    return payload['role']

        

router = APIRouter()

# @router.get("/")
# def read_root():
#     return {'status':'success','message':'به سیستم انبار داری مغازهییی خود آمدید'}


@router.get("/products/{product_id}")

def get_product(product_id: int):
    try:
       
        product = product_service.get_product_by_id(product_id)

        
        if not product:
            raise HTTPException(status_code=404, detail="کالای مورد نظر یافت نشد")
        
        
        return {
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            # "quantity": product["quantity"],
            # "category_id": product["category_id"],
            # "is_deleted": product["is_deleted"]

        }

    except HTTPException as http_err:
        
        raise http_err
    except Exception as e:
        
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="خطای داخلی سرور در اتصال به دیتابیس")
    

@router.post("/product/invoice/sell")
def sell_invoice(cart: List[InvoiceItem]):

    try:
        success = True
        for pduct in cart:
            result = product_service.sell_product(pduct.product_id,pduct.sold_quantity)
            if not result:
                success =False
                print()

        if success:
            return {"status":"success","message":"فاکتور با موفقیت پردازش شد"}
        else:
            raise HTTPException(status_code=400, detail="اضافه کردن ایتم شکست خورد")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")

        raise HTTPException(status_code=500,detail="خطای داخلی سرور در اضافه کردن ایتم به فاکتور")


@router.get("/products")
def get_all_products():

    try:
      
        products = product_service.get_all_product()


        if not products:
            raise HTTPException(status_code=404, detail="کالای مورد نظر یافت نشد")
        
       
        return [{
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": product["quantity"],
            # "category_id": product["category_id"],
            # "is_deleted": product["is_deleted"]
        }
        for product in products
        ]
    except HTTPException as http_err:
        
        raise http_err
    except Exception as e:
        
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="خطای داخلی سرور در اتصال به دیتابیس")

@router.get("/product/search")
def search_product(keyword):
    try:
        searched_product =product_service.search_product(keyword)
        if not searched_product:
            raise HTTPException(status_code=404,detail="کالای مورد نظر یافت نشد")
        
        return searched_product
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500,detail="خطای داخلی در اتصال به سرور")
    
@router.get("/admin/analytics/today-total-sales")
def today_total_sales():
    try:
        total = product_service.get_today_total_sales()
        
        return total
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500,detail="خطای داخلی در اتصال به سرور")


@router.get("/admin/analytics/total-sales-withtime")
def total_sales(first_date,second_date):
    try:
        total = product_service.get_total_sales_with_time(first_date,second_date)
        
        return total
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500,detail="خطای داخلی در اتصال به سرور")
@router.get("/admin/analytics/total-profit")
def total_profit(time =None):
    if time is None:
        time = (datetime.datetime.now().date())
    try:
        total = product_service.get_profit_of_sales(time)
        return {"total":total,"detail":"سود روز شما :"}
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500,detail="خطای داخلی در اتصال به سرور")


@router.post("/products")
def create_product(product_data: ProductCreate, admin_status: str = Depends(verify_admin)):
    try:
        print("--- دیتای دریافتی در بک‌آند ---:", product_data.dict())
        
        new_product_dict = product_data.dict()
        
        result = product_service.add_product(**new_product_dict)
        
        if result:
            return {"status": "success", "message": "کالا با موفقیت در انبار ثبت شد"}
        else:
            raise HTTPException(status_code=400, detail="ثبت کالا ناموفق بود (احتمالاً نام تکراری است)")
        
    except HTTPException as http_err:
        raise http_err
    

    except Exception as e:

        print(f"Database Error: {e}")

        raise HTTPException(status_code=500, detail="خطای داخلی سرور در ثبت کالا")


@router.put("/product/{product_id}/{new_price}/{new_quantity}")
def update_product(product_id:int,new_price:float,new_quantity:int, admin_status: str = Depends(verify_admin)):
    try:
        updated_product = product_service.update_product(product_id,new_price,new_quantity)

        if updated_product:
            return {"status": "success", "message": "قیمت و موجودی کالا با موفقیت تغییر یافت"}
        else:
            raise HTTPException(status_code=400, detail="تغییر قیمت و موجودی کالا شکست خورد")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")

        raise HTTPException(status_code=500,detail="خطای داخلی سرور در تغییر قیمت کالا")


@router.delete("/products/{product_id}")
def delete_product(product_id, admin_status: str = Depends(verify_admin)):
    
        
    status = product_service.delete_product(product_id)
    if status == "success":
        return {"status": "success", "message": "کالا با موفقیت غیرفعال و از لیست انبار حذف نرم شد"}
        
    elif status == "has_quantity":
        raise HTTPException(
            status_code=400, 
            detail="خطا: شما نمی‌توانید این کالا را حذف کنید چون هنوز در مغازه موجودی دارد"
        )
        
    elif status == "not_found":
        raise HTTPException(status_code=404, detail="کالای مورد نظر در دیتابیس یافت نشد")
        
    else:
        raise HTTPException(status_code=500, detail="خطای داخلی سرور در پردازش حذف کالا")
    


@router.put("/product/{product_id}/{sold_quantity}")
def sold_product(product_id:int,sold_quantity:int):
    try:
        solded_product = product_service.sell_product(product_id,sold_quantity)

        if solded_product:
            return {"status": "success", "message": "قیمت و موجودی کالا با موفقیت تغییر یافت"}
        else:
            raise HTTPException(status_code=400, detail="تغییر قیمت و موجودی کالا شکست خورد")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error: {e}")

        raise HTTPException(status_code=500,detail="خطای داخلی سرور در تغییر قیمت کالا")


