import asyncio
from telegram import Update, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
import random
import logging
import datetime
import os
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

cute_messages = [
    "Don't forget your eye drops! 😊💧",
    "Time for a little eye care! 🌸👁️",
    "Eye drop time! Keep those eyes healthy! 🐱💧",
    "Reminder: Eye drops are calling! 🌼💧"
]

reminder_messages = [
    "It's time for your eye drops! 💧",
    "Don't forget your eye drops! 😊",
    "Eye drop time! Keep those eyes healthy! 🐱💧"
]

load_dotenv()

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = random.choice(cute_messages)
        await update.message.reply_text(welcome_message)
        await update.message.reply_text("I'll remind you to use your eye drops every 6 hours. "
                                        "Use /setreminder to start the reminders.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = "Hi, How can I help you today? 😊\n\n" 
    await update.message.reply_text(help_message)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        users[user_id] = {'next_reminder': datetime.datetime.now()}
        await schedule_next_reminder(context, user_id)
        await update.message.reply_text("Great! I'll remind you about your eye drops every 6 hours. "
                                        "The first reminder will be in 6 hours.")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        user_id = job.data
        reminder_message = random.choice(reminder_messages)
        
        keyboard = [
            [InlineKeyboardButton("Done ✅", callback_data='done'),
             InlineKeyboardButton("Snooze 30min ⏰", callback_data='snooze')]
        ]

async def schedule_next_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
        next_reminder_time = users[user_id]['next_reminder'] + datetime.timedelta(hours=6)
        context.job_queue.run_once(send_reminder, next_reminder_time, context=user_id)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
      print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print("Starting bot......")
    app = Application.builder().token(os.getenv("API_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setreminder", set_reminder))
    app.add_handler(CommandHandler("help", help))

    app.add_error_handler(error)

    print("Polling......")
    app.run_polling(poll_interval=5)
