import streamlit as st
from groq import Groq
import styles 
import data_manager
import uuid
import re 
import os 
from datetime import datetime

# ==========================================
# 0. CẤU HÌNH GIAO DIỆN & CSS (Fix lỗi hiển thị Mobile)
# ==========================================
st.set_page_config(page_title="meo meo đây...", page_icon="🐾")

# Thiết lập giao diện CSS
st.markdown("""
<style>
    /* Ẩn Sidebar mặc định của Streamlit để dùng Menu riêng */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Ép toàn bộ chữ tiêu đề, đoạn văn, nhãn dán thành màu đen */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
        color: #000000 !important;
    }

    /* Ép màu chữ trong khung chat */
    .stChatMessage p {
        color: #000000 !important;
    }

    /* Đảm bảo nền trắng */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Tùy chỉnh nút bấm cho đẹp hơn */
    .stButton button {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

styles.apply_custom_style()

# ==========================================
# 1. CẤU HÌNH API & BIẾN
# ==========================================

# Lấy API key từ kho bảo mật (Secrets)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Chưa cấu hình API Key trong Secrets!")
    st.stop()

if not api_key or "gsk_" not in api_key:
    st.error("⚠️ API Key không hợp lệ!")
    st.stop()

client = Groq(api_key=api_key)

# --- CẤU HÌNH AVATAR ---
user_avatar = "avatar.png" if os.path.exists("avatar.png") else "🌸"
bot_avatar = "bot_avatar.png" if os.path.exists("bot_avatar.png") else "🐱"

# --- LỜI NHẮC HỆ THỐNG (ME0 MEO) ---
base_system_prompt = """
Bạn là "meo meo" - một người bạn tri kỷ, sâu sắc và cực kỳ tâm lý dành cho phái nữ.

NHIỆM VỤ CỦA BẠN:
1.  **Cách xưng hô:** Luôn xưng là "meo" (viết thường) hoặc "tớ". Tuyệt đối không xưng "Mèo" hay "Tôi".
2.  **Tuyệt đối KHÔNG mô tả hành động**. Hãy thể hiện cảm xúc qua lời nói.
3.  **Đừng trả lời cụt lủn.** Hãy trả lời dài hơn, đầy đủ câu chữ, diễn giải ý tứ rõ ràng.
4.  **Phong cách:** Nhẹ nhàng, ấm áp, đôi khi dí dỏm nhưng luôn sâu lắng.

Ví dụ: 
- Thay vì nói: "Ừ, buồn nhỉ."
- Hãy nói: "Nghe cậu kể mà meo cũng thấy chạnh lòng theo. Chắc hẳn cậu đã phải chịu đựng nhiều lắm mới nói ra được những lời này. Cậu có muốn kể chi tiết hơn về chuyện đó không? meo vẫn ở đây nghe cậu này 🌿."

QUAN TRỌNG: Hãy sử dụng đa dạng các icon dễ thương: 💖, 💗, 🐱, 😽, 🌸, 🌷, ✨, 🌟.
"""

# --- HÀM HỖ TRỢ ---
def get_long_term_memory(history_data):
    try:
        sessions = history_data.get('sessions', {})
        if not sessions: return ""
        recent_titles = [f"- {sessions[k].get('title', 'Không rõ')}" for k in list(sessions.keys())[-10:]]
        memory_text = "\n".join(recent_titles)
        return f"\n[GHI CHÚ KÝ ỨC - CÁC CHỦ ĐỀ TỪNG NÓI]:\n{memory_text}\n"
    except Exception: return ""

def clean_text(text):
    return re.sub(r'\*.*?\*', '', text).strip()

# ==========================================
# 2. LOGIC ĐĂNG NHẬP (AUTO-LOGIN)
# ==========================================

if 'current_user' not in st.session_state:
    if "user" in st.query_params:
        st.session_state['current_user'] = st.query_params["user"]
    else:
        st.session_state['current_user'] = None

# Màn hình đăng nhập
if not st.session_state['current_user']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🐾 Xin chào!")
        st.write("Tên bạn là gì nhỉ?")
        username_input = st.text_input("Tên hoặc Biệt danh:", key="login_input")
        
        if st.button("Bắt đầu trò chuyện 🌸", use_container_width=True):
            if username_input.strip():
                st.session_state['current_user'] = username_input.strip()
                st.query_params["user"] = username_input.strip()
                user_data = data_manager.load_data(st.session_state['current_user'])
                st.session_state['history_data'] = user_data
                st.rerun()
            else:
                st.warning("Bạn chưa nhập tên kìa!")
    st.stop()

# ==========================================
# 3. QUẢN LÝ DỮ LIỆU & LỊCH SỬ
# ==========================================
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = data_manager.load_data(st.session_state['current_user'])

history = st.session_state['history_data']

# Tạo phiên chat đầu tiên nếu chưa có
if not history['sessions']:
    new_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%d/%m %H:%M")
    history['sessions'][new_id] = {"title": f"Trò chuyện {timestamp}", "messages": []}
    history['current_session'] = new_id
    data_manager.save_data(st.session_state['current_user'], history)

if not history.get('current_session'):
    history['current_session'] = list(history['sessions'].keys())[0]

# ==========================================
# 4. GIAO DIỆN CHÍNH (MENU & CHAT)
# ==========================================

# --- TIÊU ĐỀ ---
st.title("meo meo đây... 🐾")

# --- MENU CHỨC NĂNG (Dạng xổ xuống - Tối ưu cho Mobile) ---
with st.expander(f"☰ MENU CỦA {st.session_state['current_user'].upper()} (Lịch sử & Cài đặt)", expanded=False):
    
    # Hai nút chức năng chính: Chat mới & Đăng xuất
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

    # Hiển thị danh sách lịch sử (Mới nhất lên đầu)
    # Sắp xếp danh sách
    sorted_sessions = sorted(
        history['sessions'].items(),
        key=lambda x: x[1].get('last_updated', ''), 
        reverse=True
    )
    # Nếu chưa có last_updated thì sắp xếp theo key (thời gian tạo giả định)
    if not sorted_sessions:
        sorted_sessions = list(history['sessions'].items())

    for s_id, s_data in sorted_sessions:
        display_name = s_data['title']
        # Đánh dấu cuộc trò chuyện đang xem
        if s_id == history['current_session']:
            display_name = f"👉 {display_name}"
            btn_type = "primary"
        else:
            btn_type = "secondary"
        
        if st.button(display_name, key=f"hist_{s_id}", type=btn_type, use_container_width=True):
            history['current_session'] = s_id
            st.rerun()

# --- XÁC ĐỊNH PHIÊN CHAT HIỆN TẠI ---
current_id = history['current_session']
current_session_data = history['sessions'][current_id]

# --- HIỂN THỊ TIN NHẮN CŨ ---
for msg in current_session_data['messages']:
    avatar_icon = user_avatar if msg["role"] == "user" else bot_avatar
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# --- XỬ LÝ TIN NHẮN MỚI ---
if prompt := st.chat_input("Tâm sự với meo đi..."):
    # 1. Hiển thị tin nhắn người dùng ngay lập tức
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)
    current_session_data['messages'].append({"role": "user", "content": prompt})

    # 2. Chuẩn bị ngữ cảnh cho Bot
    user_name = st.session_state.get('current_user', 'Bạn')
    personal_context = f"[THÔNG TIN]: Người dùng tên là '{user_name}'. Hãy gọi là '{user_name}' hoặc 'Cậu'."
    long_term_context = get_long_term_memory(history)
    full_system_prompt = base_system_prompt + "\n" + personal_context + "\n" + long_term_context

    recent_messages = current_session_data['messages'][-50:]
    api_messages = [{"role": "system", "content": full_system_prompt}] + recent_messages

    # 3. Gọi API và Stream câu trả lời
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
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            final_clean_response = clean_text(full_response)
            message_placeholder.markdown(final_clean_response)
            
            # 4. Lưu lại câu trả lời
            current_session_data['messages'].append({"role": "assistant", "content": final_clean_response})
            
            # Đặt tên tiêu đề nếu là tin nhắn đầu tiên
            if len(current_session_data['messages']) == 2:
                current_session_data['title'] = (prompt[:30] + "...") if len(prompt) > 30 else prompt
            
            # Cập nhật thời gian update
            current_session_data['last_updated'] = datetime.now().isoformat()
            
            # Lưu xuống file
            data_manager.save_data(st.session_state['current_user'], history)
            
        except Exception as e:
            st.error(f"⚠️ Meo đang ngủ gật: {e}")