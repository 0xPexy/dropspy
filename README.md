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
src/dropspy/
├── config.py           # Configurations and constants
├── main.py             # Entry point for running full pipeline
├── llm/
│   ├── prompt_loader.py  # Loads prompts for LLM
│   └── tokenizer.py      # Tokenizes text for LLM
├── pipeline/
│   ├── fetch.py          # Fetches data from Telegram
│   ├── prebatch.py       # Preprocesses fetched data
│   └── batch.py          # Batches preprocessed data
├── telegram/
│   ├── api_adapter.py    # Adapts Telegram API
│   └── types.py          # Defines Telegram data types
```

---

## ⚙️ Usage

### Telegram Chats

To list currently joined Telegram chats:

```bash
python src/dropspy/main.py chats
```

This command will display a list of all the Telegram chats you are currently participating in, including their ID, title, and handle.

### Fetch Telegram Messages

To fetch recent Telegram messages:

```bash
python src/dropspy/main.py fetch
```

This command will fetch recent messages from the target Telegram chats specified in the configuration. The messages will be saved to a file in the `data/fetches/` directory by default. The root directory can be configured by setting the `DATA_DIRECTORY_ROOT` environment variable in `.env`.

### Reset Data (for dev/testing)

```bash
python src/dropspy/main.py reset
```

This command will delete all app data in `DATA_DIRECTORY_ROOT`. Use with caution!

---

> ✨ *“Drop the noise. Spot the alpha.”*
