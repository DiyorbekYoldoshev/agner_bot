import sqlite3
import datetime
from typing import List, Dict
from config import DATABASE_FILE


class Database:
    def __init__(self):
        self.init_database()

    def init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Foydalanuvchilar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # Vazifalar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 1,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Pomodoro seanslar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_id INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                duration INTEGER,
                is_completed BOOLEAN DEFAULT 0,
                session_type TEXT DEFAULT 'work',
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')

        # Kunlik statistika jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                pomodoros_completed INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                total_work_time INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, date)
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Yangi foydalanuvchi qo'shish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))

        conn.commit()
        conn.close()

    def add_task(self, user_id: int, title: str, description: str = None, priority: int = 1):
        """Yangi vazifa qo'shish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tasks (user_id, title, description, priority)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, priority))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_user_tasks(self, user_id: int, completed: bool = False) -> List[Dict]:
        """Foydalanuvchi vazifalarini olish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, description, priority, created_at, completed_at
            FROM tasks
            WHERE user_id = ? AND is_completed = ?
            ORDER BY priority DESC, created_at ASC
        ''', (user_id, completed))

        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'created_at': row[4],
                'completed_at': row[5]
            })

        conn.close()
        return tasks

    def complete_task(self, task_id: int):
        """Vazifani bajarilgan deb belgilash"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE tasks 
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))

        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        """Vazifani o'chirish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

        conn.commit()
        conn.close()

    def start_pomodoro_session(self, user_id: int, task_id: int = None):
        """Pomodoro seansini boshlash"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO pomodoro_sessions (user_id, task_id, session_type)
            VALUES (?, ?, 'work')
        ''', (user_id, task_id))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def finish_pomodoro_session(self, session_id: int, duration: int):
        """Pomodoro seansini tugatish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE pomodoro_sessions 
            SET finished_at = CURRENT_TIMESTAMP, duration = ?, is_completed = 1
            WHERE id = ?
        ''', (duration, session_id))

        conn.commit()
        conn.close()

    def get_daily_stats(self, user_id: int, date: str = None) -> Dict:
        """Kunlik statistikani olish"""
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Pomodoro seanslar
        cursor.execute('''
            SELECT COUNT(*), SUM(duration)
            FROM pomodoro_sessions
            WHERE user_id = ? AND DATE(started_at) = ? AND is_completed = 1
        ''', (user_id, date))

        pomodoro_data = cursor.fetchone()
        pomodoros_completed = pomodoro_data[0] or 0
        total_work_time = pomodoro_data[1] or 0

        # Bajarilgan vazifalar
        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND DATE(completed_at) = ? AND is_completed = 1
        ''', (user_id, date))

        tasks_completed = cursor.fetchone()[0] or 0

        # Jami vazifalar
        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND DATE(created_at) = ?
        ''', (user_id, date))

        total_tasks = cursor.fetchone()[0] or 0

        conn.close()

        completion_rate = (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0

        return {
            'date': date,
            'pomodoros_completed': pomodoros_completed,
            'tasks_completed': tasks_completed,
            'total_tasks': total_tasks,
            'completion_rate': round(completion_rate, 1),
            'total_work_time': total_work_time
        }

    def get_weekly_stats(self, user_id: int) -> Dict:
        """Haftalik statistikani olish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Oxirgi 7 kun
        cursor.execute('''
            SELECT COUNT(*), SUM(duration)
            FROM pomodoro_sessions
            WHERE user_id = ? AND started_at >= DATE('now', '-7 days') AND is_completed = 1
        ''', (user_id,))

        pomodoro_data = cursor.fetchone()
        pomodoros_completed = pomodoro_data[0] or 0
        total_work_time = pomodoro_data[1] or 0

        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND completed_at >= DATE('now', '-7 days') AND is_completed = 1
        ''', (user_id,))

        tasks_completed = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND created_at >= DATE('now', '-7 days')
        ''', (user_id,))

        total_tasks = cursor.fetchone()[0] or 0

        conn.close()

        completion_rate = (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0

        return {
            'pomodoros_completed': pomodoros_completed,
            'tasks_completed': tasks_completed,
            'total_tasks': total_tasks,
            'completion_rate': round(completion_rate, 1),
            'total_work_time': total_work_time
        }

    def get_monthly_stats(self, user_id: int) -> Dict:
        """Oylik statistikani olish"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Oxirgi 30 kun
        cursor.execute('''
            SELECT COUNT(*), SUM(duration)
            FROM pomodoro_sessions
            WHERE user_id = ? AND started_at >= DATE('now', '-30 days') AND is_completed = 1
        ''', (user_id,))

        pomodoro_data = cursor.fetchone()
        pomodoros_completed = pomodoro_data[0] or 0
        total_work_time = pomodoro_data[1] or 0

        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND completed_at >= DATE('now', '-30 days') AND is_completed = 1
        ''', (user_id,))

        tasks_completed = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT COUNT(*)
            FROM tasks
            WHERE user_id = ? AND created_at >= DATE('now', '-30 days')
        ''', (user_id,))

        total_tasks = cursor.fetchone()[0] or 0

        conn.close()

        completion_rate = (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0

        return {
            'pomodoros_completed': pomodoros_completed,
            'tasks_completed': tasks_completed,
            'total_tasks': total_tasks,
            'completion_rate': round(completion_rate, 1),
            'total_work_time': total_work_time
        }

    def get_all_users_stats(self) -> List[Dict]:
        """Barcha foydalanuvchilar statistikasi (admin uchun)"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.username, u.first_name, u.last_name,
                   COUNT(DISTINCT p.id) as pomodoros,
                   COUNT(DISTINCT t.id) as tasks_completed,
                   SUM(p.duration) as total_work_time
            FROM users u
            LEFT JOIN pomodoro_sessions p ON u.user_id = p.user_id AND p.is_completed = 1
            LEFT JOIN tasks t ON u.user_id = t.user_id AND t.is_completed = 1
            WHERE u.is_active = 1
            GROUP BY u.user_id
            ORDER BY pomodoros DESC
        ''')

        users_stats = []
        for row in cursor.fetchall():
            users_stats.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'pomodoros': row[4] or 0,
                'tasks_completed': row[5] or 0,
                'total_work_time': row[6] or 0
            })

        conn.close()
        return users_stats