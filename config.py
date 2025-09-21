import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv("BOT_TOKEN")  # @BotFather dan olingan token
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]  # Admin foydalanuvchi ID'lari

# Pomodoro sozlamalari
POMODORO_WORK_TIME = 25 * 60  # 25 daqiqa (sekundlarda) - default
POMODORO_BREAK_TIME = 5 * 60  # 5 daqiqa (sekundlarda) - default
LONG_BREAK_TIME = 15 * 60  # 15 daqiqa (sekundlarda) - default

# Database fayl nomi
DATABASE_FILE = "pomodoro_bot.db"

# Xabarlar
MESSAGES = {
    'start': """🍅 Pomodoro Bot'ga xush kelibsiz!

Bu bot sizga Pomodoro texnikasi yordamida samarali ishlashga yordam beradi.

Mavjud buyruqlar:
/start - Botni ishga tushirish
/pomodoro - Pomodoro seansini boshlash
/tasks - Vazifalar ro'yxati
/add_task - Yangi vazifa qo'shish
/stats - Statistikani ko'rish
/settings - Sozlamalar
/help - Yordam""",

    'help': """🆘 Yordam

🍅 **Pomodoro texnikasi:**
- 25 daqiqa ishlash
- 5 daqiqa tanaffus
- Har 4 seansdan keyin 15 daqiqa uzun tanaffus

📝 **Vazifalar:**
- Vazifalar qo'shing va kuzatib boring
- Bajarilgan vazifalarni belgilang

📊 **Statistika:**
- Kunlik/haftalik hisobotlar
- Samaradorlik ko'rsatkichlari""",

    'pomodoro_start': "🍅 Pomodoro seansi boshlandi!\n⏰ 25 daqiqa ishlash vaqti",
    'pomodoro_work_end': "⏰ Ish vaqti tugadi!\n☕ 5 daqiqa tanaffus qiling",
    'pomodoro_break_end': "☕ Tanaffus tugadi!\n🍅 Keyingi seansni boshlashga tayyormisiz?",
    'pomodoro_long_break': "🎉 Ajoyib!\n🛋 15 daqiqa uzun tanaffus qiling",
    'pomodoro_cancelled': "❌ Pomodoro seansi bekor qilindi",

    'task_added': "✅ Vazifa qo'shildi!",
    'task_completed': "🎉 Vazifa bajarildi!",
    'task_deleted': "🗑 Vazifa o'chirildi!",
    'recurring_task_added': "✅ Takrorlanuvchi vazifa qo'shildi!",

    'no_tasks': "📝 Hozircha vazifalar yo'q.\nYangi vazifa qo'shing!",

    'stats_daily': "📊 Bugungi statistika:\n🍅 Seanslar: {sessions}\n⏰ Umumiy vaqt: {time}\n✅ Bajarilgan vazifalar: {tasks}",
    'stats_weekly': "📊 Haftalik statistika:\n🍅 Seanslar: {sessions}\n⏰ Umumiy vaqt: {time}\n✅ Bajarilgan vazifalar: {tasks}",

    'settings_updated': "⚙️ Sozlamalar yangilandi!",
    'invalid_time': "❌ Noto'g'ri vaqt formati. Masalan: 25",
}

# Keyboard tugmalari
KEYBOARDS = {
    'main_menu': [
        ['🍅 Pomodoro', '📝 Vazifalar'],
        ['📊 Statistika', '⚙️ Sozlamalar'],
        ['🆘 Yordam']
    ],

    'pomodoro_active': [
        ['⏸ Pauza', '❌ Bekor qilish'],
        ['🔙 Asosiy menyu']
    ],

    'pomodoro_paused': [
        ['▶️ Davom etish', '❌ Bekor qilish'],
        ['🔙 Asosiy menyu']
    ],

    'tasks_menu': [
        ['➕ Vazifa qoshish', "📋 Royxat"],['🔙 Asosiy menyu']
],

'stats_menu': [
    ['📅 Bugungi', '📊 Haftalik'],
    ['📈 Umumiy', '🔙 Asosiy menyu']
],

'settings_menu': [
    ['⏰ Ish vaqti', '☕ Tanaffus vaqti'],
    ['🛋 Uzun tanaffus', '🔔 Bildirishnomalar'],
    ['🔙 Asosiy menyu']
]
}