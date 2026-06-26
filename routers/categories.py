from fastapi import APIRouter,HTTPException
from services import category_service
from pydantic import BaseModel


router = APIRouter()



class CategoryCreat(BaseModel):
    name: str


@router.post("/categories")
def creat_category_api(category: CategoryCreat):
    try:
        result = category_service.add_category(category.name)

        if result:
            return {"status":"success","message":"Category successfully created"}
        else:
            raise HTTPException(status_code=400,detail="Add to categroy unsuccessful")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error : {e}")
        raise HTTPException(status_code=500, detail="Database Error")
    



@router.get("/categories")

def list_category_api():
    try:
        categories = category_service.get_all_categories()

        if not categories:
            raise HTTPException(status_code=404, detail="nothing category for show")
        else:
            return [dict(row) for row in categories]
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Database Error : {e}")
        raise HTTPException(status_code=500, detail="Database Error")
@router.delete("/categories/{category_id}")
def delete_category_api(category_id: int):
    
    result = category_service.delete_category(category_id)
    if result:
        return {"status": "success", "message": f"دسته‌بندی با آیدی {category_id} با موفقیت حذف شد"}
    
    raise HTTPException(
        status_code=400, 
        detail="حذف دسته‌بندی شکست خورد. ابتدا باید تمام محصولاتِ متصل به این دسته‌بندی را حذف کنید."
    )