import json
import os

# Tên thư mục chứa dữ liệu
DATA_FOLDER = "data"

# Đảm bảo thư mục 'data' luôn tồn tại
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def get_file_path(username):
    """Hàm tạo đường dẫn file dựa trên tên người dùng.
    Ví dụ: user là 'lan' -> data/lan.json
    """
    # Xử lý tên file an toàn (xóa khoảng trắng thừa, chuyển thường)
    safe_name = "".join(x for x in username if x.isalnum()).lower()
    if not safe_name: safe_name = "unknown"
    return os.path.join(DATA_FOLDER, f"{safe_name}.json")

def load_data(username):
    """Đọc dữ liệu lịch sử của một người dùng"""
    file_path = get_file_path(username)
    
    # Nếu file chưa tồn tại (người dùng mới), trả về dữ liệu mặc định
    if not os.path.exists(file_path):
        return {
            "sessions": {},       # Danh sách các cuộc trò chuyện
            "current_session": "" # ID của cuộc trò chuyện đang mở
        }
    
    # Nếu file có rồi thì mở ra đọc
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return {}

def save_data(username, data):
    """Lưu dữ liệu của người dùng vào file"""
    file_path = get_file_path(username)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # ensure_ascii=False để lưu tiếng Việt không bị lỗi font
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file {file_path}: {e}")
        return False