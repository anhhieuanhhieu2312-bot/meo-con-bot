import json
import urllib.request
import sys
import time

# --- BẮT BUỘC: DÁN API KEY MỚI VÀO ĐÂY ---
API_KEY = "AIzaSyC2s6MSB5C9nqKCG9DEw5xKWwFT-CpsmmI"

# Dùng bản 1.5 Flash (Bản ổn định nhất, không lỗi vặt)
MODEL_NAME = "gemini-1.5-flash"

URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def chat_with_gemini(user_text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
    }
    
    try:
        data_json = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(URL, data=data_json, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            return "Không có phản hồi."
            
    except urllib.error.HTTPError as e:
        # In lỗi chi tiết để biết chính xác lý do
        error_msg = e.read().decode('utf-8')
        print(f"\n[LỖI CHI TIẾT TỪ GOOGLE]: {error_msg}")
        return "Lỗi kết nối."
    except Exception as e:
        return f"Lỗi hệ thống: {e}"

def main():
    print(f"\n✅ Đang kết nối tới: {MODEL_NAME}...")
    # Test thử 1 câu ngay khi bật
    test_reply = chat_with_gemini("Chào Mây")
    
    if "Lỗi" in test_reply:
        print("❌ Kết nối thất bại. Hãy kiểm tra lại API Key.")
        return

    print("✅ Kết nối THÀNH CÔNG! Bắt đầu chat nhé.")
    print("="*50)

    while True:
        user_input = input("\nBẠN: ")
        if user_input.lower() in ['bye', 'exit']: break
        
        print("Mây: ...", end="\r")
        reply = chat_with_gemini(user_input)
        print(f"Mây: {reply}")

if __name__ == "__main__":
    main()