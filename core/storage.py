import json
import os
from datetime import datetime
from config import notes_file, settings_file


class NotesStorage:
    def __init__(self):
        self.notes = []
        self.load()

    def load(self):
        if os.path.exists(notes_file):
            try:
                with open(notes_file, "r", encoding="utf-8") as f:
                    self.notes = json.load(f)
            except:
                self.notes = []

    def save(self):
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def create(self, title, content):
        note = {
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "pinned": False
        }
        self.notes.insert(0, note)
        self.save()
        return 0

    def update(self, index, title, content):
        if 0 <= index < len(self.notes):
            pinned = self.notes[index].get("pinned", False)
            self.notes[index] = {
                "title": title,
                "content": content,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "pinned": pinned
            }
            self.save()

    def delete(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]
            self.save()

    def get(self, index):
        if 0 <= index < len(self.notes):
            return self.notes[index]
        return None

    def toggle_pin(self, index):
        if 0 <= index < len(self.notes):
            self.notes[index]["pinned"] = not self.notes[index].get("pinned", False)
            self.save()
            return self.notes[index]["pinned"]
        return False


class AppSettings:
    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = {}

    def save(self):
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()