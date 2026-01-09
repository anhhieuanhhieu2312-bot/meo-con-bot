import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Meo Con Chatbot", page_icon="🐱")
st.title("🐱 Meo Con Tinh Nghịch")

# --- CẤU HÌNH API GEMINI ---
# Bạn hãy thay mã API của bạn vào giữa dấu ngoặc kép bên dưới
api_key = "AIzaSyCKSwpKmQX6L8jE3tpNertyOmCkglP5us8"
genai.configure(api_key=api_key)

# Khởi tạo model
# Sửa dòng này:
# Sử dụng bản 2.5 Flash nhanh và ổn định nhất trong list của bạn
# Sửa thành gemini-1.5-flash (Bản ổn định, miễn phí nhiều)
# Chọn model gemini-2.0-flash (Có trong danh sách của bạn)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- QUẢN LÝ LỊCH SỬ CHAT (TRÍ NHỚ) ---
# Kiểm tra xem trong phiên làm việc (session) đã có cuộc trò chuyện nào chưa
# Nếu chưa, ta tạo mới một cuộc trò chuyện với Gemini
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- HIỂN THỊ LỊCH SỬ CHAT CŨ ---
# Mỗi khi bạn nhấn Enter, Streamlit sẽ chạy lại code từ đầu.
# Đoạn này giúp vẽ lại những tin nhắn cũ để không bị mất đi.
for message in st.session_state.chat_session.history:
    # Gemini dùng role là "user" hoặc "model". Streamlit cần "user" hoặc "assistant"
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- XỬ LÝ KHI BẠN NHẬP TIN NHẮN MỚI ---
# Hàm st.chat_input sẽ tạo ra ô nhập liệu ở dưới cùng màn hình
if prompt := st.chat_input("Kể chuyện cho tớ nghe đi..."):
    
    # 1. Hiển thị tin nhắn của BẠN lên màn hình ngay lập tức
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Gửi qua cho Gemini xử lý
    try:
        response = st.session_state.chat_session.send_message(prompt)
        
        # 3. Hiển thị câu trả lời của MEO CON
        with st.chat_message("assistant"):
            st.markdown(response.text)
            
    except Exception as e:
        st.error(f"Meo Con đang bị ốm (Lỗi kết nối): {e}")