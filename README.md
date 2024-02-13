# Codenames Online

Codenames Online is a web-based multiplayer version of the popular board game Codenames, allowing players to enjoy the game remotely with friends or strangers.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Codenames is a word-based party game designed by Vlaada Chvátil. It has gained popularity due to its simple yet engaging gameplay, making it a favorite among board game enthusiasts. Codenames Online aims to bring the same excitement of the physical game to the digital realm, allowing players to join games, guess words, and strategize with their teammates in real-time.

## Features

- Real-time multiplayer gameplay
- Support for multiple teams and customizable game settings
- WebSocket communication for instant updates
- Interactive game board with dynamic word coloring
- User-friendly interface for easy navigation
- Ability to restart games and end them when necessary

## Technologies Used

- **Backend:** Python (Flask), Flask-SocketIO
- **Frontend:** Angular, Socket.IO client
- **Communication:** WebSocket
- **Styling:** CSS
- **Database:** None (data stored in memory)

## Getting Started

To get started with Codenames Online, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies for both the backend (Python) and frontend (Angular).
3. Start the Flask server to run the backend.
4. Open the Angular application in your browser to access the frontend.

## Usage

- Upon opening the application, players can join an existing game or create a new one.
- Once in a game, players will be assigned to different teams and given words to guess.
- Teams take turns guessing words based on clues provided by their spymaster.
- The game continues until one team successfully identifies all their words or the assassin word is chosen.
- Players can restart the game or end it when desired.

## Contributing

Contributions to Codenames Online are welcome! If you'd like to contribute to the project, feel free to fork the repository and submit a pull request with your changes. Be sure to follow the contribution guidelines outlined in the repository.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code for your own purposes.
