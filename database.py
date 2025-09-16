import sqlite3
from datetime import datetime


class Database:

    def __init__(self,table_name):
        self.connection = sqlite3.connect(table_name,check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_personal_user(self, full_name, username):
        self.cursor.execute(
            "INSERT INTO personal_users(full_name, username) VALUES (?, ?)",
            (full_name, username),
        )
        self.connection.commit()

    def create_personal_plan(self, user_id, plan_type, title, description,
                             status="kutilmoqda", start_date=None, end_date=None):
        self.cursor.execute("""
            INSERT INTO personal_plans(user_id, plan_type, title, description, status, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, plan_type, title, description, status,
              start_date, end_date, datetime.now()))
        self.connection.commit()

    def create_personal_result(self, user_id, plan_id, result_text):
        self.cursor.execute("""
            INSERT INTO personal_results(user_id, plan_id, result_text, result_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, plan_id, result_text, datetime.now().date()))
        self.connection.commit()

    def get_personal_results(self, user_id):
        self.cursor.execute("SELECT * FROM personal_results WHERE user_id = ?", (user_id,))
        return dict_fetchall(self.cursor)

    # ========================
    # Biznes metodlari
    # ========================

    def create_business_user(self, full_name, username, role):
        self.cursor.execute(
            "INSERT INTO business_users(full_name, username, role) VALUES (?, ?, ?)",
            (full_name, username, role),
        )
        self.connection.commit()

    def create_business_task(self, assigned_to, assigned_by, task_type, title, description,
                             status="kutilmoqda", start_date=None, end_date=None):
        self.cursor.execute("""
            INSERT INTO business_tasks(assigned_to, assigned_by, task_type, title, description, status, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (assigned_to, assigned_by, task_type, title, description, status,
              start_date, end_date, datetime.now()))
        self.connection.commit()

    def create_business_report(self, user_id, task_id, work_hours, result_text):
        self.cursor.execute("""
            INSERT INTO business_reports(user_id, task_id, work_hours, result_text, result_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, task_id, work_hours, result_text, datetime.now().date()))
        self.connection.commit()

    def get_business_reports(self, user_id):
        self.cursor.execute("SELECT * FROM business_reports WHERE user_id = ?", (user_id,))
        return dict_fetchall(self.cursor)




def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))