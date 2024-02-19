# Codenames Online

Codenames Online is a web application that allows users to play the popular board game Codenames online with their
friends. The application consists of both a backend server and a frontend web application.

## Backend

The backend of Codenames Online is built using Flask, Socket.IO, and SQLAlchemy.

### Features

- **Real-time Gameplay**: Enjoy real-time gameplay with your friends through WebSocket communication.
- **Authentication**: Users can authenticate using simple token generation.
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

## Frontend

The frontend of Codenames Online is built using Angular and communicates with the backend server using WebSocket for
real-time updates.

## Features

- Real-time updates using WebSocket communication
- Multiple players support with team assignments
- Spymaster mode for each team
- Dynamic game board with clickable tiles

### Prerequisites

- Node.js and npm installed on your machine
- Angular CLI installed globally (`npm install -g @angular/cli`)

### Installation

1. Navigate into the project directory
   ```sh
   cd your_project/frontend
   ```
2. Install dependencies
   ```sh
   npm install
   ```

### Usage

1. Start the development server
   ```sh
   ng serve --host 0.0.0.0 --port 4200 
   ```

### Open your browser and navigate to `http://localhost:4200` to view the application.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
