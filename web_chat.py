import streamlit as st
from groq import Groq
import styles 
import data_manager
import uuid
import re 
import os 
from datetime import datetime

# ==========================================
# 0. CẤU HÌNH GIAO DIỆN & CSS
# ==========================================
st.set_page_config(page_title="meo meo đây...", page_icon="🐾")

# Thiết lập giao diện CSS (Giữ nguyên style bạn thích)
st.markdown("""
<style>
    /* Ẩn Sidebar mặc định */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Ép màu chữ đen */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
        color: #000000 !important;
    }
    .stChatMessage p {
        color: #000000 !important;
    }

    /* Nền trắng */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Nút bấm bo tròn */
    .stButton button {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

try:
    styles.apply_custom_style()
except:
    pass

# ==========================================
# 1. CẤU HÌNH API & BIẾN
# ==========================================

# Lấy API key an toàn
try:
        api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Chưa cấu hình API Key trong Secrets của Streamlit Cloud!")
    st.stop()

client = Groq(api_key=api_key)

# Cấu hình Avatar
user_avatar = "avatar.png" if os.path.exists("avatar.png") else "🌸"
bot_avatar = "bot_avatar.png" if os.path.exists("bot_avatar.png") else "🐱"

# Prompt hệ thống
base_system_prompt = """
Bạn là "meo meo" - một người bạn tri kỷ, sâu sắc và cực kỳ tâm lý dành cho phái nữ.

NHIỆM VỤ CỦA BẠN:
1.  Cách xưng hô: Luôn xưng là "meo" (viết thường) hoặc "tớ". Tuyệt đối không xưng "Mèo" hay "Tôi".
2.  Tuyệt đối KHÔNG mô tả hành động. Hãy thể hiện cảm xúc qua lời nói.
3.  Đừng trả lời cụt lủn. Hãy trả lời dài hơn, đầy đủ câu chữ, diễn giải ý tứ rõ ràng.
4.  Phong cách: Nhẹ nhàng, ấm áp, đôi khi dí dỏm nhưng luôn sâu lắng.
5.  Sử dụng icon dễ thương: 💖, 💗, 🐱, 😽, 🌸, 🌷, ✨, 🌟.
"""

def get_long_term_memory(history_data):
    try:
        sessions = history_data.get('sessions', {})
        if not sessions: return ""
        recent_titles = [f"- {sessions[k].get('title', 'Không rõ')}" for k in list(sessions.keys())[-10:]]
        memory_text = "\n".join(recent_titles)
        return f"\n[GHI CHÚ KÝ ỨC]:\n{memory_text}\n"
    except Exception: return ""

def clean_text(text):
    return re.sub(r'\*.*?\*', '', text).strip()

# ==========================================
# 2. LOGIC ĐĂNG NHẬP (Đã sửa lỗi lưu data)
# ==========================================

if 'current_user' not in st.session_state:
    if "user" in st.query_params:
        st.session_state['current_user'] = st.query_params["user"]
    else:
        st.session_state['current_user'] = None

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state['current_user']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🐾 Xin chào!")
        st.write("Tên bạn là gì nhỉ?")
        username_input = st.text_input("Tên hoặc Biệt danh:", key="login_input")
        
        if st.button("Bắt đầu trò chuyện 🌸", use_container_width=True):
            if username_input.strip():
                user_name = username_input.strip()
                
                # 1. Lưu tên vào session
                st.session_state['current_user'] = user_name
                st.query_params["user"] = user_name
                
                # 2. Load dữ liệu và KHỞI TẠO NGAY nếu chưa có
                user_data = data_manager.load_data(user_name)
                
                if not user_data.get('sessions'):
                    # Tạo phiên chat đầu tiên ngay lập tức
                    new_id = str(uuid.uuid4())
                    timestamp = datetime.now().strftime("%d/%m %H:%M")
                    user_data['sessions'] = {
                        new_id: {"title": f"Trò chuyện {timestamp}", "messages": []}
                    }
                    user_data['current_session'] = new_id
                    
                    # LƯU XUỐNG FILE NGAY (Fix lỗi không lưu được trên Cloud)
                    data_manager.save_data(user_name, user_data)
                
                st.session_state['history_data'] = user_data
                st.rerun()
            else:
                st.warning("Bạn chưa nhập tên kìa!")
    
    # [QUAN TRỌNG] Dừng code tại đây nếu chưa đăng nhập
    st.stop()

# ==========================================
# 3. LOGIC CHAT (Chỉ chạy khi ĐÃ Đăng nhập)
# ==========================================

# Load dữ liệu nếu chưa có trong session
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = data_manager.load_data(st.session_state['current_user'])

history = st.session_state['history_data']

# Phòng hờ: Nếu load lên mà vẫn chưa có session nào (hiếm gặp), tạo lại
if not history.get('sessions'):
    new_id = str(uuid.uuid4())
    history['sessions'] = {new_id: {"title": "Trò chuyện mới", "messages": []}}
    history['current_session'] = new_id
    data_manager.save_data(st.session_state['current_user'], history)

if not history.get('current_session'):
    history['current_session'] = list(history['sessions'].keys())[0]

# --- GIAO DIỆN CHÍNH ---
st.title("meo meo đây... 🐾")

# [SỬA LỖI] Xử lý tên hiển thị an toàn cho Menu
current_name = st.session_state.get('current_user', "KHÁCH")
safe_display_name = current_name.upper() if current_name else "KHÁCH"

with st.expander(f"☰ MENU CỦA {safe_display_name} (Lịch sử & Cài đặt)", expanded=False):
    col_menu_1, col_menu_2 = st.columns(2)
    
    with col_menu_1:
        if st.button("➕ Chat Mới", use_container_width=True):
            new_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%d/%m %H:%M")
            history['sessions'][new_id] = {"title": f"Trò chuyện {timestamp}", "messages": []}
            history['current_session'] = new_id
            data_manager.save_data(st.session_state['current_user'], history)
            st.rerun()
            
    with col_menu_2:
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state['current_user'] = None
            st.query_params.clear()
            st.rerun()

    st.markdown("---")
    st.markdown("**📜 Lịch sử trò chuyện:**")

    # Sắp xếp lịch sử
    sorted_sessions = sorted(
        history['sessions'].items(),
        key=lambda x: x[1].get('last_updated', ''), 
        reverse=True
    )
    if not sorted_sessions:
        sorted_sessions = list(history['sessions'].items())

    for s_id, s_data in sorted_sessions:
        display_name = s_data.get('title', 'Cuộc trò chuyện')
        btn_type = "primary" if s_id == history['current_session'] else "secondary"
        
        if s_id == history['current_session']:
            display_name = f"👉 {display_name}"
        
        if st.button(display_name, key=f"hist_{s_id}", type=btn_type, use_container_width=True):
            history['current_session'] = s_id
            st.rerun()

# --- HIỂN THỊ HỘI THOẠI ---
current_id = history['current_session']
current_session_data = history['sessions'][current_id]

for msg in current_session_data['messages']:
    avatar_icon = user_avatar if msg["role"] == "user" else bot_avatar
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# --- XỬ LÝ NHẬP TIN NHẮN ---
if prompt := st.chat_input("Tâm sự với meo đi..."):
    # 1. Hiển thị User
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)
    current_session_data['messages'].append({"role": "user", "content": prompt})

    # 2. Chuẩn bị Context
    user_real_name = st.session_state.get('current_user', 'Bạn')
    full_system_prompt = base_system_prompt + \
                         f"\n[USER INFO]: Tên người dùng là '{user_real_name}'.\n" + \
                         get_long_term_memory(history)

    recent_messages = current_session_data['messages'][-20:] # Lấy 20 tin gần nhất để tiết kiệm token
    api_messages = [{"role": "system", "content": full_system_prompt}] + recent_messages

    # 3. Gọi API
    with st.chat_message("assistant", avatar=bot_avatar):
        message_placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=0.7, 
                max_tokens=1024,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            final_clean_response = clean_text(full_response)
            message_placeholder.markdown(final_clean_response)
            
            # 4. Lưu Bot Response
            current_session_data['messages'].append({"role": "assistant", "content": final_clean_response})
            
            # Đặt tiêu đề nếu mới bắt đầu
            if len(current_session_data['messages']) <= 2:
                short_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
                current_session_data['title'] = short_title
            
            current_session_data['last_updated'] = datetime.now().isoformat()
            data_manager.save_data(st.session_state['current_user'], history)
            
        except Exception as e:
            st.error(f"Meo đang mất kết nối: {e}")