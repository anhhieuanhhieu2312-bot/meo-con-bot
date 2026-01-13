import streamlit as st
import base64
import os
from PIL import Image
from io import BytesIO

# --- GIỮ NGUYÊN HÀM XỬ LÝ ẢNH (VÌ ĐANG CHẠY RẤT TỐT) ---
def get_optimized_base64(image_path):
    try:
        img = Image.open(image_path)
        img.thumbnail((80, 80)) 
        buffered = BytesIO()
        img.save(buffered, format="PNG", optimize=True)
        return base64.b64encode(buffered.getvalue()).decode().replace("\n", "")
    except Exception:
        return None

def get_sticker_css():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    stickers_dir = os.path.join(current_dir, "stickers")
    
    try:
        # Lấy file ảnh
        files = [f for f in os.listdir(stickers_dir) if f.lower().endswith(('.png', '.jpg'))]
        
        # --- THAY ĐỔI: NHÂN BẢN DANH SÁCH ẢNH ĐỂ LẤP ĐẦY MÀN HÌNH ---
        # Nếu ít ảnh quá thì nhân 3 lên để dùng lại, lấy tối đa 20 sticker
        files = (files * 3)[:20] 
    except:
        return ""

    bg_images = []
    
    # --- THAY ĐỔI: DANH SÁCH VỊ TRÍ DÀY ĐẶC HƠN (15 vị trí) ---
    positions = [
        "2% 5%",   "20% 5%",  "80% 5%",   "98% 5%",   # Hàng trên cùng
        "10% 30%", "90% 30%",                         # Hàng lửng trên
        "5% 50%",  "95% 50%",                         # Hàng giữa (tránh che đoạn chat chính)
        "15% 70%", "85% 70%",                         # Hàng lửng dưới
        "2% 95%",  "25% 90%", "50% 95%", "75% 90%", "98% 95%" # Hàng dưới đáy
    ]
    
    valid_count = 0
    # Lặp qua từng file để xử lý
    for i, filename in enumerate(files):
        # Nếu hết vị trí để đặt thì dừng lại
        if valid_count >= len(positions): break
            
        path = os.path.join(stickers_dir, filename)
        b64 = get_optimized_base64(path)
        
        if b64:
            bg_images.append(f"url('data:image/png;base64,{b64}')")
            valid_count += 1
            
    if not bg_images: return ""

    css_images = ", ".join(bg_images)
    # Cắt lấy số lượng vị trí tương ứng với số ảnh xử lý được
    css_positions = ", ".join(positions[:valid_count])

    return f"""
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: {css_images};
            background-position: {css_positions};
            background-repeat: no-repeat;
            background-size: 80px; /* Kích thước ảnh */
            opacity: 0.5;
            z-index: 0;
            pointer-events: none;
        }}
    """

# --- PHẦN CHỈNH SỬA MÀU SẮC MỚI ---
def apply_custom_style():
    sticker_style = get_sticker_css()
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Nunito', sans-serif;
        }}
        
        /* 1. NỀN CHÍNH: Màu hồng phấn siêu nhạt (Dịu mắt hơn nhiều) */
        [data-testid="stAppViewContainer"] {{
            background-color: #FFF5F7; 
        }}
        
        /* 2. CỘT BÊN TRÁI (SIDEBAR): Màu hồng kem, tách biệt nhẹ nhàng */
        [data-testid="stSidebar"] {{
            background-color: #FFF0F5;
            border-right: 1px solid #FFE4E1;
        }}
        
        /* Chữ trong Sidebar */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #D65A72 !important;
        }}

        /* 3. KHUNG NHẬP CHAT: Trang điểm cho đẹp hơn */
        .stChatInput input {{
            background-color: #FFFFFF !important; /* Nền trắng sạch */
            border: 2px solid #FFC0CB !important; /* Viền hồng */
            color: #4A4A4A !important; /* Chữ xám đậm dễ đọc */
            border-radius: 25px !important; /* Bo tròn dễ thương */
            padding-left: 15px !important;
        }}
        
        /* Hiệu ứng khi bấm vào khung chat (Phát sáng nhẹ) */
        .stChatInput input:focus {{
            border-color: #FF69B4 !important;
            box-shadow: 0 0 10px rgba(255, 182, 193, 0.5) !important;
        }}

        /* STICKER (Giữ nguyên) */
        {sticker_style}
        
        /* Lớp nội dung (đè lên sticker) */
        [data-testid="stVerticalBlock"] {{
            z-index: 1;
            position: relative;
        }}
        
        /* Ẩn Header mặc định */
        header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)