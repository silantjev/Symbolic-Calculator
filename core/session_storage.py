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
    
    def __init__(self, logger, json_path=""):
        self.logger = logger
        if not json_path:
            json_path = self.DEFAULT_DB_FILENAME
        self.json_path = make_path(json_path)
        if self.json_path.exists():
            self.logger.info("Session file '%s' found", self.json_path)
        else:
            self.logger.warning(f"Session file '%s' not found", self.json_path)
            self._new_file()

    def _new_file(self):
        with open(self.json_path, 'w', encoding="utf-8") as f:
            json.dump({}, f)
            self.logger.info(f"Empty file '%s' created", self.json_path)

    def _load(self):
        try:
            with open(self.json_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError as exc:
            self.logger.error(f"Failed to read the file '%s'. Error: %s", self.json_path, exc)
            self._new_file()
            data = {}
        return data

    def save(self, session_data, session_id):
        assert isinstance(session_data, dict)
        data = self._load()
        data[str(session_id)] = session_data
        with open(self.json_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        self.logger.info("Session saved to '%s'", self.json_path)

    def load(self, session_id):
        data = self._load()
        return data.get(str(session_id), {})

class StateManager:
    def __init__(self, storage):
        self.storage = storage
        self.logger = storage.logger

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
