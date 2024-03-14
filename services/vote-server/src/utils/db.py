import sqlite3
from .constants import DB_PATH


class DB:
    conn = None

    def __init__(self, path: str = DB_PATH):
        if self.conn is None:
            self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
