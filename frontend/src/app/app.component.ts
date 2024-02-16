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
  name: string;
  color: string;
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
  spymasterPlaceHolder: string = "Become spymaster"

  redTeam: string = 'red';
  redScore: number = 0;
  redScoreInitial: number = 0;
  redPlayers: [] = [];
  redSpymaster: string = "";

  blueTeam: string = 'blue';
  blueScore: number = 0;
  blueScoreInitial: number = 0;
  bluePlayers: [] = [];
  blueSpymaster: string = "";

  constructor() {
    this.ws = io("192.168.1.229:5000"
    );
  }

  ngOnInit() {
    this.ws.on("usersGameData", (data: GameData) => {
      this.mapGameData(data)
    });
    this.ws.on("spymasterGameData", (data: GameData) => {
      this.mapGameData(data, false)
    });
    this.ws.on("restartedGameData", (data: GameData) => {
      this.handleRestartedGameData(data)
    });
    this.ws.on("clickedAction", (data: ClickAction) => {
      this.handleClickedAction(data)
    });
    this.ws.on("spymasterAppeared", (data: Member) => {
      this.handleSpymasterAppeared(data)
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

  private mapGameData(data: GameData, isUsers: boolean = true) {
    console.log("Received event:", isUsers, data);

    this.updateThisData(data.score);

    if (Array.isArray(data.codenames)) {
      this.gameData = data.codenames.map((wordObject: any) => ({
        word: wordObject.word,
        color: !wordObject.clicked || !isUsers ? "white" : wordObject.color,
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

  handleSpymasterAppeared(member: Member) {
    if (member.color === 'red') {
      this.redSpymaster = member.name
      this.toggleSpymasterButton(member.color, 'true');
    } else {
      this.blueSpymaster = member.name;
      this.toggleSpymasterButton(member.color, 'true');
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


  restartGame() {
    this.ws.emit('restartGame');
  }


  protected readonly Object = Object;
}
