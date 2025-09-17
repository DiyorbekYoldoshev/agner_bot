import sqlite3
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, ConversationHandler
)

ASK_FULLNAME = 1

def start(update: Update, context: CallbackContext):
    text = "Quyidagilardan birini tanlang"
    buttons = [
        [KeyboardButton(text="Shaxsiy foydalanish uchun")],
        [KeyboardButton(text="Biznes uchun")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=reply_markup)

def personal_start(update: Update, context: CallbackContext):
    full_name = update.message.text
    user = update.message.from_user
    username = user.username
    user_id = user.id

    conn = sqlite3.connect("agner_base.db")
    curr = conn.cursor()
    curr.execute("SELECT * FROM personal_users WHERE username = ?", (username,))
    result = curr.fetchone()

    if not result:
        update.message.reply_text("Ismingizni kiriting:")
        curr.execute(
            "INSERT INTO personal_users (id, full_name, username) VALUES (?, ?, ?)",
            (user_id, full_name, username)
        )
        conn.commit()
        update.message.reply_text(
            f"Siz ro'yxatdan o'tdingiz!\n"
            f"ID: {user_id}\nIsm: {full_name}\nUsername: @{username if username else 'yo‘q'}"
        )
    update.message.reply_text("Botimizga Xush Kelibsiz:")

    return ASK_FULLNAME

def save_fullname(update: Update, context: CallbackContext):
    full_name = update.message.text
    user = update.message.from_user
    username = user.username
    user_id = user.id

    conn = sqlite3.connect("agner_base.db")
    curr = conn.cursor()

    # Foydalanuvchini tekshirish
    curr.execute("SELECT * FROM personal_users WHERE username = ?", (username,))
    result = curr.fetchone()

    if not result:
        curr.execute(
            "INSERT INTO personal_users (id, full_name, username) VALUES (?, ?, ?)",
            (user_id, full_name, username)
        )
        conn.commit()
        update.message.reply_text(
            f"Siz ro'yxatdan o'tdingiz!\n"
            f"ID: {user_id}\nIsm: {full_name}\nUsername: @{username if username else 'yo‘q'}"
        )
    else:
        update.message.reply_text("Siz avval ro'yxatdan o'tgansiz")

    conn.close()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Bekor qilindi ❌")
    return ConversationHandler.END

def main():
    updater = Updater(token="8006573821:AAEeC0iEQu2FCaohCOvRIh5Nc1-KSo4_4J0")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'Shaxsiy foydalanish uchun'), personal_start)],
        states={
            ASK_FULLNAME: [MessageHandler(Filters.text & ~Filters.command, save_fullname)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
