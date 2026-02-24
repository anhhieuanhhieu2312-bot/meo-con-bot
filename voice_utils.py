import edge_tts
import asyncio
import re
import emoji
import speech_recognition as sr
import os
import pygame  # Thư viện phát âm thanh mới

# --- CẤU HÌNH ---
VOICE_ID = "vi-VN-HoaiMyNeural" 
READING_RATE = "-15%" 
OUTPUT_FILE = "reply.mp3"

# Khởi tạo mixer để phát nhạc
pygame.mixer.init()

async def _generate_audio(text):
    """Tạo file âm thanh từ văn bản"""
    communicate = edge_tts.Communicate(text, VOICE_ID, rate=READING_RATE)
    await communicate.save(OUTPUT_FILE)

def clean_text_for_speech(text):
    """Lọc text rác trước khi đọc"""
    if not text: return ""
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[\*#_`~]', '', text) 
    return text.strip()

def text_to_speech_edge(text):
    """Tạo file MP3 (Dùng cho chế độ bấm nút)"""
    clean_text = clean_text_for_speech(text)
    if not clean_text: return None
    try:
        asyncio.run(_generate_audio(clean_text))
        return OUTPUT_FILE
    except Exception as e:
        print(f"Lỗi TTS: {e}")
        return None

# --- [MỚI] HÀM PHÁT ÂM THANH CHẶN (Chờ đọc xong mới chạy tiếp) ---
def play_audio_blocking(file_path):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        # Vòng lặp chờ cho đến khi nhạc tắt
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Lỗi phát âm thanh: {e}")

# --- [MỚI] HÀM NGHE TRỰC TIẾP TỪ MICRO (Cho chế độ rảnh tay) ---
def listen_live():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Đang nghe...")
        # Tự động căn chỉnh độ ồn môi trường
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Nghe tối đa 5 giây im lặng, giới hạn câu nói 10 giây
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio, language="vi-VN")
            return text
        except sr.WaitTimeoutError:
            return None # Không nói gì
        except sr.UnknownValueError:
            return None # Nói không rõ
        except Exception as e:
            print(f"Lỗi Mic: {e}")
            return None

# Hàm cũ (vẫn giữ để dùng cho nút bấm web)
def speech_to_text(audio_bytes):
    r = sr.Recognizer()
    with open("temp_input.wav", "wb") as f:
        f.write(audio_bytes)
    with sr.AudioFile("temp_input.wav") as source:
        r.adjust_for_ambient_noise(source, duration=0.5) 
        audio_data = r.record(source)
        try:
            return r.recognize_google(audio_data, language="vi-VN")
        except:
            return None