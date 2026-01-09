import urllib.request
import json

# Dán API Key của bạn vào đây
API_KEY = "AIzaSyC2s6MSB5C9nqKCG9DEw5xKWwFT-CpsmmI"

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    print(f"--- Đang kiểm tra Key: {API_KEY[:5]}... ---")
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("✅ KẾT NỐI THÀNH CÔNG! Google đã trả lời.")
        print("Danh sách các Model bạn có thể dùng (hãy copy 1 cái tên bên dưới):")
        print("-" * 50)
        found_any = False
        for model in data.get('models', []):
            # Chỉ lấy những model hỗ trợ tạo nội dung (generateContent)
            if "generateContent" in model.get('supportedGenerationMethods', []):
                # Lấy phần tên sau dấu / (ví dụ: models/gemini-pro -> gemini-pro)
                clean_name = model['name'].replace('models/', '')
                print(f"👉 {clean_name}")
                found_any = True
        
        if not found_any:
            print("⚠️ Key đúng nhưng không tìm thấy model chat nào. Tài khoản có thể bị hạn chế.")
        print("-" * 50)

except urllib.error.HTTPError as e:
    print(f"❌ LỖI TỪ GOOGLE ({e.code}): {e.reason}")
    if e.code == 400:
        print("=> Key của bạn có thể không hợp lệ hoặc sai định dạng.")
    elif e.code == 403:
        print("=> Key đúng, nhưng bị chặn quyền truy cập (do vị trí địa lý hoặc hết hạn ngạch).")
except Exception as e:
    print(f"❌ LỖI KHÁC: {e}")