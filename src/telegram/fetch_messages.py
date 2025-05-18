from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta, timezone
import json
import os
from config import API_ID, API_HASH, SESSION_NAME, TARGET_CHATS, DEFAULT_FETCH_DAYS, PROMPT_VERSION

# 🌐 한국 시간대
KST = timezone(timedelta(hours=9))

msg_limit_per_call = 100
output_dir = "chat_exports"
prompt_dir = "prompts"
os.makedirs(output_dir, exist_ok=True)

# 📁 last_fetch 기록 불러오기
fetch_record_file = "last_fetch.json"
if os.path.exists(fetch_record_file):
    with open(fetch_record_file, "r") as f:
        last_fetch = json.load(f)
else:
    last_fetch = {}

# 📄 GPT 프롬프트 로드
prompt_path = os.path.join(prompt_dir, f"{PROMPT_VERSION}.md")
print(f"🧠 사용 중인 GPT 프롬프트 버전: {PROMPT_VERSION}")
if not os.path.exists(prompt_path):
    raise FileNotFoundError(f"프롬프트 파일이 없습니다: {prompt_path}")
with open(prompt_path, "r", encoding="utf-8") as f:
    gpt_prompt = f.read().strip()

# 📡 텔레그램 세션 시작
with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
    daily_messages = {}

    for chat in TARGET_CHATS:
        print(f"\n📥 수집 시작: {chat}")
        try:
            entity = client.get_entity(chat)
            last_time = last_fetch.get(chat)

            if last_time:
                min_date = datetime.fromisoformat(last_time).astimezone(KST)
                print(f"↪️ 마지막 수집 이후: {min_date.strftime('%Y-%m-%d %H:%M:%S')} 부터 가져옵니다.")
            else:
                min_date = datetime.now(KST) - timedelta(days=DEFAULT_FETCH_DAYS)
                print(f"🆕 수집 기록 없음 → 최근 {DEFAULT_FETCH_DAYS}일치 ({min_date.strftime('%Y-%m-%d')}) 부터 가져옵니다.")

            offset_id = 0
            collected = []

            while True:
                history = client(GetHistoryRequest(
                    peer=entity,
                    limit=msg_limit_per_call,
                    offset_id=offset_id,
                    offset_date=None,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                if not history.messages:
                    break

                for msg in history.messages:
                    msg_kst = msg.date.astimezone(KST)
                    if msg.message and msg_kst > min_date:
                        collected.append(msg)
                    elif msg_kst <= min_date:
                        break

                if history.messages:
                    offset_id = history.messages[-1].id
                else:
                    break

                if any(msg.date.astimezone(KST) <= min_date for msg in history.messages):
                    break

            print(f"✅ {chat}에서 {len(collected)}개 메시지 수집됨")

            for msg in collected:
                kst_time = msg.date.astimezone(KST)
                msg_date = kst_time.strftime("%Y-%m-%d")
                full_time = kst_time.strftime("%Y-%m-%d %H:%M")

                if msg_date not in daily_messages:
                    daily_messages[msg_date] = []

                daily_messages[msg_date].append({
                    "channel": chat,
                    "time": full_time,
                    "text": msg.message.strip()
                })

            if collected:
                last_time = max([m.date for m in collected])
                last_fetch[chat] = last_time.astimezone(KST).isoformat()

        except Exception as e:
            print(f"❌ {chat}에서 에러 발생: {e}")

# 📄 날짜별 Markdown 저장 (프롬프트 포함)
for day, messages in daily_messages.items():
    filename = f"{output_dir}/airdrop_digest_{day}.md"
    with open(filename, "w", encoding="utf-8") as f:
        # 📌 프롬프트 먼저 삽입
        f.write(f"<!-- GPT Prompt (version: {PROMPT_VERSION}) -->\n")
        f.write(gpt_prompt + "\n\n")
        f.write("---\n\n")  # 구분선
        f.write(f"# 📅 Airdrop Digest - {day} (KST 기준)\n\n")
        for msg in sorted(messages, key=lambda x: x["time"], reverse=True):
            f.write(f"## 📡 채널: {msg['channel']}\n")
            f.write(f"### 🕒 {msg['time']}\n")
            f.write(f"```\n{msg['text']}\n```\n\n")
    print(f"📄 저장 완료: {filename}")

# 💾 마지막 수집 시점 저장
with open(fetch_record_file, "w") as f:
    json.dump(last_fetch, f, indent=2)

print("✅ 전체 수집 완료.")
