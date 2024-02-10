from pprint import pprint

from flask import Flask, render_template, request
import random

app = Flask(__name__)

# List of codenames for the game
codenames = [
    "Apple",
    "Banana",
    "Orange",
    "Table",
    "Chair",
    "Computer",
    "Keyboard",
    "Mouse",
    "Dog",
    "Cat",
    "Car",
    "Train",
    "Plane",
    "Boat",
    "Building",
    "Tree",
    "Mountain",
    "River",
    "Ocean",
    "Lake",
    "Apple",
    "Banana",
    "Orange",
    "Table",
    "Chair",
    "Computer",
    "Keyboard",
    "Mouse",
    "Dog",
    "Cat",
    "Car",
    "Train",
    "Plane",
    "Boat",
    "Building",
    "Tree",
    "Mountain",
    "River",
    "Ocean",
    "Lake",
]

words = None


class RandomCodeNameGenerator:
    def __init__(self, codenames_list: list):
        self.codenames_list = codenames_list

    def generate(self):
        word = random.choice(self.codenames_list)
        self.codenames_list.remove(word)
        return word


@app.route("/restart", methods=["POST"])
def restart():
    global words
    code_name_generator = RandomCodeNameGenerator(codenames_list=codenames.copy())
    team_words_quantity = [8, 9]
    random.shuffle(team_words_quantity)
    words = []
    for team, quantity in zip(["BLUE", "RED"], team_words_quantity):
        words.extend(
            [{code_name_generator.generate(): team} for _ in range(0, quantity)]
        )
    words.extend([{code_name_generator.generate(): "YELLOW"} for _ in range(6 + 1)])
    words.append({code_name_generator.generate(): "BLACK"})
    random.shuffle(words)
    words = [words[i : i + 5] for i in range(0, len(words), 5)]
    return render_template("index.html", words=words)


@app.route("/", methods=["GET"])
def home():
    global words
    if words is None:
        restart()
    return render_template("index.html", words=words)


if __name__ == "__main__":
    app.run(debug=True)
