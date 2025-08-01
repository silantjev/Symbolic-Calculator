import os
# import sqlite3
import json
from pathlib import Path

DEFAULT_DB_DIR = Path(os.path.expanduser('~/.symcalc'))

def make_path(path):
    path = Path(path)
    if path.parent == Path("."):
        path = Path(DEFAULT_DB_DIR) / path
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    return path

class JSONStorage:
    DEFAULT_DB_FILENAME = 'sessions.json'
    
    def __init__(self, json_path=""):
        if not json_path:
            json_path = self.DEFAULT_DB_FILENAME
        self.json_path = make_path(json_path)
        if not self.json_path.exists():
            with open(self.json_path, 'w', encoding="utf-8") as f:
                json.dump({}, f)

    def save(self, session_data, session_id):
        with open(self.json_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(session_data, dict)
        data[str(session_id)] = session_data
        with open(self.json_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self, session_id):
        with open(self.json_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(session_id), {})

class StateManager:
    def __init__(self, storage, logger):
        self.storage = storage
        self.logger = logger
        self.logger.info("Session file '%s' found or created", self.storage.json_path)

    def save_state(self, calc, session_id=0):
        session_data = calc.get_session()
        self.storage.save(session_data, session_id=session_id)

    def load_state(self, calc, session_id=0):
        try:
            session_data = self.storage.load(session_id=session_id)
            if session_data:
                calc.load_state(session_data)
            else:
                self.logger.warning("Failed to load data from json")
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self.logger.error("Error: Failed to load data %s", exc)

class ClientStateManager:

    def save_state(self, calc, session_id=0):
        calc.save_state(session_id=session_id)

    def load_state(self, calc, session_id=0):
        pass
