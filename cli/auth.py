from services import user_service

def auth_login():
    print("1: Login\n2: Exit")
    choice = input("Enter : ")
    
    if choice == '1':
        user = input("Enter username: ")
        password = input("Enter password: ")
        current_user = user_service.login(user, password)
        return current_user  # کاربرِ لاگین شده (یا None) را پس می‌دهد
        
    elif choice == '2':
        print("Goodbye")
        exit()
        
    return None