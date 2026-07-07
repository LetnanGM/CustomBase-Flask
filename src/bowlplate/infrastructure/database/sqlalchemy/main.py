from sqlalchemy import create_engine

from bowlplate.contract.database.Storage import Storage


class database_context:
    engine = create_engine("sqlite:////data")


class SQLDB(Storage):
    def __init__(self, path_db=...):
        super().__init__(path_db)
        self._session = None
