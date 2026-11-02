# Multithreaded Telegram Bot 🤖⚡

An asynchronous and multithreaded Telegram chatbot powered by OpenAI, featuring live SQLite storage and a Tkinter GUI monitoring dashboard.

## 🚀 Features
- **Concurrent Processing:** Background worker threads process long-running tasks and concurrent counting without blocking user messaging.
- **OpenAI Integration:** Direct response generation using ChatGPT completions.
- **Database Telemetry:** Logs conversations, inputs, and background responses in SQLite.
- **Desktop GUI:** Built-in Tkinter interface for live monitoring.

## 📦 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nimasoy/multithread_telebot.git
   cd multithread_telebot
   ```

2. **Configure Environment Variables:**
   Copy the example environment configuration:
   ```bash
   cp .env.example .env
   ```
   Add your API keys to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN="your_bot_father_token"
   OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Install Dependencies & Run:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## 📄 License
This project is open-source under the [MIT License](LICENSE).
