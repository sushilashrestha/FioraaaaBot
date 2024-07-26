import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import logging
from datetime import datetime, timedelta

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
REMINDER_INTERVAL = 6 * 60 * 60  # 6 hours in seconds
users = {}

cute_messages = [
    "Hello there! 🌟 Ready to keep those eyes sparkling? Let's start our eye drop adventure!",
    "Welcome aboard the Eye Care Express! 🚂💨 We're here to make your eyes happy!",
    "Greetings, eye care champion! 🏆 Together, we'll keep your peepers in tip-top shape!",
    "Hey there, bright eyes! 👀✨ Excited to be your personal eye drop reminder buddy!",
    "Welcome to the 'Clear Vision Crew'! 🎉 Let's make every drop count!"
]

reminder_messages = [
    "Time for your eye drops! 💧👁️ Keep those peepers happy!",
    "Your eyes are calling for some refreshing drops! 📞💦",
    "Eye drop o'clock! 🕒 Let's keep that vision crystal clear!",
    "Pssst... Your eyes could use a little moisture right about now! 💧😉",
    "Drop it like it's hot! 🔥 (And by 'it', we mean your eye drops!)"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    users[user_id] = {'next_reminder': datetime.now()}
    
    welcome_message = random.choice(cute_messages)
    await update.message.reply_text(welcome_message)
    await update.message.reply_text("I'll remind you to use your eye drops every 6 hours. "
                                    "Use /setreminder to start the reminders.")

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    users[user_id]['next_reminder'] = datetime.now()
    await schedule_next_reminder(context, user_id)
    await update.message.reply_text("Great! I'll remind you about your eye drops every 6 hours. "
                                    "The first reminder will be in 6 hours.")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user_id = job.data
    reminder_message = random.choice(reminder_messages)
    
    keyboard = [
        [InlineKeyboardButton("Done ✅", callback_data='done'),
         InlineKeyboardButton("Snooze 30min ⏰", callback_data='snooze')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=user_id, text=reminder_message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if query.data == 'done':
        users[user_id]['next_reminder'] = datetime.now() + timedelta(seconds=REMINDER_INTERVAL)
        await query.edit_message_text("Great job! 👍 Next reminder in 6 hours.")
    elif query.data == 'snooze':
        users[user_id]['next_reminder'] = datetime.now() + timedelta(minutes=30)
        await query.edit_message_text("Okay, I'll remind you again in 30 minutes. Don't forget! 😊")
    
    await schedule_next_reminder(context, user_id)

async def schedule_next_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    chat_id = user_id  # In Telegram, user_id is the same as chat_id for private chats
    job_removed = remove_job_if_exists(str(chat_id), context)
    
    next_reminder = users[user_id]['next_reminder']
    now = datetime.now()
    
    if next_reminder <= now:
        next_reminder = now + timedelta(seconds=10)  # Send almost immediately if we're past due
    
    context.job_queue.run_once(send_reminder, next_reminder - now, chat_id=chat_id, name=str(chat_id), data=user_id)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setreminder", set_reminder))
    application.add_handler(CallbackQueryHandler(button_callback))

    await application.initialize()
    await application.start()
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())