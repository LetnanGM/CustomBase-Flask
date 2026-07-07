from pydantic import BaseModel, field_validator
from typing import List, Dict, Any

from bowlplate.bootstrap.sql import SQLite, Database
from bowlplate.share.builtns.handler.decorator import validate_parameter

# name indicator 'manifest.json' for read file, you can customized where metadata plugin file.
_name_file: str = "manifest"
_suffix: str = ".json"


def _get_current_version() -> None:
    from bowlplate.bootstrap.config import reader as conf

    data = conf.get("config.json")
    version = data["config"]["version"]
    return version


class Hooks(BaseModel):
    startup: str | None = None
    shutdown: str | None = None


class Requirements(BaseModel):
    enable: bool
    min_framework_version: str
    max_framework_version: str


class Metadata(BaseModel):
    author: str
    description: str
    product_type: str
    visibility: str

    @field_validator("visibility")
    @classmethod
    def visibility_settings(cls, visibility: str) -> str:
        allowed = {"public", "private"}
        value = visibility.lower()

        if value not in allowed:
            raise ValueError(
                "visibility at: product plugin doesn't accepted by server, must be 'private' or 'public'."
            )

        return value


class Manifest(BaseModel):
    name: str
    version: str
    type: str

    description: str
    service: str
    entrypoint: str
    priority: int

    hooks: Hooks
    provides: List[str]
    requires: List[str]

    dependencies: Dict[str, str]
    requirements: Requirements
    metadata: Metadata

    @field_validator("entrypoint")
    @classmethod
    def validate_entrypoint(cls, value: str) -> str:
        if ":" not in value:
            raise ValueError("entrypoint must use format module:function")

        return value


class DBase:
    def __init__(self) -> None:
        from bowlplate.data import database_path
        import os

        self.db: Database = SQLite(db=os.path.join(database_path, "plugins.db")).get_db

        self.cur = self.db.cur
        self.con = self.db.conn
        self.create_table("plugins")

    def create_table(self, table_name: str) -> bool:
        """ """

        self.cur.execute("""
CREATE TABLE IF NOT EXISTS plugins (
    key TEXT PRIMARY KEY,
    value TEXT
)
        """)
        self.con.commit()
        return True

    @validate_parameter({"column_name": str, "manifest_data": Dict[str, Any]})
    def insert(
        self,
        column_name: str,
        manifest_data: Dict[str, Any],
        force_update: bool = False,
    ) -> bool:
        if isinstance(manifest_data, dict):
            import json

            manifest_data = json.dumps(obj=manifest_data)

        if not force_update:
            self.cur.execute(
                """
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value;
            """,
                (column_name, manifest_data),
            )

        else:
            self.cur.execute(
                """
            INSERT INTO config (key, value) VALUES (?, ?);
                """,
                (column_name, manifest_data),
            )

        self.con.commit()
        return True

    @validate_parameter({"col_name": str})
    def get(self, col_name: str) -> dict | None:
        import json

        self.cur.execute(
            """
            SELECT value FROM config WHERE key=?
            """,
            (col_name,),
        )

        row = self.cur.fetchone()
        if row is not None:
            return json.loads(row[0])

        return None


class Parser:
    def __init__(self) -> None:
        self.manifest_instance: Manifest = None
        self.db = DBase()

    @property
    def data_manifest(self) -> Manifest:
        return self.manifest_instance if self.manifest_instance else None

    def load_manifest(self, manifest_file: str) -> Manifest | None:
        from pathlib import Path
        from bowlplate.support.file.FileHandling import File

        try:
            absp = Path(manifest_file).resolve()

            if absp.suffix != _suffix:
                print(
                    f"[!] Runtime: can't read manifest from {manifest_file}\n[!] cause manifest doesn't compatible with our software. [allowed json, not {absp.suffix}]"
                )
                return False

            if absp.stem != _name_file:
                print(
                    f"[!] Software only can read '{_name_file}.{_suffix}', not {absp.name + '.' + absp.suffix}"
                )
                return False

            data = File(str(absp)).Read().json

            # update for dev :D
            # and this db is registry plugin :D
            self.db.insert(column_name=absp.name, manifest_data=data, force_update=True)

            self.manifest_instance = Manifest(**data)

        # temporary prevent error from plugin :D
        except Exception as e:
            print(f"[!] kernel:plugin>load:manifest > {e}")

        return self.manifest_instance
