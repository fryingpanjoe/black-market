import sqlite3
from contextlib import closing
import crypt

DEFAULT_DATABASE = 'bm_account.db'
MEMORY_DATABASE = ':memory:'

USER_TABLE_SCRIPT = """create table bm_account_users(
        user_id integer primary key autoincrement
    ,   name text unique
    ,   password text
    ,   email text unique
    ,   suspended integer default 0
    ,   deleted integer default 0
    ,   created_at datetime default current_timestamp
);"""


class AccountStore(object):

    def __init__(self, filename=DEFAULT_DATABASE):
        self.filename = filename
        self.db = sqlite3.connect(filename)

    def first_run(self):
        with closing(self.db.cursor()) as cur:
            cur.execute(USER_TABLE_SCRIPT)

    def close(self):
        self.db.close()

    def add_user(self, name, raw_password, email):
        encrypted_password = crypt.encrypt_password(raw_password)
        with closing(self.db.cursor()) as cur:
            try:
                cur.execute(
                    'insert into bm_account_users (name, password, email) values (?,?,?)',
                    (name, encrypted_password, email,))
                cur.execute('select last_insert_rowid()')
                user_id = cur.fetchone()[0]
            except sqlite3.DatabaseError:
                self.db.rollback()
                return None
            else:
                self.db.commit()
                return user_id

    def delete_user(self, user_id):
        with closing(self.db.cursor()) as cur:
            try:
                cur.execute(
                    'update bm_account_users set deleted = 1 where user_id = ?',
                    (user_id,))
            except sqlite3.DatabaseError:
                self.db.rollback()
                return False
            else:
                self.db.commit()
                return True

    def authenticate_user(self, name, raw_password):
        with closing(self.db.cursor()) as cur:
            try:
                cur.execute(
                    'select user_id, password from bm_account_users where name = ? limit 1',
                    (name,))
            except sqlite3.DatabaseError:
                pass
            else:
                data = cur.fetchone()
                if data:
                    user_id, encrypted_password = data
                    if crypt.check_password(raw_password, encrypted_password):
                        return user_id
        return None
