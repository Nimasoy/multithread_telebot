import threading
import time
import sqlite3
import tkinter as tk
from tkinter import ttk
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

client = OpenAI(api_key=OPENAI_API_KEY)


def count_numbers(chat_id, target, user_id, user_input):
    try:
        updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
        context = updater.dispatcher

        target = int(target)
        if target < 0:
            raise ValueError("Please enter a non-negative number.")

        for i in range(target + 1):
            time.sleep(1)
            # just the thread name to print out as a response
            message = f"{threading.current_thread().name}: {i}"
            context.bot.send_message(chat_id=chat_id, text=message)

            save_to_database(user_id, user_input, message)
    except ValueError as e:
        context.bot.send_message(chat_id=chat_id, text=f"Error: {e}")


def process_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_input = update.message.text

    try:
        target = int(user_input)
        # distinct thread creation for each message handling of numbers
        thread = threading.Thread(target=count_numbers, args=(chat_id, target, user_id, user_input))
        thread.start()
    except ValueError:
        context.bot.send_message(chat_id=chat_id, text="I'm thinking about your message. Please wait.")
        # distinct thread creation for each message handling of something other than a number
        thread = threading.Thread(target=invoke_chatgpt, args=(chat_id, user_id, user_input))
        thread.start()

        save_to_database(user_id, user_input, "")


def invoke_chatgpt(chat_id, user_id, user_input):
    messages = [
        {"role": "user", "content": user_input}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100
        )

        gpt_response = response.choices[0].message.content

        updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
        updater.dispatcher.bot.send_message(chat_id=chat_id, text=gpt_response)

        save_to_database(user_id, user_input, gpt_response)

    except Exception as e:
        print(f"Error invoking ChatGPT: {e}")


def save_to_database(user_id, user_input, bot_response):
    connection = sqlite3.connect("bot_db.db")
    cursor = connection.cursor()

    try:
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        user_message TEXT,
                        bot_response TEXT
                    )
                ''')
        cursor.execute('''
                    INSERT INTO chat_history (user_id, user_message, bot_response)
                    VALUES (?, ?, ?)
                ''', (user_id, user_input, bot_response))
        connection.commit()
    finally:
        connection.close()


def fetch_messages():
    connection = sqlite3.connect("bot_db.db")
    cursor = connection.cursor()

    cursor.execute('''
            SELECT user_id, user_message, bot_response
            FROM chat_history
        ''')
    messages = cursor.fetchall()
    connection.close()

    return messages


class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Control Panel")

        self.tree = ttk.Treeview(self.root, columns=('User ID', 'User Message', 'Bot Response'), show='headings')
        self.tree.heading('User ID', text='User ID')
        self.tree.heading('User Message', text='User Message')
        self.tree.heading('Bot Response', text='Bot Response')
        self.tree.pack(padx=10, pady=10)

        refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_messages)
        refresh_button.pack(pady=10)

        self.refresh_messages()

        clear_button = tk.Button(self.root, text='Clear History', command=self.clear_history)
        clear_button.pack(pady=10)

    def clear_history(self):
        connection = sqlite3.connect("bot_db.db")
        cursor = connection.cursor()

        try:
            cursor.execute('DROP TABLE IF EXISTS chat_history')
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS chat_history (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                user_message TEXT,
                                bot_response TEXT
                            )
                        ''')
            print("Chat history cleared.")
        finally:
            connection.close()

    def refresh_messages(self):
        messages = fetch_messages()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for message in messages:
            self.tree.insert("", "end", values=message)

        self.root.after(1000, self.refresh_messages)


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    # constantly check for new messages in the background while the main program is running
    updater_thread = threading.Thread(target=updater.start_polling)
    updater_thread.start()

    root = tk.Tk()
    admin_panel = AdminPanel(root)
    root.mainloop()

    updater.stop()
    updater_thread.join()


if __name__ == "__main__":
    main()