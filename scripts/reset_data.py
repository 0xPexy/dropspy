import os
import shutil

# 🔧 설정
chat_export_dir = "chat_exports"
last_fetch_file = "last_fetch.json"

# 📁 chat_exports 폴더 비우기
if os.path.exists(chat_export_dir):
    for filename in os.listdir(chat_export_dir):
        file_path = os.path.join(chat_export_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".md"):
            os.remove(file_path)
    print(f"✅ '{chat_export_dir}/' 안의 Markdown 파일들 삭제 완료")
else:
    print(f"⚠️ '{chat_export_dir}/' 폴더가 존재하지 않음")

# 🗑️ last_fetch.json 삭제
if os.path.exists(last_fetch_file):
    os.remove(last_fetch_file)
    print(f"✅ '{last_fetch_file}' 삭제 완료")
else:
    print(f"⚠️ '{last_fetch_file}' 파일이 존재하지 않음")
