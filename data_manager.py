import json
import streamlit as st
from github import Github, GithubException

# ==============================================
# CẤU HÌNH KẾT NỐI
# ==============================================
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = "anhhieuanhhieu2312-bot/meo-con-bot" 
DATA_FOLDER = "data"

def get_repo():
    """Kết nối tới kho GitHub"""
    if not GITHUB_TOKEN:
        st.error("⚠️ LỖI: Chưa có GITHUB_TOKEN trong Secrets!")
        return None
    try:
        g = Github(GITHUB_TOKEN)
        return g.get_repo(REPO_NAME)
    except Exception as e:
        st.error(f"⚠️ Không thể kết nối GitHub: {e}")
        return None

def load_data(username):
    """Tải dữ liệu an toàn"""
    if not username: return {"sessions": {}, "current_session": ""}
    
    file_path = f"{DATA_FOLDER}/{username}.json"
    
    try:
        repo = get_repo()
        if repo:
            contents = repo.get_contents(file_path)
            json_content = contents.decoded_content.decode("utf-8")
            data = json.loads(json_content)
            if "sessions" not in data: data["sessions"] = {}
            return data
    except:
        # Nếu chưa có file thì trả về rỗng, không báo lỗi
        pass

    return {"sessions": {}, "current_session": ""}

def save_data(username, local_data):
    """
    Lưu dữ liệu: Tự động phát hiện nên 'Tạo mới' hay 'Cập nhật'
    """
    if not username: return
    
    file_path = f"{DATA_FOLDER}/{username}.json"
    repo = get_repo()
    if not repo: return

    try:
        # BƯỚC 1: Kiểm tra xem file đã tồn tại trên GitHub chưa
        contents = None
        remote_data = {"sessions": {}}
        file_exists = False

        try:
            contents = repo.get_contents(file_path)
            remote_json = contents.decoded_content.decode("utf-8")
            remote_data = json.loads(remote_json)
            file_exists = True # Đánh dấu là file ĐÃ CÓ
        except:
            file_exists = False # Đánh dấu là file CHƯA CÓ

        # BƯỚC 2: Hợp nhất dữ liệu (Merge)
        if "sessions" not in remote_data: remote_data["sessions"] = {}
        
        # Cập nhật tin nhắn mới vào dữ liệu cũ
        remote_data["sessions"].update(local_data.get("sessions", {}))
        remote_data["current_session"] = local_data.get("current_session")

        # BƯỚC 3: Chuẩn bị nội dung
        json_str = json.dumps(remote_data, ensure_ascii=False, indent=4)
        
        # BƯỚC 4: Lưu (Chia 2 trường hợp rõ ràng)
        if file_exists and contents:
            # Trường hợp A: File đã có -> Cập nhật (Update)
            repo.update_file(contents.path, f"Update {username}", json_str, contents.sha)
        else:
            # Trường hợp B: File chưa có -> Tạo mới (Create)
            repo.create_file(file_path, f"Create {username}", json_str)
            
    except Exception as e:
        st.error(f"⚠️ Lỗi khi lưu: {e}")