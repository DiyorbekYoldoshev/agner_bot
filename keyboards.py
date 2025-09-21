from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_main_keyboard():
    """Asosiy klaviatura"""
    keyboard = [
        ["🍅 Pomodoro", "📝 Vazifalar"],
        ["📊 Statistika", "⚙️ Sozlamalar"],
        ["ℹ️ Yordam"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_pomodoro_keyboard():
    """Pomodoro klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("▶️ Boshlash", callback_data="start_pomodoro")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_active_pomodoro_keyboard():
    """Faol Pomodoro klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("⏹ To'xtatish", callback_data="stop_pomodoro")],
        [InlineKeyboardButton("⏸ Pauza", callback_data="pause_pomodoro")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tasks_keyboard():
    """Vazifalar klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("➕ Yangi vazifa", callback_data="add_task")],
        [InlineKeyboardButton("📋 Vazifalar ro'yxati", callback_data="list_tasks")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_task_list_keyboard(tasks):
    """Vazifalar ro'yxati klaviaturasi"""
    keyboard = []

    for task in tasks:
        priority_emoji = "🔴" if task['priority'] == 3 else "🟡" if task['priority'] == 2 else "🟢"
        button_text = f"{priority_emoji} {task['title'][:30]}..."
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"task_{task['id']}")])

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="tasks_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_task_actions_keyboard(task_id):
    """Vazifa amallar klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("✅ Bajarildi", callback_data=f"complete_task_{task_id}")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_task_{task_id}")],
        [InlineKeyboardButton("🍅 Pomodoro", callback_data=f"pomodoro_task_{task_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="list_tasks")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_priority_keyboard():
    """Muhimlik darajasi klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("🔴 Yuqori", callback_data="priority_3")],
        [InlineKeyboardButton("🟡 O'rta", callback_data="priority_2")],
        [InlineKeyboardButton("🟢 Past", callback_data="priority_1")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_keyboard():
    """Statistika klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("📊 Bugun", callback_data="stats_daily")],
        [InlineKeyboardButton("📈 Hafta", callback_data="stats_weekly")],
        [InlineKeyboardButton("📅 Oy", callback_data="stats_monthly")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard():
    """Admin klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Umumiy statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard():
    """Sozlamalar klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("⏰ Timer sozlamalari", callback_data="timer_settings")],
        [InlineKeyboardButton("🔔 Bildirishnomalar", callback_data="notification_settings")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


