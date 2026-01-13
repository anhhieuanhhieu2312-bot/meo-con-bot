import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import os
from PIL import Image, ImageTk, ImageEnhance
import google.generativeai as genai 

# --- CẤU HÌNH API ---
API_KEY = "AIzaSyCKSwpKmQX6L8jE3tpNertyOmCkglP5us8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- HÀM GỌI API ---
def call_gemini_api(user_text):
    try:
        response = model.generate_content(user_text)
        if response.text:
            return response.text
        else:
            return "Meo Con đang chải lông, chưa nghĩ ra câu trả lời... 😿"
    except Exception:
        return "Meo Con bị mất kết nối vệ tinh rồi. Kiểm tra lại wifi nha! 📡"

# --- MÀU SẮC ---
BG_MAIN = "#FFC0CB"         
BG_CANVAS = "#FFF0F5"       
BUBBLE_USER = "#FF69B4"     
BUBBLE_BOT = "#FFFFFF"      
TEXT_USER = "#FFFFFF"       
TEXT_BOT = "#5F9EA0"        

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat với Meo Con 🐱")
        
        # Kích thước cửa sổ
        self.root.geometry("550x750")
        self.root.configure(bg=BG_MAIN)

        self.sticker_photos = [] 
        self.current_y = 20      

        # HEADER
        header = tk.Frame(root, bg="#FF1493", pady=15)
        header.pack(fill=tk.X)
        tk.Label(header, text="🐱 Meo Con Tinh Nghịch ✨", bg="#FF1493", fg="white", font=("Segoe UI", 16, "bold")).pack()

        # KHUNG CHAT
        self.chat_frame = tk.Frame(root, bg=BG_MAIN)
        self.chat_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.chat_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self.chat_frame, bg=BG_CANVAS, bd=0, highlightthickness=0,
                                yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)

        # Xử lý cuộn chuột
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.draw_background_stickers(total_height=5000)

        # INPUT AREA
        input_frame = tk.Frame(root, bg=BG_MAIN, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry = tk.Entry(input_frame, font=("Segoe UI", 12), bd=0, highlightthickness=2, highlightbackground="#FF1493", relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
        self.entry.bind("<Return>", self.send_message)

        btn = tk.Button(input_frame, text="Gửi 🐾", command=self.send_message, bg="#FF1493", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=20)
        btn.pack(side=tk.RIGHT)

        # --- QUAN TRỌNG: Khởi tạo biến theo dõi độ rộng ---
        self.root.update_idletasks() # Cập nhật để lấy kích thước thật
        self.last_width = self.canvas.winfo_width()
        if self.last_width <= 1: self.last_width = 500 # Giá trị dự phòng

        self.add_bubble("Meo Con 🐱", "Chào cậu! Có chuyện gì vui kể tớ nghe với? 🐟", is_user=False)
        self.ai_queue = []   # Tạo cái hộp thư
        self.check_ai_queue() # Bắt đầu canh thư
    def check_ai_queue(self):
        # Nếu trong hộp thư có thư mới
        if hasattr(self, 'ai_queue') and len(self.ai_queue) > 0:
            # Lấy thư ra (câu trả lời của Bot)
            reply_text = self.ai_queue.pop(0)
            # Hiển thị lên màn hình (Lúc này đang ở luồng chính nên an toàn)
            self.add_bubble("Meo Con 🐱", reply_text, is_user=False)
        
        # Cứ 100ms (0.1 giây) lại kiểm tra hộp thư một lần
        self.root.after(100, self.check_ai_queue)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def draw_background_stickers(self, total_height):
        folder = "stickers"
        if not os.path.exists(folder): return
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files: return
        
        density = 150 
        num_stickers = int(total_height / density) * 2 
        for _ in range(num_stickers):
            try:
                img_path = os.path.join(folder, random.choice(files))
                max_x = 500 
                x = random.randint(-50, max_x) 
                y = random.randint(0, total_height)
                img = Image.open(img_path).convert("RGBA")
                size = random.randint(50, 150)
                img.thumbnail((size, size), Image.LANCZOS)
                angle = random.randint(-45, 45)
                img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
                alpha = img.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.15) 
                img.putalpha(alpha)
                photo = ImageTk.PhotoImage(img)
                self.sticker_photos.append(photo)
                self.canvas.create_image(x, y, image=photo, anchor='center')
            except: pass

    # --- HÀM ADD_BUBBLE ĐÃ ĐƯỢC SỬA LỖI CUỘN TRIỆT ĐỂ ---
    def add_bubble(self, sender, text, is_user=True):
        # --- 1. LOGIC KIỂM TRA VỊ TRÍ CUỘN (SMART SCROLL) ---
        # Lấy vị trí hiện tại của thanh cuộn (trả về tuple, phần tử thứ 2 là đáy)
        # Nếu > 0.9 nghĩa là người dùng đang xem ở đoạn cuối cùng.
        # Nếu < 0.9 nghĩa là người dùng đang lướt lên xem tin cũ.
        try:
            current_pos = self.canvas.yview()[1]
            was_at_bottom = current_pos > 0.9
        except:
            was_at_bottom = True # Mặc định là True nếu mới mở app

        # --- 2. TÍNH TOÁN VỊ TRÍ VẼ ---
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100: canvas_width = 500 # Kích thước dự phòng
        
        max_text_width = int(canvas_width * 0.70) 
        font_style = ("Segoe UI", 11)
        
        # Gắn thẻ (Tag) để phục vụ việc thay đổi kích thước cửa sổ sau này
        msg_tags = "user_msg" if is_user else "bot_msg"

        if is_user:
            bg_color = BUBBLE_USER
            text_color = TEXT_USER
            anchor_text = "ne"     # Neo chữ sang phải
            justify_text = "left" 
            x_pos = canvas_width - 30 
        else:
            bg_color = BUBBLE_BOT
            text_color = TEXT_BOT
            anchor_text = "nw"     # Neo chữ sang trái
            justify_text = "left"
            x_pos = 20 

        # --- 3. VẼ LÊN CANVAS ---
        # Vẽ văn bản
        text_id = self.canvas.create_text(
            x_pos, 
            self.current_y + 15, 
            text=f"{text}", 
            width=max_text_width, 
            font=font_style, 
            fill=text_color, 
            anchor=anchor_text,
            justify=justify_text,
            tags=msg_tags # <--- Tag quan trọng để fix lỗi giao diện
        )
        
        # Lấy khung bao quanh văn bản
        bbox = self.canvas.bbox(text_id)
        
        # Vẽ hình chữ nhật nền (Bubble chat)
        padding_x = 15
        padding_y = 10
        rect_coords = (bbox[0] - padding_x, bbox[1] - padding_y, bbox[2] + padding_x, bbox[3] + padding_y)
        
        rect_id = self.canvas.create_rectangle(
            rect_coords, 
            fill=bg_color, 
            outline=bg_color, 
            width=0,
            tags=msg_tags # <--- Tag quan trọng
        )
        
        # Vẽ tên người gửi
        if is_user:
            name_anchor = "se"
            name_x = bbox[2]
            name_y = bbox[1] - 15
        else:
            name_anchor = "sw"
            name_x = bbox[0]
            name_y = bbox[1] - 15
            
        self.canvas.create_text(
            name_x, name_y, 
            text=sender, 
            font=("Segoe UI", 8, "bold"), 
            fill="#888", 
            anchor=name_anchor,
            tags=msg_tags # <--- Tag quan trọng
        )

        # Đẩy hình chữ nhật xuống dưới lớp chữ
        self.canvas.tag_lower(rect_id, text_id)
        
        # Cập nhật vị trí Y cho tin nhắn tiếp theo
        msg_height = (bbox[3] - bbox[1]) + (padding_y * 2) + 25
        self.current_y += msg_height
        
        # Cập nhật vùng cuộn của Canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # --- 4. XỬ LÝ CUỘN (CHỐT HẠ) ---
        if is_user:
            # Nếu là tin nhắn của BẠN -> Luôn cuộn xuống để nhìn thấy
            self.canvas.yview_moveto(1.0)
        elif was_at_bottom:
            # Nếu là tin của BOT và TRƯỚC ĐÓ bạn đang ở đáy -> Cuộn xuống
            self.canvas.yview_moveto(1.0)
        
        

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg.strip(): return
        self.add_bubble("Bạn", msg, is_user=True)
        self.entry.delete(0, tk.END)
        threading.Thread(target=self.get_ai_reply, args=(msg,)).start()

    def get_ai_reply(self, user_msg):
        # Gọi API lấy câu trả lời (việc nặng nhọc này cứ để thread làm)
        reply_text = call_gemini_api(user_msg)
        
        # Có câu trả lời rồi thì bỏ vào hộp thư
        if not hasattr(self, 'ai_queue'): 
            self.ai_queue = []
        self.ai_queue.append(reply_text)

    def on_canvas_configure(self, event):
        # Cập nhật vùng cuộn
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        current_width = event.width
        
        # Nếu chưa có last_width hoặc cửa sổ quá nhỏ (lỗi lúc khởi tạo), cập nhật lại rồi thoát
        if not hasattr(self, 'last_width') or self.last_width < 100:
            self.last_width = current_width
            return

        # Tính độ lệch giữa độ rộng cũ và mới
        diff = current_width - self.last_width
        
        # Nếu có sự thay đổi kích thước đáng kể
        if abs(diff) > 0:
            # Di chuyển tất cả các đối tượng có tag "user_msg" theo trục X một đoạn bằng diff
            self.canvas.move("user_msg", diff, 0)
            
            # Cập nhật lại độ rộng mới để dùng cho lần sau
            self.last_width = current_width

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()