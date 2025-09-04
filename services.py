from datetime import date

def check_file_exist(items:list) -> None:
    today_date:str = "inventory_update_" + str(date.today())
    if today_date in items:
            print(f"file exist")
    
    
