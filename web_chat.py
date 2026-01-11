import streamlit as st
from groq import Groq
import styles 
import data_manager
import uuid
import re 
import os 
from datetime import datetime
import streamlit as st
# Lấy API key từ kho bảo mật (Secrets)
# ... (các dòng import ở trên) ...

# Thiết lập giao diện
st.markdown("""
<style>
    /* ... (Các code CSS cũ của bạn giữ nguyên, ví dụ hình nền v.v...) ... */

    /* DÁN ĐOẠN CODE MỚI VÀO ĐÂY NHÉ */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
        color: #000000 !important;
    }
    .stChatMessage p {
        color: #000000 !important;
    }
    .stApp {
        background-color: #ffffff !important; /* Dòng này đảm bảo nền trắng */
    }

</style>
""", unsafe_allow_html=True)


# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="meo meo đây...", page_icon="🐾")
styles.apply_custom_style()

# --- CẤU HÌNH API ---
import streamlit as st

# Lấy API key từ kho bảo mật (Secrets)
api_key = st.secrets["GROQ_API_KEY"]
if not api_key or "gsk_" not in api_key:
    st.error("⚠️ Chưa có API Key Groq!")
    st.stop()
client = Groq(api_key=api_key)


# ==========================================
# 1. KHAI BÁO BIẾN & CÀI ĐẶT
# ==========================================

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
# 2. LOGIC ĐĂNG NHẬP (ĐÃ NÂNG CẤP AUTO-LOGIN)
# ==========================================

# [MỚI] Kiểm tra URL xem có lưu tên người dùng không
if 'current_user' not in st.session_state:
    # Nếu trên thanh địa chỉ có ?user=TenBan, tự động lấy tên đó vào
    if "user" in st.query_params:
        st.session_state['current_user'] = st.query_params["user"]
    else:
        st.session_state['current_user'] = None

# Nếu vẫn chưa có người dùng, hiện màn hình đăng nhập
if not st.session_state['current_user']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🐾 Xin chào!")
        st.write("Tên bạn là gì nhỉ?")
        username_input = st.text_input("Tên hoặc Biệt danh:", key="login_input")
        
        if st.button("Bắt đầu trò chuyện 🌸"):
            if username_input.strip():
                # Lưu vào Session
                st.session_state['current_user'] = username_input.strip()
                # [MỚI] Lưu vào URL để F5 không bị mất
                st.query_params["user"] = username_input.strip()
                
                # Load dữ liệu
                user_data = data_manager.load_data(st.session_state['current_user'])
                st.session_state['history_data'] = user_data
                st.rerun()
            else:
                st.warning("Bạn chưa nhập tên kìa!")
    st.stop()

# ==========================================
# 3. QUẢN LÝ LỊCH SỬ CHAT
# ==========================================
# Đảm bảo dữ liệu được load nếu auto-login
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = data_manager.load_data(st.session_state['current_user'])

history = st.session_state['history_data']

if not history['sessions']:
    new_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%d/%m %H:%M")
    history['sessions'][new_id] = {"title": f"Trò chuyện {timestamp}", "messages": []}
    history['current_session'] = new_id
    data_manager.save_data(st.session_state['current_user'], history)

if not history.get('current_session'):
    history['current_session'] = list(history['sessions'].keys())[0]

# --- SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {st.session_state['current_user']}")
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True, key="new_chat"):
        new_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        history['sessions'][new_id] = {"title": f"Trò chuyện {timestamp}", "messages": []}
        history['current_session'] = new_id
        data_manager.save_data(st.session_state['current_user'], history)
        st.rerun()

    st.divider()
    st.write("📜 **Lịch sử:**")
    session_ids = list(history['sessions'].keys())
    for sess_id in reversed(session_ids):
        sess_data = history['sessions'][sess_id]
        btn_type = "primary" if sess_id == history['current_session'] else "secondary"
        if st.button(sess_data['title'], key=sess_id, type=btn_type, use_container_width=True):
            history['current_session'] = sess_id
            st.rerun()
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất"):
        # [MỚI] Xóa thông tin khi đăng xuất
        st.session_state['current_user'] = None
        st.query_params.clear() # Xóa trên URL
        st.rerun()

# ==========================================
# 4. HIỂN THỊ VÀ XỬ LÝ CHAT
# ==========================================
current_id = history['current_session']
current_session_data = history['sessions'][current_id]

# --- GIAO DIỆN CHÍNH (Sửa lại để có nút Chat mới ngay tiêu đề) ---
col_header_1, col_header_2 = st.columns([5, 1])
with col_header_1:
    st.title("meo meo đây... 🐾") 
with col_header_2:
    st.markdown("<br>", unsafe_allow_html=True) # Căn chỉnh cho nút xuống thấp chút
    if st.button("➕", help="Tạo cuộc trò chuyện mới"):
        new_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        history['sessions'][new_id] = {"title": f"Trò chuyện {timestamp}", "messages": []}
        history['current_session'] = new_id
        data_manager.save_data(st.session_state['current_user'], history)
        st.rerun()

# --- HIỂN THỊ TIN NHẮN CŨ ---
for msg in current_session_data['messages']:
    avatar_icon = user_avatar if msg["role"] == "user" else bot_avatar
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# --- XỬ LÝ TIN NHẮN MỚI ---
if prompt := st.chat_input("Tâm sự với meo đi..."):
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)
    current_session_data['messages'].append({"role": "user", "content": prompt})

    # Ngữ cảnh
    user_name = st.session_state.get('current_user', 'Bạn')
    personal_context = f"[THÔNG TIN]: Người dùng tên là '{user_name}'. Hãy gọi là '{user_name}' hoặc 'Cậu'."
    long_term_context = get_long_term_memory(history)
    full_system_prompt = base_system_prompt + "\n" + personal_context + "\n" + long_term_context

    recent_messages = current_session_data['messages'][-50:]
    api_messages = [{"role": "system", "content": full_system_prompt}] + recent_messages

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
            
            current_session_data['messages'].append({"role": "assistant", "content": final_clean_response})
            if len(current_session_data['messages']) == 2:
                current_session_data['title'] = (prompt[:30] + "...") if len(prompt) > 30 else prompt
            data_manager.save_data(st.session_state['current_user'], history)
        except Exception as e:
            st.error(f"⚠️ Meo đang ngủ gật: {e}")