from dataclasses import dataclass
from sqlite3 import Connection, Cursor, connect

import os

_suffix: str = ".db"


@dataclass
class Database:
    conn: Connection
    cur: Cursor


class SQLite:
    def __init__(self, db: str) -> None:
        if not os.path.exists(db):
            from pathlib import Path

            db_path = Path(db)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn: Connection = connect(db)
        self.cur = self._conn.cursor()

    @property
    def get_db(self) -> Database:
        return Database(conn=self._conn, cur=self.cur)
