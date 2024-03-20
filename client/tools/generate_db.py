import aiosqlite
import sqlite3
import asyncio
import hashlib
import time
import random

class AccountGenerator:
    def __init__(self, db_name):
        self.db_name = db_name

        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, login TEXT, password TEXT, hash_id TEXT, user_name TEXT, server TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id TEXT, text TEXT, timestamp FLOAT, chat_id INTEGER)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, user_id TEXT, public_key TEXT, our_private_key TEXT, nick_name TEXT, status TEXT, chat_id INTEGER)")

        conn.commit()
        conn.close()

        return True


    def create_account(self, login, password, user_name, server):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return None  # уже существует запись, создание второй запрещено

        hash_id = self.generate_user_id(login)

        cursor.execute("INSERT INTO accounts (login, password, hash_id, user_name, server) VALUES (?, ?, ?, ?, ?)",
                       (login, self._hash_password(password), hash_id, user_name, server))

        conn.commit()
        conn.close()

        return True

    def get_my_id(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT hash_id FROM accounts")
        row = cursor.fetchone()
        return row


    def get_username(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT user_name FROM accounts")
        row = cursor.fetchone()
        return row

    def get_nickname(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT nick_name FROM contacts WHERE user_id = ?", (user_id, ))
        row = cursor.fetchone()
        return row[0]


    def add_contact(self, user_id, public_key, our_private_key, nickname, status, chat_id):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute("INSERT INTO contacts (user_id, public_key, our_private_key, nick_name, status, chat_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, public_key, our_private_key, nickname, status, chat_id))
        conn.commit()
        conn.close()

    def update_contact(self, public_key, status, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE contacts SET public_key = ?, status = ? WHERE user_id = ?",
                       (public_key, status, user_id))
        conn.commit()
        conn.close()

    def get_contact(self, chat_id):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cursor = cur.execute("SELECT user_id, public_key, our_private_key, nick_name FROM contacts WHERE chat_id = ?", (chat_id,))
        contact = cursor.fetchone()
        return contact

    def add_server(self, user_name, server):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET user_name = ?, server = ? WHERE id = ?",
                       (user_name, server, 1))
        conn.commit()
        conn.close()

    def add_message(self, user_id, text, timestamp, chat_id):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute("INSERT INTO messages (user_id, text, timestamp, chat_id) VALUES (?, ?, ?, ?)",
                             (user_id, text, timestamp, chat_id))
        conn.commit()

    async def add_all_messages(self, data):
        async with aiosqlite.connect(self.db_name) as db:
            await db.executemany('INSERT INTO messages (user_id, text, timestamp, chat_id) VALUES (?, ?, ?, ?)', data)
            await db.commit()

    def get_messages(self, chat_id):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cursor = cur.execute("SELECT * FROM messages WHERE chat_id = ?", (chat_id,))
        messages = cursor.fetchall()
        return messages

    def get_my_contacts(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cursor = cur.execute("SELECT * FROM contacts")
        messages = cursor.fetchall()
        return messages

    def check_password(self, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM accounts")
        db_password = cursor.fetchone()

        conn.close()

        if db_password[0] == self._hash_password(password):
            return True
        else:
            return False

    def get_server(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT server FROM accounts")
        db_password = cursor.fetchone()
        conn.close()

        return db_password[0]


    def generate_user_id(self, login):
        simple_salt = str(random.randint(10000, 1000000))
        return hashlib.sha1((simple_salt + login).encode()).hexdigest()

    def _hash_password(self, password):
        return hashlib.sha1(password.encode()).hexdigest()

