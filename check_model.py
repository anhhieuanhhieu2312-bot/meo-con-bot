import google.generativeai as genai

# Dán API Key của bạn vào đây
api_key = "AIzaSyCKSwpKmQX6L8jE3tpNertyOmCkglP5us8"
genai.configure(api_key=api_key)

print("Đang kiểm tra các model khả dụng...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Lỗi rồi: {e}")