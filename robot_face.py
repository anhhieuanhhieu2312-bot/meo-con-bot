# FILE: robot_face.py (Phiên bản Fix: Đầu to hơn, Miệng nằm gọn trong mặt)
import streamlit.components.v1 as components

def get_robot_svg(emotion):
    # --- 1. CẤU HÌNH MÀU SẮC & HÌNH DÁNG ---
    # Mặc định (Normal)
    eye_color = "#00ffff"   # Cyan
    eye_height = 25         
    cheek_opacity = "0"     
    # Miệng cười nhẹ
    mouth_path = "M 85 115 Q 100 120 115 115" 
    mouth_stroke = eye_color 

    if emotion == "happy" or emotion == "love":
        eye_color = "#ff69b4"   # Hồng
        eye_height = 8          # Mắt híp
        cheek_opacity = "0.8"   # Hiện má hồng
        # Miệng cười tươi (Đã chỉnh độ cong để không lòi ra ngoài)
        # M: Điểm bắt đầu, Q: Điểm uốn cong, Điểm kết thúc
        mouth_path = "M 70 110 Q 100 135 130 110" 
        mouth_stroke = eye_color

    elif emotion == "sad":
        eye_color = "#4682b4"   # Xanh buồn
        eye_height = 15         
        cheek_opacity = "0"     
        # Miệng mếu
        mouth_path = "M 75 125 Q 100 105 125 125"
        mouth_stroke = eye_color

    elif emotion == "angry":
        eye_color = "#ff0000"   # Đỏ
        eye_height = 20
        cheek_opacity = "0.6"   
        # Miệng ngang
        mouth_path = "M 75 120 L 125 120"
        mouth_stroke = eye_color

    # --- 2. VẼ SVG ---
    # viewBox="0 0 200 180" -> Mở rộng chiều cao khung vẽ lên 180 để chứa đầu dài hơn
    svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; background-color: transparent;">
        <svg width="250" height="200" viewBox="0 0 200 170" xmlns="http://www.w3.org/2000/svg">
            
            <ellipse cx="100" cy="155" rx="60" ry="10" fill="rgba(0,0,0,0.1)" />
            
            <rect x="20" y="20" width="160" height="120" rx="45" ry="45" fill="#000000">
                <animate attributeName="y" values="20;15;20" dur="3s" repeatCount="indefinite" />
            </rect>

            <ellipse cx="50" cy="100" rx="10" ry="6" fill="#ffb6c1" opacity="{cheek_opacity}">
                 <animate attributeName="cy" values="100;95;100" dur="3s" repeatCount="indefinite" />
            </ellipse>
            <ellipse cx="150" cy="100" rx="10" ry="6" fill="#ffb6c1" opacity="{cheek_opacity}">
                 <animate attributeName="cy" values="100;95;100" dur="3s" repeatCount="indefinite" />
            </ellipse>

            <path d="{mouth_path}" stroke="{mouth_stroke}" stroke-width="4" fill="none" stroke-linecap="round">
                <animateTransform attributeName="transform" type="translate" values="0 0; 0 -5; 0 0" dur="3s" repeatCount="indefinite"/>
            </path>

            <ellipse cx="70" cy="65" rx="20" ry="{eye_height}" fill="{eye_color}">
                <animate attributeName="ry" values="{eye_height};2;{eye_height}" dur="4s" begin="0.5s" repeatCount="indefinite" />
                <animate attributeName="cy" values="65;60;65" dur="3s" repeatCount="indefinite" />
            </ellipse>
            
            <ellipse cx="130" cy="65" rx="20" ry="{eye_height}" fill="{eye_color}">
                <animate attributeName="ry" values="{eye_height};2;{eye_height}" dur="4s" begin="0.5s" repeatCount="indefinite" />
                <animate attributeName="cy" values="65;60;65" dur="3s" repeatCount="indefinite" />
            </ellipse>
            
            <defs>
                <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
            </defs>
             <circle cx="70" cy="65" r="15" fill="none" stroke="{eye_color}" stroke-width="2" filter="url(#glow)" opacity="0.6">
                 <animate attributeName="cy" values="65;60;65" dur="3s" repeatCount="indefinite" />
            </circle>
            <circle cx="130" cy="65" r="15" fill="none" stroke="{eye_color}" stroke-width="2" filter="url(#glow)" opacity="0.6">
                 <animate attributeName="cy" values="65;60;65" dur="3s" repeatCount="indefinite" />
            </circle>
        </svg>
    </div>
    """
    return svg

def render_robot(emotion="normal"):
    svg_code = get_robot_svg(emotion)
    # Tăng height của khung chứa lên 220 để không bị scroll
    components.html(svg_code, height=220)