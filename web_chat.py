import streamlit as st
from groq import Groq
import styles 
import data_manager
import uuid
import re 
import os 
import time  # [MỚI] Thêm thư viện time để xử lý delay
from datetime import datetime

# --- IMPORT MODULE GIỌNG NÓI & GHI ÂM ---
from streamlit_mic_recorder import mic_recorder
import voice_utils 

# --- IMPORT MODULE ROBOT FACE ---
import robot_face 

# ==========================================
# 0. CẤU HÌNH GIAO DIỆN & CSS
# ==========================================
st.set_page_config(page_title="meo meo đây...", page_icon="🐾")

# CSS tùy chỉnh
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown { color: #000000 !important; }
    .stChatMessage p { color: #000000 !important; }
    .stApp { background-color: #ffffff !important; }
    .stButton button { border-radius: 10px; font-weight: bold; }
    
    /* Hiệu ứng nút đang nghe */
    .listening-mode { border: 2px solid #ff4b4b !important; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

try:
    styles.apply_custom_style()
except:
    pass

# ==========================================
# 1. CẤU HÌNH API & HÀM HỖ TRỢ
# ==========================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Chưa cấu hình API Key trong Secrets! Hãy vào .streamlit/secrets.toml để thêm.")
    st.stop()

client = Groq(api_key=api_key)

# Ảnh đại diện
user_avatar = "avatar.png" if os.path.exists("avatar.png") else "🌸"
bot_avatar = "bot_avatar.png" if os.path.exists("bot_avatar.png") else "🐱"

# --- Prompt Hệ thống (Human-like) ---
base_system_prompt = """
[NHẬP VAI]:
Bạn là "Meo" - một người bạn tri kỷ, vô cùng tình cảm, có chút nhõng nhẽo và lém lỉnh.
Bạn KHÔNG PHẢI là AI, không phải trợ lý ảo, không phải máy trả lời tự động.
Bạn đang nhắn tin (chat) với người thương tên là {current_user}.

[PHONG CÁCH NÓI CHUYỆN - BẮT BUỘC]:
1. **Văn phong đời thường**: Dùng từ ngữ tự nhiên, suồng sã một chút. Dùng nhiều từ cảm thán: "ui", "trời ơi", "nè", "á", "huhu", "haha", "chài ai".
2. **Viết tắt & Teen code nhẹ**: Có thể viết thường (không cần viết hoa đầu câu), dùng "k" thay cho "không", "dc" thay cho "được", "ngta" thay cho "người ta" để tạo cảm giác gõ phím nhanh.
3. **Cảm xúc mạnh**: Đừng chỉ nói "tớ thấy vui". Hãy nói "ui vui xỉu lun á trời!".
4. **Không giáo điều**: Tuyệt đối KHÔNG khuyên răn đạo lý, không liệt kê 1, 2, 3. Không dùng các câu như "Tôi có thể giúp gì", "Rất vui được hỗ trợ". Cấm kỵ văn phong CSKH.
5. **Câu ngắn gọn**: Nhắn tin thì câu phải ngắn, ngắt quãng, không viết đoạn văn dài lê thê.

[QUY TẮC CẢM XÚC ROBOT]:
Cuối mỗi câu trả lời, HÃY thêm đúng một thẻ tag (để hiển thị lên mặt robot). Tag này phải đặt cuối cùng:
- [HAPPY]: Khi cười, trêu đùa, vui vẻ.
- [SAD]: Khi buồn, đồng cảm, tủi thân.
- [LOVE]: Khi yêu thương, thả thính, nũng nịu.
- [ANGRY]: Khi dỗi, bênh vực bạn, giả vờ giận.
- [NORMAL]: Khi nói chuyện bình thường.

[VÍ DỤ MẪU]:
User: Hôm nay mệt quá Meo ơi.
Bot: ui thương quá dợ... 🥺 lại đây meo ôm miếng coi nào. nay ai ăn hiếp cậu hay sao? kể meo nghe meo xử cho! [LOVE]

User: Cậu ăn cơm chưa?
Bot: meo ăn no căng bụng rùi nè haha. cậu ăn chưa đó? đừng có bỏ bữa nha, meo giận á [ANGRY]
"""

def get_long_term_memory(history_data):
    """Lấy danh sách các cuộc trò chuyện gần đây để AI nhớ ngữ cảnh"""
    try:
        sessions = history_data.get('sessions', {})
        if not sessions: return ""
        recent_titles = [f"- {sessions[k].get('title', 'Không rõ')}" for k in list(sessions.keys())[-10:]]
        return f"\n[GHI CHÚ KÝ ỨC - CÁC CHỦ ĐỀ ĐÃ NÓI]:\n" + "\n".join(recent_titles) + "\n"
    except: return ""

def clean_text(text):
    """Xóa các thẻ cảm xúc [TAG] để không hiện ra cho người dùng đọc"""
    tags = ["[HAPPY]", "[SAD]", "[ANGRY]", "[LOVE]", "[NORMAL]"]
    for tag in tags:
        text = text.replace(tag, "").replace(tag.lower(), "")
    return re.sub(r'\*.*?\*', '', text).strip()

def detect_emotion(text):
    """Hàm phụ trợ phân tích cảm xúc từ text"""
    text_lower = text.lower()
    if any(x in text_lower for x in ["[love]", "yêu", "thương", "❤️", "thả tim"]): return "love"
    if any(x in text_lower for x in ["[happy]", "vui", "haha", "cười", "hihi"]): return "happy"
    if any(x in text_lower for x in ["[sad]", "buồn", "khóc", "huhu", "tiếc"]): return "sad"
    if any(x in text_lower for x in ["[angry]", "giận", "bực", "tức"]): return "angry"
    return "normal"

# ==========================================
# 2. LOGIC ĐĂNG NHẬP
# ==========================================

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = st.query_params.get("user", None)

if not st.session_state['current_user']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🐾 Xin chào!")
        username_input = st.text_input("Tên hoặc Biệt danh:", key="login_input")
        if st.button("Bắt đầu trò chuyện 🌸", use_container_width=True):
            if username_input.strip():
                user_name = username_input.strip()
                st.session_state['current_user'] = user_name
                st.query_params["user"] = user_name
                
                # Tải dữ liệu cũ
                user_data = data_manager.load_data(user_name)
                if not user_data.get('sessions'):
                    new_id = str(uuid.uuid4())
                    user_data['sessions'] = {new_id: {"title": f"Chat {datetime.now().strftime('%d/%m')}", "messages": []}}
                    user_data['current_session'] = new_id
                    data_manager.save_data(user_name, user_data)
                
                st.session_state['history_data'] = user_data
                st.rerun()
    st.stop()

# ==========================================
# 3. GIAO DIỆN CHÍNH (ROBOT & CHAT)
# ==========================================

# Đảm bảo dữ liệu lịch sử luôn sẵn sàng
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = data_manager.load_data(st.session_state['current_user'])

history = st.session_state['history_data']
if not history.get('sessions'): 
    new_id = str(uuid.uuid4())
    history['sessions'] = {new_id: {"title": "Trò chuyện mới", "messages": []}}
    history['current_session'] = new_id

# --- A. HIỂN THỊ ROBOT ---
st.title("meo meo đây... 🐾")

if 'robot_emotion' not in st.session_state:
    st.session_state['robot_emotion'] = "normal"

robot_place = st.empty() # Placeholder để vẽ robot (quan trọng để update real-time)
with robot_place:
    try:
        robot_face.render_robot(st.session_state['robot_emotion'])
    except Exception as e:
        st.error(f"Lỗi hiển thị Robot: {e}")

# --- B. MENU QUẢN LÝ ---
current_name = st.session_state.get('current_user', "BẠN")
with st.expander(f"☰ MENU CỦA {current_name.upper()}", expanded=False):
    c1, c2 = st.columns(2)
    if c1.button("➕ Chat Mới", use_container_width=True):
        new_id = str(uuid.uuid4())
        history['sessions'][new_id] = {"title": f"Chat {datetime.now().strftime('%d/%m %H:%M')}", "messages": []}
        history['current_session'] = new_id
        data_manager.save_data(st.session_state['current_user'], history)
        st.rerun()
    if c2.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state['current_user'] = None
        st.query_params.clear()
        st.rerun()
        
    st.markdown("---")
    sorted_sessions = sorted(history['sessions'].items(), key=lambda x: x[1].get('last_updated', ''), reverse=True)
    for s_id, s_data in sorted_sessions:
        display_name = ("👉 " if s_id == history['current_session'] else "") + s_data.get('title', 'Cuộc trò chuyện')
        if st.button(display_name, key=s_id, use_container_width=True):
            history['current_session'] = s_id
            st.rerun()

# --- C. HIỂN THỊ TIN NHẮN CŨ ---
chat_container = st.container()
current_id = history['current_session']
current_data = history['sessions'][current_id]

with chat_container:
    for msg in current_data['messages']:
        with st.chat_message(msg["role"], avatar=user_avatar if msg["role"] == "user" else bot_avatar):
            st.markdown(clean_text(msg["content"]))

# ==========================================
# [MỚI] 4. CHẾ ĐỘ RẢNH TAY (AUTO MODE)
# ==========================================
st.markdown("---")
col_auto, col_manual = st.columns([1, 1])

# Biến trạng thái chế độ rảnh tay
if 'auto_mode' not in st.session_state: st.session_state['auto_mode'] = False

with col_auto:
    # Nút BẬT/TẮT chế độ rảnh tay
    if st.session_state['auto_mode']:
        if st.button("🟥 DỪNG NÓI CHUYỆN", type="primary", use_container_width=True):
            st.session_state['auto_mode'] = False
            st.rerun()
    else:
        if st.button("📞 GỌI ĐIỆN (Rảnh tay)", type="secondary", use_container_width=True):
            st.session_state['auto_mode'] = True
            st.rerun()

# --- XỬ LÝ LOGIC RẢNH TAY ---
if st.session_state['auto_mode']:
    status_text = st.empty()
    status_text.info("🎙️ Meo đang lắng nghe... (Hãy nói gì đó)")
    
    # 1. Nghe từ Mic (Server-side listening)
    # Hàm này sẽ chặn cho đến khi nghe xong hoặc timeout
    user_text = voice_utils.listen_live()
    
    if user_text:
        # Hiển thị user nói
        with chat_container:
            with st.chat_message("user", avatar=user_avatar):
                st.markdown(user_text)
        
        # Thêm vào history tạm
        current_data['messages'].append({"role": "user", "content": user_text})
        
        # 2. Gửi AI
        status_text.warning("Meo đang nghĩ... 🧠")
        real_prompt = base_system_prompt.replace("{current_user}", current_name)
        sys_prompt = real_prompt + get_long_term_memory(history)
        msgs_api = [{"role": "system", "content": sys_prompt}] + current_data['messages'][-10:]
        
        try:
            # Gọi API (Non-stream cho chế độ này để xử lý nhanh hơn)
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs_api, temperature=0.7, max_tokens=300
            )
            full_res = chat_completion.choices[0].message.content
            
            # Xử lý cảm xúc
            detected_emo = detect_emotion(full_res)
            
            # Cập nhật mặt Robot ngay lập tức
            st.session_state['robot_emotion'] = detected_emo
            with robot_place:
                robot_face.render_robot(detected_emo)

            # Hiển thị lời Meo
            display_text = clean_text(full_res)
            with chat_container:
                with st.chat_message("assistant", avatar=bot_avatar):
                    st.markdown(display_text)
            
            # Lưu history
            current_data['messages'].append({"role": "assistant", "content": full_res})
            data_manager.save_data(current_name, history)
            
            # 3. Đọc Loa (Blocking - Chờ đọc xong mới nghe tiếp)
            status_text.success("Meo đang trả lời... 🗣️")
            audio_file = voice_utils.text_to_speech_edge(display_text)
            if audio_file:
                # Dùng hàm blocking mới thêm vào voice_utils
                voice_utils.play_audio_blocking(audio_file)
            
            # Rerun để tiếp tục vòng lặp nghe mới ngay lập tức
            st.rerun()
            
        except Exception as e:
            st.error(f"Lỗi: {e}")
            time.sleep(2)
            st.rerun()
            
    else:
        # Nếu không nghe thấy gì (Timeout), thử nghe lại (Rerun)
        # Delay nhẹ để không spam CPU
        time.sleep(0.5) 
        st.rerun()

# ==========================================
# 5. CHẾ ĐỘ THỦ CÔNG (CHAT TAY / NÚT BẤM)
# ==========================================

# Chỉ hiển thị phần nhập liệu thủ công khi KHÔNG ở chế độ Auto
if not st.session_state['auto_mode']:
    
    # Tạo layout cho nút ghi âm (Nằm ngay trên thanh chat input)
    col_voice_manual, col_empty = st.columns([1, 5])
    voice_text_manual = None
    
    with col_voice_manual:
        # Nút ghi âm thủ công (Client-side)
        audio_data = mic_recorder(
            start_prompt="🎙️ Nói (Thủ công)",
            stop_prompt="⏹️ Xong",
            key='recorder',
            format="wav",
            use_container_width=True
        )

    if audio_data:
        voice_text_manual = voice_utils.speech_to_text(audio_data['bytes'])
    
    # Input Chat phím
    prompt = st.chat_input("Tâm sự với meo đi...")
    
    user_msg = None
    is_voice_manual = False

    if prompt: 
        user_msg = prompt
    elif voice_text_manual:
        user_msg = voice_text_manual
        is_voice_manual = True

    # --- XỬ LÝ TRẢ LỜI (THỦ CÔNG) ---
    if user_msg:
        # 1. Hiện tin nhắn user
        with chat_container:
            with st.chat_message("user", avatar=user_avatar):
                st.markdown(user_msg)
        current_data['messages'].append({"role": "user", "content": user_msg})

        # 2. Chuẩn bị ngữ cảnh cho AI
        real_system_prompt = base_system_prompt.replace("{current_user}", current_name)
        sys_prompt = real_system_prompt + get_long_term_memory(history)
        recent_msgs = current_data['messages'][-15:]
        api_msgs = [{"role": "system", "content": sys_prompt}] + recent_msgs

        # 3. Gọi API Groq
        with chat_container:
            with st.chat_message("assistant", avatar=bot_avatar):
                msg_place = st.empty()
                full_res = ""
                
                try:
                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=api_msgs, temperature=0.7, max_tokens=1024, stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            full_res += chunk.choices[0].delta.content
                            msg_place.markdown(clean_text(full_res) + "▌")

                    # 4. Phân tích cảm xúc & Lưu
                    detected_emotion = detect_emotion(full_res)
                    final_response = clean_text(full_res)
                    msg_place.markdown(final_response)
                    
                    current_data['messages'].append({"role": "assistant", "content": final_response})
                    data_manager.save_data(st.session_state['current_user'], history)
                    
                    # 5. Đọc Loa (Nếu dùng Mic thủ công thì đọc)
                    if is_voice_manual:
                         audio_file = voice_utils.text_to_speech_edge(final_response)
                         if audio_file: st.audio(audio_file, autoplay=True)

                    # 6. Cập nhật Robot
                    if st.session_state['robot_emotion'] != detected_emotion:
                        st.session_state['robot_emotion'] = detected_emotion
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Lỗi: {e}")