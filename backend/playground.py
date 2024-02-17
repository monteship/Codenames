import os
import random
import json
from typing import Literal, Optional, Dict


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


class CodenameGenerator:
    def __init__(self, codenames_list):
        self.codenames = random.sample(codenames_list, 25)

    def gen(self):
        codename = random.choice(self.codenames)
        self.codenames.remove(codename)
        return codename

    def get_codenames(self, color: str, count: int):
        return [
            dict(word=self.gen(), color=color, clicked=False) for _ in range(0, count)
        ]


class Playground:
    def __init__(self, session: str = "default"):
        self.session = session
        self._codenames: Optional[Dict[str, str, list]] = None
        self.words_loader = WordsLoader()

    def __generate_game(self):
        generator = CodenameGenerator(self.words_loader.get["codenames"])
        team_words_counts = [8, 9]
        random.shuffle(team_words_counts)

        data = {
            "score": {
                "initial_score_red": 0,
                "score_red": 0,
                "initial_score_blue": 0,
                "score_blue": 0,
            },
            "codenames": [],
        }
        for color, count in zip(["blue", "red"], team_words_counts):
            data["score"][f"initial_score_{color}"] = count
            data["codenames"].extend(generator.get_codenames(color, count))

        data["codenames"].extend(generator.get_codenames(color="yellow", count=7))
        data["codenames"].extend(generator.get_codenames(color="black", count=1))

        random.shuffle(data["codenames"])

        self._codenames = data

    def get_nickname(self):
        return f"{random.choice(self.words_loader.get['noun']).capitalize()} {random.choice(self.words_loader.get['adjective'])}"

    def trigger_click(self, word) -> str:
        for codename in self.codenames["codenames"]:
            if codename["word"] == word:
                codename["clicked"] = True
                color = codename["color"]
                if color in ["red", "blue"]:
                    self.codenames["score"][f"score_{color}"] += 1
                return color
        return "white"

    def restart_game(self):
        self.__generate_game()

    @property
    def codenames(self) -> dict:
        if self._codenames is None:
            self.__generate_game()
        return self._codenames
