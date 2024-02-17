import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {io, Socket} from 'socket.io-client';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';

interface Score {
  initial_score_red: number;
  score_red: number;
  spymaster_red: string;
  players_red: [];
  initial_score_blue: number;
  score_blue: number;
  spymaster_blue: string;
  players_blue: [];
}


interface GameData {
  score: Score;
  codenames: any[];
  spymasters: any[];
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
  redPlayers: string[] = [];

  blueScore: number = 0;
  blueScoreInitial: number = 0;
  bluePlayers: string[] = [];

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
      this.mapGameData(data)
    });
    this.ws.on("restartedGameData", (data: GameData) => {
      this.handleRestartedGameData(data)
    });
    this.ws.on("clickedAction", (event) => {
      this.handleClickedAction(event)
    });
    this.ws.on("playersUpdate", (event) => {
      this.handlePlayersUpdate(event)
    });
    this.ws.on("spymasterGameData", (data: GameData) => {
      this.handleSpymasterGameData(data)
    });
  }


  updateThisData(score: Score) {
    this.redScoreInitial = score.initial_score_red;
    this.redScore = score.score_red;

    this.blueScoreInitial = score.initial_score_blue;
    this.blueScore = score.score_blue;
  }

  private mapGameData(data: GameData) {
    console.log("Received event:", data);

    this.updateThisData(data.score);

    if (Array.isArray(data.codenames)) {
      this.gameData = data.codenames.map((wordObject: any) => ({
        word: wordObject.word,
        color: !wordObject.clicked ? "white" : wordObject.color,
        clicked: wordObject.clicked
      }));
    }
  }

  toggleSpymasterButton(team: string, state: string) {
    const button = document.querySelector(`button.spymaster.${team}`);
    if (button) {
      button.setAttribute('disabled', state);
    }
  }

  handleRestartedGameData(data: GameData) {
    this.mapGameData(data);

    this.redScore = 0;
    this.blueScore = 0;

    this.redSpymasterButtonDisabled = false;
    this.blueSpymasterButtonDisabled = false;

    const activeElements = document.querySelectorAll('.active');
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

    for (const team of ["red", "blue"]) {
      this.toggleSpymasterButton(team, 'false')
    }
  }

  handleClickedAction(click: { "word": string, "color": string }) {
    const element = this.gameData.find(item => item.word === click.word);

    if (click.color === this.redTeam) {
      this.redScore += 1;
    } else if (click.color === this.blueTeam) {
      this.blueScore += 1;
    }

    if (element) {
      element.clicked = true;
      const elementRef = document.getElementById(click.word);
      if (elementRef) {
        console.log('Updating element class');
        elementRef.classList.remove('white');
        elementRef.classList.add(click.color);
        elementRef.classList.add('active');
      }
    }


  }

  handleSpymasterGameData(data: GameData) {
    console.log("Received event:", data);

    this.updateThisData(data.score);

    if (Array.isArray(data.codenames)) {
      data.codenames.forEach((wordObject: any) => {
        const colorClass = wordObject.color;
        const tdElement = document.querySelector(`td[class="${wordObject.word}"]`);
        if (tdElement) {
          tdElement.classList.add(colorClass);
        }
      });
    }
  }

  updateName() {
    this.ws.emit("changeUsername", this.name)
  }

  handlePlayersUpdate(event: {
    "red": { "players": string[], "spymaster": string[] },
    "blue": { "players": string[], "spymaster": string[] },
    "grey": { "players": string[] }
  }) {
    this.redPlayers = event.red.players;
    this.bluePlayers = event.blue.players;

    this.redSpymaster = event.red.spymaster.join();
    this.blueSpymaster = event.blue.spymaster.join();
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
    this.toggleSpymasterButton(color, 'false')
  }

  becomePlayer(event: any, team: string) {
    this.ws.emit('joinPlayers', team);
  }


  restartGame() {
    this.ws.emit('restartGame');
  }


  protected readonly Object = Object;
}
