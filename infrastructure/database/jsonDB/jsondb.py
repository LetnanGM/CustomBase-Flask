from typing import Any
from .components.crud import OperateC
from share.contract.database.Storage import Storage


class JsonDB(OperateC, Storage):
    __TITLE__ = "JsonDB"
    __VERSION__ = "1.0.0"
    __DEVELOPER__ = "LetnanGM"
    __LICENSE__ = "MIT License"

    def __init__(self, path_db: str) -> None:
        super().__init__(path_db=path_db)

        self._path = path_db
        self._db = {}
        self._loaded = False

    def load_db(self) -> None:
        """
        Handling load database
        """
        from share.support.file import File

        instance = File(path_file=self._path)
        response = instance.Read()

        self._db = response.json or {}
        self._loaded = True

    def write_db(self) -> None:
        """
        Handling write database
        """
        from share.support.file import File

        self._ensure_loaded()
        File(path_file=self._path).Write(Message=self._db).to_json

    def reload_db(self) -> None:
        """
        Handling 'reload' with Write & Load database
        """
        print("Reloading DB..")
        self.write_db()

    def find_as_id(self, id: str | None = ...) -> Any:
        self._ensure_loaded()
        return self._db.get(id)

    # 🔒 safety guard
    def _ensure_loaded(self):
        if not self._loaded:
            raise RuntimeError("Database belum di-load! Panggil load_db() dulu.")
