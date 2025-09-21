import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from database import Database
from keyboards import *
from config import *

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global o'zgaruvchilar
db = Database()
active_pomodoros = {}  # user_id: {'session_id': int, 'start_time': datetime, 'task_id': int}
user_states = {}  # user_id: {'state': str, 'data': dict}

import os
class PomodoroBot:
    def __init__(self):
        self.application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
        self.setup_handlers()

        tz = pytz.timezone("Asia/Tashkent")
        self.application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
        if self.application.job_queue:
            self.application.job_queue.scheduler.configure(timezone=tz)
        self.setup_handlers()

    def setup_handlers(self):
        """Handler'larni sozlash"""
        # Komandalar
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))

        # Callback query'lar
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # Matn xabarlari
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)

        await update.message.reply_text(
            MESSAGES['start'],
            reply_markup=get_main_keyboard()
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam komandasi"""
        await update.message.reply_text(
            MESSAGES['help'],
            reply_markup=get_main_keyboard()
        )

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin komandasi"""
        user_id = update.effective_user.id

        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q!")
            return

        await update.message.reply_text(
            "🔧 Admin paneli",
            reply_markup=get_admin_keyboard()
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Matn xabarlarini qayta ishlash"""
        user_id = update.effective_user.id
        text = update.message.text

        # Foydalanuvchi holatini tekshirish
        if user_id in user_states:
            await self.handle_user_state(update, context)
            return

        # Asosiy menyu tugmalari
        if text == "🍅 Pomodoro":
            await self.show_pomodoro_menu(update, context)
        elif text == "📝 Vazifalar":
            await self.show_tasks_menu(update, context)
        elif text == "📊 Statistika":
            await self.show_stats_menu(update, context)
        elif text == "⚙️ Sozlamalar":
            await self.show_settings_menu(update, context)
        elif text == "ℹ️ Yordam":
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=get_main_keyboard()
            )

    async def handle_user_state(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Foydalanuvchi holatini qayta ishlash"""
        user_id = update.effective_user.id
        state = user_states[user_id]['state']
        text = update.message.text

        if state == "adding_task_title":
            # Vazifa nomini saqlash
            user_states[user_id]['data']['title'] = text
            user_states[user_id]['state'] = "adding_task_description"

            await update.message.reply_text(
                "📝 Vazifa tavsifini kiriting (ixtiyoriy):\n\n"
                "Agar tavsif kerak bo'lmasa, /skip yozing."
            )

        elif state == "adding_task_description":
            if text != "/skip":
                user_states[user_id]['data']['description'] = text

            await update.message.reply_text(
                "🎯 Vazifa muhimlik darajasini tanlang:",
                reply_markup=get_priority_keyboard()
            )

        elif state == "admin_broadcast":
            # Admin xabar yuborish
            if user_id in ADMIN_IDS:
                await self.broadcast_message(text, context)
                await update.message.reply_text("✅ Xabar barcha foydalanuvchilarga yuborildi!")

            del user_states[user_id]

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback query'larni qayta ishlash"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        # Pomodoro amallar
        if data == "start_pomodoro":
            await self.start_pomodoro(query, context)
        elif data == "stop_pomodoro":
            await self.stop_pomodoro(query, context)
        elif data == "pause_pomodoro":
            await self.pause_pomodoro(query, context)

        # Vazifa amallar
        elif data == "add_task":
            await self.add_task_start(query, context)
        elif data == "list_tasks":
            await self.list_tasks(query, context)
        elif data.startswith("task_"):
            task_id = int(data.split("_")[1])
            await self.show_task_details(query, context, task_id)
        elif data.startswith("complete_task_"):
            task_id = int(data.split("_")[2])
            await self.complete_task(query, context, task_id)
        elif data.startswith("delete_task_"):
            task_id = int(data.split("_")[2])
            await self.delete_task(query, context, task_id)
        elif data.startswith("pomodoro_task_"):
            task_id = int(data.split("_")[2])
            await self.start_pomodoro_with_task(query, context, task_id)

        # Muhimlik darajasi
        elif data.startswith("priority_"):
            priority = int(data.split("_")[1])
            await self.save_task(query, context, priority)

        # Statistika
        elif data == "stats_daily":
            await self.show_daily_stats(query, context)
        elif data == "stats_weekly":
            await self.show_weekly_stats(query, context)
        elif data == "stats_monthly":
            await self.show_monthly_stats(query, context)

        # Admin amallar
        elif data == "admin_users":
            await self.show_admin_users(query, context)
        elif data == "admin_stats":
            await self.show_admin_stats(query, context)
        elif data == "admin_broadcast":
            await self.admin_broadcast_start(query, context)

        # Navigatsiya
        elif data == "back_to_main":
            await self.back_to_main(query, context)
        elif data == "tasks_menu":
            await self.show_tasks_menu(query, context)

    async def show_pomodoro_menu(self, update, context):
        """Pomodoro menyusini ko'rsatish"""
        user_id = update.effective_user.id if hasattr(update, 'effective_user') else update.from_user.id

        if user_id in active_pomodoros:
            # Faol Pomodoro bor
            session = active_pomodoros[user_id]
            elapsed = datetime.now() - session['start_time']
            remaining = timedelta(seconds=POMODORO_WORK_TIME) - elapsed

            if remaining.total_seconds() > 0:
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)

                text = f"🍅 Pomodoro faol!\n\n⏰ Qolgan vaqt: {minutes:02d}:{seconds:02d}\n\n💪 Diqqatingizni saqlang!"
                keyboard = get_active_pomodoro_keyboard()
            else:
                # Vaqt tugagan
                await self.finish_pomodoro(user_id, context)
                text = "🍅 Pomodoro menyusi\n\nYangi Pomodoro seansini boshlang!"
                keyboard = get_pomodoro_keyboard()
        else:
            text = "🍅 Pomodoro menyusi\n\nYangi Pomodoro seansini boshlang!"
            keyboard = get_pomodoro_keyboard()

        if hasattr(update, 'message'):
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.edit_message_text(text, reply_markup=keyboard)

    async def start_pomodoro(self, query, context):
        """Pomodoro boshlash"""
        user_id = query.from_user.id

        if user_id in active_pomodoros:
            await query.edit_message_text("⚠️ Sizda allaqachon faol Pomodoro bor!")
            return

        # Pomodoro seansini boshlash
        session_id = db.start_pomodoro_session(user_id)
        active_pomodoros[user_id] = {
            'session_id': session_id,
            'start_time': datetime.now(),
            'task_id': None
        }

        # Timer o'rnatish
        context.job_queue.run_once(
            self.pomodoro_finished_callback,
            POMODORO_WORK_TIME,
            data={'user_id': user_id, 'session_id': session_id}
        )

        await query.edit_message_text(
            MESSAGES['pomodoro_started'],
            reply_markup=get_active_pomodoro_keyboard()
        )

    async def start_pomodoro_with_task(self, query, context, task_id):
        """Vazifa bilan Pomodoro boshlash"""
        user_id = query.from_user.id

        if user_id in active_pomodoros:
            await query.edit_message_text("⚠️ Sizda allaqachon faol Pomodoro bor!")
            return

        # Pomodoro seansini boshlash
        session_id = db.start_pomodoro_session(user_id, task_id)
        active_pomodoros[user_id] = {
            'session_id': session_id,
            'start_time': datetime.now(),
            'task_id': task_id
        }

        # Timer o'rnatish
        context.job_queue.run_once(
            self.pomodoro_finished_callback,
            POMODORO_WORK_TIME,
            data={'user_id': user_id, 'session_id': session_id}
        )

        await query.edit_message_text(
            f"{MESSAGES['pomodoro_started']}\n\n📝 Vazifa bilan bog'langan!",
            reply_markup=get_active_pomodoro_keyboard()
        )

    async def pomodoro_finished_callback(self, context):
        """Pomodoro tugaganda chaqiriladigan callback"""
        job_data = context.job.data
        user_id = job_data['user_id']
        session_id = job_data['session_id']

        await self.finish_pomodoro(user_id, context)

    async def finish_pomodoro(self, user_id, context):
        """Pomodoro tugatish"""
        if user_id not in active_pomodoros:
            return

        session = active_pomodoros[user_id]
        session_id = session['session_id']

        # Seansni tugatish
        db.finish_pomodoro_session(session_id, POMODORO_WORK_TIME)
        del active_pomodoros[user_id]

        # Foydalanuvchiga xabar yuborish
        try:
            await context.bot.send_message(
                user_id,
                MESSAGES['pomodoro_finished'],
                reply_markup=get_pomodoro_keyboard()
            )

            # Tanaffus timer
            context.job_queue.run_once(
                self.break_finished_callback,
                POMODORO_BREAK_TIME,
                data={'user_id': user_id}
            )
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")

    async def break_finished_callback(self, context):
        """Tanaffus tugaganda chaqiriladigan callback"""
        user_id = context.job.data['user_id']

        try:
            await context.bot.send_message(
                user_id,
                MESSAGES['break_finished'],
                reply_markup=get_pomodoro_keyboard()
            )
        except Exception as e:
            logger.error(f"Tanaffus xabarini yuborishda xatolik: {e}")

    async def stop_pomodoro(self, query, context):
        """Pomodoro to'xtatish"""
        user_id = query.from_user.id

        if user_id not in active_pomodoros:
            await query.edit_message_text("❌ Faol Pomodoro topilmadi!")
            return

        # Seansni to'xtatish
        session = active_pomodoros[user_id]
        elapsed = datetime.now() - session['start_time']
        db.finish_pomodoro_session(session['session_id'], int(elapsed.total_seconds()))

        del active_pomodoros[user_id]

        await query.edit_message_text(
            "⏹ Pomodoro to'xtatildi!\n\nYangi seans boshlashingiz mumkin.",
            reply_markup=get_pomodoro_keyboard()
        )

    async def pause_pomodoro(self, query, context):
        """Pomodoro pauza (hozircha oddiy to'xtatish)"""
        await self.stop_pomodoro(query, context)

    async def show_tasks_menu(self, update, context):
        """Vazifalar menyusini ko'rsatish"""
        text = "📝 Vazifalar menyusi\n\nQuyidagi amallardan birini tanlang:"

        if hasattr(update, 'message'):
            await update.message.reply_text(text, reply_markup=get_tasks_keyboard())
        else:
            await update.edit_message_text(text, reply_markup=get_tasks_keyboard())

    async def add_task_start(self, query, context):
        """Vazifa qo'shishni boshlash"""
        user_id = query.from_user.id

        user_states[user_id] = {
            'state': 'adding_task_title',
            'data': {}
        }

        await query.edit_message_text(
            "📝 Yangi vazifa\n\nVazifa nomini kiriting:"
        )

    async def save_task(self, query, context, priority):
        """Vazifani saqlash"""
        user_id = query.from_user.id

        if user_id not in user_states:
            await query.edit_message_text("❌ Xatolik yuz berdi!")
            return

        data = user_states[user_id]['data']
        title = data['title']
        description = data.get('description', '')

        # Vazifani saqlash
        task_id = db.add_task(user_id, title, description, priority)

        # Holatni tozalash
        del user_states[user_id]

        await query.edit_message_text(
            f"✅ Vazifa qo'shildi!\n\n📝 {title}\n🎯 Muhimlik: {'🔴 Yuqori' if priority == 3 else '🟡 O\'rta' if priority == 2 else '🟢 Past'}",
            reply_markup=get_tasks_keyboard()
        )

    async def list_tasks(self, query, context):
        """Vazifalar ro'yxatini ko'rsatish"""
        user_id = query.from_user.id
        tasks = db.get_user_tasks(user_id, completed=False)

        if not tasks:
            await query.edit_message_text(
                MESSAGES['no_tasks'],
                reply_markup=get_tasks_keyboard()
            )
            return

        await query.edit_message_text(
            f"📋 Sizning vazifalaringiz ({len(tasks)} ta):\n\nVazifani tanlang:",
            reply_markup=get_task_list_keyboard(tasks)
        )

    async def show_task_details(self, query, context, task_id):
        """Vazifa tafsilotlarini ko'rsatish"""
        user_id = query.from_user.id
        tasks = db.get_user_tasks(user_id)

        task = None
        for t in tasks:
            if t['id'] == task_id:
                task = t
                break

        if not task:
            await query.edit_message_text("❌ Vazifa topilmadi!")
            return

        priority_text = "🔴 Yuqori" if task['priority'] == 3 else "🟡 O'rta" if task['priority'] == 2 else "🟢 Past"

        text = f"📝 Vazifa tafsilotlari\n\n"
        text += f"📌 Nom: {task['title']}\n"
        if task['description']:
            text += f"📄 Tavsif: {task['description']}\n"
        text += f"🎯 Muhimlik: {priority_text}\n"
        text += f"📅 Yaratilgan: {task['created_at'][:16]}"

        await query.edit_message_text(
            text,
            reply_markup=get_task_actions_keyboard(task_id)
        )

    async def complete_task(self, query, context, task_id):
        """Vazifani bajarilgan deb belgilash"""
        db.complete_task(task_id)

        await query.edit_message_text(
            MESSAGES['task_completed'],
            reply_markup=get_tasks_keyboard()
        )

    async def delete_task(self, query, context, task_id):
        """Vazifani o'chirish"""
        db.delete_task(task_id)

        await query.edit_message_text(
            MESSAGES['task_deleted'],
            reply_markup=get_tasks_keyboard()
        )

    async def show_stats_menu(self, update, context):
        """Statistika menyusini ko'rsatish"""
        text = "📊 Statistika menyusi\n\nQaysi davr uchun statistikani ko'rmoqchisiz?"

        if hasattr(update, 'message'):
            await update.message.reply_text(text, reply_markup=get_stats_keyboard())
        else:
            await update.edit_message_text(text, reply_markup=get_stats_keyboard())

    async def show_daily_stats(self, query, context):
        """Kunlik statistikani ko'rsatish"""
        user_id = query.from_user.id
        stats = db.get_daily_stats(user_id)

        work_hours = stats['total_work_time'] // 3600
        work_minutes = (stats['total_work_time'] % 3600) // 60

        text = f"📊 Bugungi statistika\n\n"
        text += f"🍅 Pomodoro seanslar: {stats['pomodoros_completed']}\n"
        text += f"✅ Bajarilgan vazifalar: {stats['tasks_completed']}/{stats['total_tasks']}\n"
        text += f"📈 Bajarish foizi: {stats['completion_rate']}%\n"
        text += f"⏰ Ish vaqti: {work_hours}s {work_minutes}d\n\n"

        if stats['completion_rate'] >= 80:
            text += "🎉 Ajoyib natija!"
        elif stats['completion_rate'] >= 60:
            text += "👍 Yaxshi natija!"
        elif stats['completion_rate'] >= 40:
            text += "💪 Yaxshiroq qilishingiz mumkin!"
        else:
            text += "📈 Ertaga ko'proq harakat qiling!"

        await query.edit_message_text(text, reply_markup=get_stats_keyboard())

    async def show_weekly_stats(self, query, context):
        """Haftalik statistikani ko'rsatish"""
        user_id = query.from_user.id
        stats = db.get_weekly_stats(user_id)

        work_hours = stats['total_work_time'] // 3600
        work_minutes = (stats['total_work_time'] % 3600) // 60

        text = f"📈 Haftalik statistika (oxirgi 7 kun)\n\n"
        text += f"🍅 Pomodoro seanslar: {stats['pomodoros_completed']}\n"
        text += f"✅ Bajarilgan vazifalar: {stats['tasks_completed']}/{stats['total_tasks']}\n"
        text += f"📈 Bajarish foizi: {stats['completion_rate']}%\n"
        text += f"⏰ Ish vaqti: {work_hours}s {work_minutes}d\n\n"
        text += f"📊 Kuniga o'rtacha: {stats['pomodoros_completed'] / 7:.1f} Pomodoro"

        await query.edit_message_text(text, reply_markup=get_stats_keyboard())

    async def show_monthly_stats(self, query, context):
        """Oylik statistikani ko'rsatish"""
        user_id = query.from_user.id
        stats = db.get_monthly_stats(user_id)

        work_hours = stats['total_work_time'] // 3600
        work_minutes = (stats['total_work_time'] % 3600) // 60

        text = f"📅 Oylik statistika (oxirgi 30 kun)\n\n"
        text += f"🍅 Pomodoro seanslar: {stats['pomodoros_completed']}\n"
        text += f"✅ Bajarilgan vazifalar: {stats['tasks_completed']}/{stats['total_tasks']}\n"
        text += f"📈 Bajarish foizi: {stats['completion_rate']}%\n"
        text += f"⏰ Ish vaqti: {work_hours}s {work_minutes}d\n\n"
        text += f"📊 Kuniga o'rtacha: {stats['pomodoros_completed'] / 30:.1f} Pomodoro"

        await query.edit_message_text(text, reply_markup=get_stats_keyboard())

    async def show_settings_menu(self, update, context):
        """Sozlamalar menyusini ko'rsatish"""
        text = "⚙️ Sozlamalar\n\nHozircha asosiy sozlamalar mavjud."

        if hasattr(update, 'message'):
            await update.message.reply_text(text, reply_markup=get_settings_keyboard())
        else:
            await update.edit_message_text(text, reply_markup=get_settings_keyboard())

    async def show_admin_users(self, query, context):
        """Admin: foydalanuvchilar ro'yxati"""
        if query.from_user.id not in ADMIN_IDS:
            await query.edit_message_text("❌ Ruxsat yo'q!")
            return

        users_stats = db.get_all_users_stats()

        text = f"👥 Foydalanuvchilar ({len(users_stats)} ta)\n\n"

        for i, user in enumerate(users_stats[:10], 1):  # Faqat birinchi 10 ta
            name = user['first_name'] or user['username'] or f"ID{user['user_id']}"
            text += f"{i}. {name}\n"
            text += f"   🍅 {user['pomodoros']} | ✅ {user['tasks_completed']}\n\n"

        if len(users_stats) > 10:
            text += f"... va yana {len(users_stats) - 10} ta foydalanuvchi"

        await query.edit_message_text(text, reply_markup=get_admin_keyboard())

    async def show_admin_stats(self, query, context):
        """Admin: umumiy statistika"""
        if query.from_user.id not in ADMIN_IDS:
            await query.edit_message_text("❌ Ruxsat yo'q!")
            return

        users_stats = db.get_all_users_stats()

        total_users = len(users_stats)
        total_pomodoros = sum(user['pomodoros'] for user in users_stats)
        total_tasks = sum(user['tasks_completed'] for user in users_stats)
        total_work_time = sum(user['total_work_time'] for user in users_stats)

        work_hours = total_work_time // 3600

        text = f"📊 Umumiy statistika\n\n"
        text += f"👥 Jami foydalanuvchilar: {total_users}\n"
        text += f"🍅 Jami Pomodoro seanslar: {total_pomodoros}\n"
        text += f"✅ Jami bajarilgan vazifalar: {total_tasks}\n"
        text += f"⏰ Jami ish vaqti: {work_hours} soat\n\n"

        if total_users > 0:
            text += f"📈 O'rtacha ko'rsatkichlar:\n"
            text += f"   🍅 {total_pomodoros / total_users:.1f} Pomodoro/foydalanuvchi\n"
            text += f"   ✅ {total_tasks / total_users:.1f} vazifa/foydalanuvchi"

        await query.edit_message_text(text, reply_markup=get_admin_keyboard())

    async def admin_broadcast_start(self, query, context):
        """Admin: xabar yuborish"""
        if query.from_user.id not in ADMIN_IDS:
            await query.edit_message_text("❌ Ruxsat yo'q!")
            return

        user_states[query.from_user.id] = {
            'state': 'admin_broadcast',
            'data': {}
        }

        await query.edit_message_text(
            "📢 Barcha foydalanuvchilarga xabar yuborish\n\n"
            "Xabar matnini kiriting:"
        )

    async def broadcast_message(self, message_text, context):
        """Barcha foydalanuvchilarga xabar yuborish"""
        users_stats = db.get_all_users_stats()

        sent_count = 0
        for user in users_stats:
            try:
                await context.bot.send_message(
                    user['user_id'],
                    f"📢 Admin xabari:\n\n{message_text}"
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # Spam oldini olish uchun
            except Exception as e:
                logger.error(f"Foydalanuvchi {user['user_id']} ga xabar yuborishda xatolik: {e}")

        logger.info(f"Broadcast: {sent_count}/{len(users_stats)} foydalanuvchiga yuborildi")

    async def back_to_main(self, query, context):
        """Asosiy menyuga qaytish"""
        await query.edit_message_text(
            "🏠 Asosiy menyu\n\nQuyidagi tugmalardan birini tanlang:",
            reply_markup=get_main_keyboard()
        )

    def run(self):
        """Botni ishga tushirish"""
        print("🤖 Bot ishga tushmoqda...")
        self.application.run_polling()


if __name__ == "__main__":
    bot = PomodoroBot()
    bot.run()