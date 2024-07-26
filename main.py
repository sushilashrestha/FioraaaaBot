import asyncio
from telegram import Update, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
import random
import logging
import datetime

# Replace 'YOUR_API_TOKEN' with your bot's API token
API_TOKEN = ''

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

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        welcome_message = random.choice(cute_messages)
        await update.message.reply_text(welcome_message)
        await update.message.reply_text("I'll remind you to use your eye drops every 6 hours. "
                                        "Use /setreminder to start the reminders.")
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id
        users[user_id] = {'next_reminder': datetime.datetime.now()}
        await schedule_next_reminder(context, user_id)
        await update.message.reply_text("Great! I'll remind you about your eye drops every 6 hours. "
                                        "The first reminder will be in 6 hours.")
    except Exception as e:
        logger.error(f"Error in set_reminder: {e}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        job = context.job
        user_id = job.data
        reminder_message = random.choice(reminder_messages)
        
        keyboard = [
            [InlineKeyboardButton("Done ✅", callback_data='done'),
             InlineKeyboardButton("Snooze 30min ⏰", callback_data='snooze')]
        ]
        # Add code to send the reminder message with the keyboard
    except Exception as e:
        logger.error(f"Error in send_reminder: {e}")

async def schedule_next_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    try:
        next_reminder_time = users[user_id]['next_reminder'] + datetime.timedelta(hours=6)
        context.job_queue.run_once(send_reminder, next_reminder_time, context=user_id)
    except Exception as e:
        logger.error(f"Error in schedule_next_reminder: {e}")

async def main() -> None:
    try:
        application = Application.builder().token(API_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("setreminder", set_reminder))

        await application.initialize()
        await application.start()
        await application.run_polling()
        await application.stop()
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")