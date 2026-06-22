from bootstrap.sql import SQLite, Database
from share.shared.handler.decorator import validate_parameter


class state:
    loaded: bool = False

class DBase:
    def __init__(self):
        self.db: Database = SQLite("data/database/config.db").get_db
        
        self.cur = self.db.cur
        self.con = self.db.conn
        self.create_table()
        
    @property
    def configs(self):
        self.db.cur.execute(
            "SELECT key FROM config"
        )
        return [r[0] for r in self.db.cur.fetchall()]
    
    def create_table(self) -> None: 
        """
        
        """
        self.cur.execute("""
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT
)               
        """)
        self.con.commit(
            
        )
        
        return True

    @validate_parameter({"column_name": str, "json_data": dict | str})
    def insert(self, column_name: str, json_data: dict | str, force_update: bool = False) -> None:
        """
        
        """
        if isinstance(json_data, dict):
            import json
            json_data = json.dumps(obj=json_data)
        
        if not force_update:
            self.cur.execute(
                """
        INSERT INTO config (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value;
                """,
                (column_name, json_data)
            )
        else:
            self.cur.execute("""
        INSERT INTO config (key, value) VALUES (?, ?);
            """, (column_name, json_data))
        
        self.con.commit()
        return True
    
    @validate_parameter({"config_name": str})
    def get_config(self, config_name: str) -> None:
        """
        
        """
        import json
        
        self.cur.execute("""
SELECT value FROM config WHERE key=?
        """, (config_name,))
        
        row = self.cur.fetchone()
        
        if row is not None:
            return json.loads(row[0])
        
        return None
        
class reader:
    def __init__(self) -> None:
        from data import config_path
        
        self._config_path = config_path
        self.suffix = "json"
        self.db = DBase()
        
        self._loader()
            
    @property
    def configs(self):
        return self.db.configs
        
    def _loader(self) -> None:
        import json
        from pathlib import Path
        
        base = Path(self._config_path)
        for file in base.rglob(f"*.{self.suffix}"):
            try:
                with open(file, "r") as fp:
                    data = json.load(fp=fp)
                
                self.db.insert(
                    column_name=file.name,
                    json_data=data
                )
            except json.JSONDecodeError as e:
                print(f"[!] Error: '{file}'. \n{e}")
                
        state.loaded = True
    
    def get(self, key: str) -> None:
        """
        absolute path already handled by system.
        just need key file 'where'.
        
        example:
        >>> read = reader()
        >>> read.get("server.json")
        
        'how i can know the key?',
        you can do 'read.configs', this is property list of config loaded.
        
        Params:
            key: key config file.

        Return:
            None
        """
        return self.db.get_config(key)