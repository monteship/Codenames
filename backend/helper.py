import os
import random
import json
from typing import Literal


class WordsLoader:
    def __init__(self, language: Literal["en", "ru", "ua"] = "ua"):
        self.language = language
        self.path = os.path.join("config.json")

    def __load(self):
        with open(self.path, "r") as f:
            lang_data = json.load(f)[self.language]
            if lang_data:
                self._codenames = lang_data.get("codenames", [])
                self._noun = lang_data.get("noun", [])
                self._adjective = lang_data.get("adjective", [])
            else:
                raise ValueError("Language data not found")

    def __add(self, key: Literal["codenames", "noun", "adjective"], word):
        if key in self._codenames:
            return

        if word not in getattr(self, f"_{key}"):
            with open(self.path, "r+") as f:
                data = json.load(f)
                data[self.language][key].append(word)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

    @property
    def get(self) -> dict:
        if not hasattr(self, "_codenames"):
            self.__load()
        return {
            "codenames": self._codenames,
            "noun": self._noun,
            "adjective": self._adjective,
        }

    def add(self, word_type: Literal["codenames", "noun", "adjective"], word):
        if word_type in ["codenames", "noun", "adjective"]:
            self.__add(word_type, word)
        else:
            raise ValueError("Invalid word type")

    def get_nickname(self):
        if not hasattr(self, "_noun"):
            self.__load()
        return (
            f"{random.choice(self._noun).capitalize()} {random.choice(self._adjective)}"
        )
