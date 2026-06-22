from dataclasses import dataclass
from sqlite3 import Connection, Cursor, connect


@dataclass
class Database:
    conn : Connection
    cur  : Cursor


class SQLite:
    def __init__(self, db: str) -> None:
        self._conn: Connection = connect(db)
        self.cur = self._conn.cursor()
        
    @property
    def get_db(self) -> Database:
        return Database(conn=self._conn, cur=self.cur)