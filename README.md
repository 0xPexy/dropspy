# 🕵️ DropSpy

**DropSpy** is an automated crypto intelligence tool that collects messages from Telegram and other sources,  
then uses **AI-based filtering (e.g., LLMs like Gemini Flash)** to eliminate noise and highlight promising airdrop or farming opportunities.

---

## 🚀 Features

- Telegram message collection via Telegram API
- AI-based summarization and filtering for relevance and quality
- Digest output in Markdown & JSON format
- CLI utilities for chat list fetch, data reset, etc.

---

## 📁 Project Structure

```
data/chat_exports/     # Raw message logs & digest exports
scripts/reset_data.py  # Utility to reset fetch states or clear data
src/
├── telegram/           # Message fetching logic
├── digest/             # AI summarization & filtering (WIP)
├── config.py           # Configurations and constants
└── main.py             # Entry point for running full pipeline
```

---

## ⚙️ Usage

```bash
# Fetch messages from Telegram
python src/telegram/fetch_messages.py

# Reset data (for dev/testing)
python scripts/reset_data.py
```

---

> ✨ *“Drop the noise. Spot the alpha.”*
