from database import Database
from telegram import ReplyKeyboardRemove

db = Database("agner_base.db")

STATE = {
    'reg' : 1,
    'menu' : 2
}

def personal_check(update,context):
    user = update.message.from_user
    db_user = db.get_personal_by_id(user.id)


    if not db_user['full_name']:
        update.message.reply_text(
            text="Ismingizni kiriting: ",
            reply_markup = ReplyKeyboardRemove()
        )
        context.user_data['state'] = STATE['reg']

    elif not db_user['username']:
        user = update.message.from_user
        username = user.username
        if username:
            context.user_data['state'] = STATE['reg']
    else:
        context.user_data['state'] = STATE['menu']

def chek_data_personal_decorator(funk):
    def inner(update, context):
        user = update.message.from_user
        db_user = db.get_personal_by_id(user.id)
        state = context.user_data.get("state", 0)

        if not db_user or not db_user['full_name']:
            update.message.reply_text(
                text="Ismingizni kiriting: ",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data['state'] = STATE['reg']
            return False


        elif not db_user['username']:
            username = update.message.from_user.username
            if username:
                db.update_personal_username(user.id, username)
                context.user_data['state'] = STATE['menu']
            else:
                update.message.reply_text("Usernameingiz yo‘q. Telegram sozlamalaridan qo‘shing!")
                return False

        # Agar hammasi joyida bo‘lsa → asosiy funksiya ishlaydi
        context.user_data['state'] = STATE['menu']
        return funk(update, context)

    return inner
