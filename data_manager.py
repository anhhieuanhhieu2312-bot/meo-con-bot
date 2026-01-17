import json
import os
import streamlit as st
from github import Github, GithubException

# Cấu hình GitHub
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = "anhhieuanhhieu2312-bot/meo-con-bot" # Tên kho của bạn (Username/Repo)
DATA_FOLDER = "data"

def get_repo():
    """Kết nối tới kho GitHub"""
    if not GITHUB_TOKEN:
        return None
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def load_data(username):
    """Tải dữ liệu từ GitHub xuống"""
    file_path = f"{DATA_FOLDER}/{username}.json"
    
    # 1. Thử tải từ GitHub trước (Ưu tiên dữ liệu trên mây)
    try:
        repo = get_repo()
        if repo:
            contents = repo.get_contents(file_path)
            json_content = contents.decoded_content.decode("utf-8")
            return json.loads(json_content)
    except Exception as e:
        # Nếu chưa có file trên GitHub hoặc lỗi mạng, bỏ qua
        pass

    # 2. Nếu không có trên GitHub, trả về dữ liệu mới
    return {"sessions": {}, "current_session": ""}

def save_data(username, data):
    """Lưu dữ liệu thẳng lên GitHub"""
    file_path = f"{DATA_FOLDER}/{username}.json"
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    
    try:
        repo = get_repo()
        if not repo:
            return # Không có token thì thôi
            
        try:
            # Kiểm tra xem file đã tồn tại chưa để Update
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, f"Update chat history for {username}", json_str, contents.sha)
        except GithubException as e:
            if e.status == 404:
                # Nếu file chưa có thì Tạo mới
                repo.create_file(file_path, f"Create chat history for {username}", json_str)
            else:
                print(f"Lỗi GitHub: {e}")
                
    except Exception as e:
        print(f"Không thể lưu lên GitHub: {e}")