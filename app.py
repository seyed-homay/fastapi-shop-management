import os
from fastapi import FastAPI
from routers import products ,categories,users
from fastapi.responses import HTMLResponse





app = FastAPI()

# معرفی کردن مسیرهای فایل جدید به کل سیستم
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(users.router)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

