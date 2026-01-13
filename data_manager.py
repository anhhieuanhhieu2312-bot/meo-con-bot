import json
import os

# Tên thư mục chứa dữ liệu
DATA_FOLDER = "data"

def ensure_folder_exists():
    """Kiểm tra nếu chưa có thư mục data thì tự tạo"""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

def load_data(username):
    ensure_folder_exists() # <--- Luôn đảm bảo thư mục tồn tại trước
    file_path = os.path.join(DATA_FOLDER, f"{username}.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass # Nếu lỗi file thì trả về mặc định
            
    # Dữ liệu mặc định cho người mới
    return {"sessions": {}, "current_session": ""}

def save_data(username, data):
    ensure_folder_exists() # <--- Luôn đảm bảo thư mục tồn tại trước
    file_path = os.path.join(DATA_FOLDER, f"{username}.json")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")