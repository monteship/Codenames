import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {io, Socket} from 'socket.io-client';
import {HttpClientModule} from '@angular/common/http';

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

interface Member {
  username: string;
  color: string;
  role: string;
}

interface GameData {
  score: Score;
  codenames: any[];
  spymasters: any[];
}

interface ClickAction {
  word: string;
  color: string;
}

@Component({
  standalone: true,
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [CommonModule, HttpClientModule]
})

export class AppComponent implements OnInit {
  ws: Socket;
  gameData: any[] = [];
  name: string | undefined;
  spymasterPlaceHolder: string = "Become spymaster"

  redTeam: string = 'red';
  redScore: number = 0;
  redScoreInitial: number = 0;
  redPlayers: string[] = [];
  redSpymaster: string = "";

  blueTeam: string = 'blue';
  blueScore: number = 0;
  blueScoreInitial: number = 0;
  bluePlayers: string[] = [];
  blueSpymaster: string = "";

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
    this.ws.on("grantToken", (data: { token: string, name: string }) => {
      localStorage.setItem('token', data["token"])
      this.name = data["name"];
    });
    this.ws.on("updateGameData", (data: GameData) => {
      this.mapGameData(data)
    });
    this.ws.on("restartedGameData", (data: GameData) => {
      this.handleRestartedGameData(data)
    });
    this.ws.on("clickedAction", (data: ClickAction) => {
      this.handleClickedAction(data)
    });
    this.ws.on("newPlayer", (data: Member) => {
      this.handleNewPlayer(data)
    });
    this.ws.on("newSpymaster", (data: Member) => {
      this.handleNewSpymaster(data)
    });
    this.ws.on("spymasterVision", (data: GameData) => {
      this.handleSpymasterVision(data)
    });
  }


  updateThisData(score: Score) {
    this.redScoreInitial = score.initial_score_red;
    this.redScore = score.score_red;
    this.redSpymaster = score.spymaster_red;
    this.redPlayers = score.players_red;

    this.blueScoreInitial = score.initial_score_blue;
    this.blueScore = score.score_blue;
    this.blueSpymaster = score.spymaster_blue;
    this.bluePlayers = score.players_blue;
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

  handleRestartedGameData(data: GameData) {
    this.mapGameData(data);

    this.redScore = 0;
    this.redSpymaster = this.spymasterPlaceHolder;
    this.blueSpymaster = this.spymasterPlaceHolder;
    this.blueScore = 0;

    const activeElements = document.querySelectorAll('.active');
    activeElements.forEach(element => {
      element.classList.remove('active', 'blue', 'red', 'yellow', 'black');
    });

    const word = document.querySelector(`word`);
    if (word) {
      word.classList.remove('semi');
    }
  }

  handleClickedAction(click: ClickAction) {
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
    for (const team of ["red", "blue"]) {
      this.toggleSpymasterButton(team, 'false');
    }
  }

  handleSpymasterVision(data: GameData) {
    console.log("Received event:", data);

    this.updateThisData(data.score);

    if (Array.isArray(data.codenames)) {
      this.gameData = data.codenames.map((wordObject: any) => ({
        word: wordObject.word,
        color: !wordObject.clicked ? "semi " + wordObject.color : wordObject.color,
        clicked: wordObject.clicked
      }));
    }
    const word = document.querySelector(`word`);
    if (word) {
      word.classList.add('semi');
    }
  }


  handleNewSpymaster(member: Member) {
    if (member.color === 'red') {
      const index = this.redPlayers.indexOf(member.username);
      if (index !== -1) {
        this.redPlayers.splice(index, 1);
      }
      this.redSpymaster = member.username;
    } else {
      const index = this.bluePlayers.indexOf(member.username);
      if (index !== -1) {
        this.redPlayers.splice(index, 1);
      }
      this.blueSpymaster = member.username;
    }

    this.toggleSpymasterButton(member.color, 'true');
  }

  handleNewPlayer(member: Member) {
    if (member.color === 'red') {
      this.redPlayers.push(member.username);
    } else {
      this.bluePlayers.push(member.username);
    }
  }

  toggleSpymasterButton(team: string, state: string) {
    const button = document.querySelector(`button.spymaster.${team}`);
    if (button) {
      button.setAttribute('disabled', state);
    }
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

  becomeSpymaster(event: any, team: string) {
    this.ws.emit('becomeSpymaster', team);
  }

  becomePlayer(event: any, team: string) {
    this.ws.emit('becomePlayer', team);
  }


  restartGame() {
    this.ws.emit('restartGame');
  }


  protected readonly Object = Object;
}
