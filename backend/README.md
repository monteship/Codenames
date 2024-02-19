# Codenames Server

Codenames Online is a web application that allows users to play the popular board game Codenames online with their
friends. The application is built using Flask, Socket.IO, and SQLAlchemy.

## Features

- **Real-time Gameplay**: Enjoy real-time gameplay with your friends through WebSocket communication.
- **Authentication**: Users can authenticate using ~~JWT tokens~~ simple token generation.
- **Role-based Access Control**: Different roles such as players and spymasters have access to different
  functionalities.
- **Persistent Data**: Data such as game state and user information is stored in a SQLite database.

## Installation

1. Navigate to the project directory:
   ```sh
   cd your_project/backend
   ```
2. Install dependencies:
    ```sh
   pip install -r requirements.txt
   ```

### Usage

1. Run the application:
    ```sh
    gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 app:app
    ```

### Access the application at frontend with [http://localhost:5000](http://localhost:5000).

## Features

- **Login**: Users obtain username which associate with token.
- ~~**Create or Join Game**: Users can create a new game or join an existing game by entering the game name.~~
- **Gameplay**: Once in a game, players can take turns guessing words based on the clues provided by the spymaster.
- **End Game**: The game ends when one team successfully identifies all their words, or when the assassin word is
  chosen.
- **Restart Game**: Players and Spymasters can restart the game at any time.

