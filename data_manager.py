import json
import streamlit as st
from github import Github, GithubException

# ==============================================
# CẤU HÌNH KẾT NỐI (Đã điền sẵn tên Repo của bạn)
# ==============================================
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = "anhhieuanhhieu2312-bot/meo-con-bot" # Tên chính xác từ ảnh bạn gửi
DATA_FOLDER = "data"

def get_repo():
    """Kết nối tới kho GitHub và báo lỗi nếu thiếu Token"""
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
    """Tải dữ liệu. Nếu lỗi thì trả về rỗng để app không bị sập"""
    if not username: return {"sessions": {}, "current_session": ""}
    
    file_path = f"{DATA_FOLDER}/{username}.json"
    
    try:
        repo = get_repo()
        if repo:
            contents = repo.get_contents(file_path)
            json_content = contents.decoded_content.decode("utf-8")
            data = json.loads(json_content)
            # Đảm bảo cấu trúc dữ liệu luôn đúng
            if "sessions" not in data: data["sessions"] = {}
            return data
    except Exception as e:
        # Lỗi này thường do file chưa tồn tại (người dùng mới), không sao cả
        print(f"Chưa có dữ liệu cũ hoặc lỗi tải: {e}")
        pass

    return {"sessions": {}, "current_session": ""}

def save_data(username, local_data):
    """
    Lưu dữ liệu với cơ chế 'SMART MERGE' (Hợp nhất thông minh)
    để không bao giờ bị mất dữ liệu cũ.
    """
    if not username: return
    
    file_path = f"{DATA_FOLDER}/{username}.json"
    repo = get_repo()
    if not repo: return

    try:
        # BƯỚC 1: Cố gắng lấy dữ liệu đang nằm trên GitHub về trước
        try:
            contents = repo.get_contents(file_path)
            remote_json = contents.decoded_content.decode("utf-8")
            remote_data = json.loads(remote_json)
        except:
            remote_data = {"sessions": {}}

        # BƯỚC 2: HỢP NHẤT (MERGE)
        # Lấy tất cả cuộc trò chuyện cũ từ GitHub + Cuộc trò chuyện mới từ Local
        # Nếu trùng ID, ưu tiên dữ liệu mới nhất từ Local
        if "sessions" not in remote_data:
            remote_data["sessions"] = {}
            
        # Cập nhật danh sách session
        remote_data["sessions"].update(local_data.get("sessions", {}))
        
        # Cập nhật session đang chọn
        remote_data["current_session"] = local_data.get("current_session")

        # BƯỚC 3: Chuẩn bị nội dung để lưu
        json_str = json.dumps(remote_data, ensure_ascii=False, indent=4)
        
        # BƯỚC 4: Ghi đè file an toàn
        try:
            repo.update_file(contents.path, f"MeoBot saving for {username}", json_str, contents.sha)
            # st.toast("✅ Đã lưu lên mây!", icon="☁️") # Bỏ comment nếu muốn hiện thông báo
        except GithubException as e:
            # Nếu file chưa tồn tại thì tạo mới
            repo.create_file(file_path, f"MeoBot create for {username}", json_str)
            
    except Exception as e:
        st.error(f"⚠️ Lỗi khi lưu dữ liệu: {e}")