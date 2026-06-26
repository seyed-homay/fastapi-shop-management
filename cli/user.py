from services import product_service,report_service,user_service
import datetime


PRODUCTE_FILE_PATH = f"""reports/products_report__{datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")}.csv"""
USERS_FILE_PATH = f"""reports/users_report__{datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")}.csv"""

from services import product_service, report_service, user_service
# مسیرهای فایل CSV را اینجا نگه دار...

def admin_menu(current_user):
    while True: # حلقه همینجا داخل منو می‌چرخد تا کاربر خروج را بزند
        print("\n--- Admin Menu ---")
        print("1: Delete Product\n2: Export to CSV\n3: Change Password\n4: Logout")
        choice = input("Enter : ")

        if choice == "1":
            product_ID = int(input("Enter ID: "))
            product_service.delete_product(product_ID)
        elif choice == "2":
            report_service.export_product_to_csv(PRODUCTE_FILE_PATH)
        elif choice == "3":
            old_pass = input("Enter your old pass: ")
            new_password = input("Enter new password: ")
            x = user_service.changepassword(current_user['username'], old_pass, new_password)
            if x is False:
                print("Your password is not correct")
        elif choice == "4":
            print("Logging out from admin...")
            break # این بریک حلقه همین منو را می‌شکند و تابع تمام می‌شود
