import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {io, Socket} from 'socket.io-client';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';

interface Codename {
  name: string;
  color: string;
  state: boolean;
}

interface GameData {
  red_initial_score: number;
  blue_initial_score: number;

  red_score: number;
  blue_score: number;

  codenames: Codename[];
}

interface Team {
  players: string[];
  spymaster: string[]
}

interface Players {
  red: Team;
  blue: Team;
  grey: Team;
}

@Component({
  standalone: true,
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [CommonModule, HttpClientModule,
    FormsModule]
})

export class AppComponent implements OnInit {
  ws: Socket;
  gameData: any[] = [];
  name: string | null = localStorage.getItem('username');
  redSpymaster: string = "Spymaster";
  blueSpymaster: string = "Spymaster";

  redTeam: string = 'red';
  blueTeam: string = 'blue';

  redScore: number = 0;
  redScoreInitial: number = 0;
  redPlayers: string[] | null = [];

  blueScore: number = 0;
  blueScoreInitial: number = 0;
  bluePlayers: string[] | null = [];

  redSpymasterButtonDisabled: boolean = false;
  blueSpymasterButtonDisabled: boolean = false;

  constructor() {
    this.ws = io("http://192.168.1.229:5000", {
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      }
    });
  }

  ngOnInit() {
    this.ws.on("auth", (data: { "token": string, "username": string }) => {
      console.log("Received grantToken event:", data);

      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      this.name = data.username;
    });
    this.ws.on("updateGameData", (data: GameData) => {
      console.log("Received gamedata event:", data);
      this.mapGameData(data)
    });
    this.ws.on("restartedGameData", (data: GameData) => {
      this.handleRestartedGameData(data)
    });
    this.ws.on("playersUpdate", (event) => {
      this.handlePlayersUpdate(event)
    });
    this.ws.on("spymasterGameData", (data: GameData) => {
      this.handleSpymasterGameData(data)
    });
  }


  private mapGameData(data: GameData) {
    console.log("Received event:", data);

    this.redScoreInitial = data.red_initial_score;
    this.redScore = data.red_score;

    this.blueScoreInitial = data.blue_initial_score;
    this.blueScore = data.blue_score;

    this.gameData = data.codenames.map((codename: Codename) => ({
      word: codename.name,
      color: codename.state ? codename.color : "white",
      clicked: codename.state
    }));

  }

  handleSpymasterGameData(data: GameData) {
    console.log("Received event:", data);

    this.redScoreInitial = data.red_initial_score;
    this.redScore = data.red_score;

    this.blueScoreInitial = data.blue_initial_score;
    this.blueScore = data.blue_score;

    data.codenames.forEach((codename: Codename) => {
      const colorClass = codename.color;
      const tdElement = document.querySelector(`td[class="${codename.name}"]`);
      if (tdElement) {
        tdElement.classList.add(colorClass);
      }
    });

  }

  handlePlayersUpdate(event: Players) {
    this.redPlayers = event.red?.players ?? null;
    this.bluePlayers = event.blue?.players ?? null;

    this.redSpymaster = event.red?.spymaster?.join() ?? "Spymaster";
    this.blueSpymaster = event.blue?.spymaster?.join() ?? "Spymaster";


    this.redSpymasterButtonDisabled = this.redSpymaster !== "Spymaster";
    this.blueSpymasterButtonDisabled = this.blueSpymaster !== "Spymaster";
  }


  handleRestartedGameData(data: GameData) {
    this.mapGameData(data);

    this.redScore = 0;
    this.blueScore = 0;

    this.redSpymasterButtonDisabled = false;
    this.blueSpymasterButtonDisabled = false;

    const activeElements = document.querySelectorAll('span.word');
    activeElements.forEach(element => {
      element.classList.remove('active', 'blue', 'red', 'yellow', 'black');
    });
    const tdElements = document.querySelectorAll('td');

    tdElements.forEach(element => {
      element.classList.remove('blue', 'red', 'yellow', 'black');
    });

    const word = document.querySelector(`word`);
    if (word) {
      word.classList.remove('semi');
    }
    this.ws.emit('restarted');


  }


  updateName() {
    this.ws.emit("changeUsername", this.name)
  }


  toggleClass(event: any, word: any): void {
    if (word.clicked) {
      return
    }
    if (event.target.classList.contains('white')) {
      this.ws.emit('clickAction', word.word);
    }
    if (word.color === 'black') {
      this.ws.emit('endGame');
    }
  }

  becomeSpymaster(event: any, color: string) {
    this.ws.emit('joinSpymaster');
  }

  becomePlayer(event: any, team: string) {
    this.ws.emit('joinPlayers', team);
  }


  restartGame() {
    this.ws.emit('restartGame');
  }


  protected readonly Object = Object;
}
