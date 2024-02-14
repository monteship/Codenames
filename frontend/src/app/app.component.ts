import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {io, Socket} from 'socket.io-client';
import {HttpClientModule} from '@angular/common/http';


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

  redTeam: string = 'red';
  redMembers: { name: string, role: string }[] = [];
  redSpymaster: { name: string, role: string }[] = [];

  blueTeam: string = 'blue';
  blueMembers: { name: string, role: string }[] = [];
  blueSpymaster: { name: string, role: string }[] = [];


  redScore: number = 0;
  redScoreInitial: number = 0;

  blueScore: number = 0;
  blueScoreInitial: number = 0;

  constructor() {
    this.ws = io('192.168.1.229:5000');
  }

  ngOnInit() {
    this.ws.on('updatedGameData', (data) => {
      console.log("Get updated from server")
      this.updateThisData(data);
      this.handleGameData(data["codenames"]);
    });

    this.ws.on('restartedGame', (data) => {
      this.updateThisData(data);
      this.handleRestartedGameData(data["codenames"]);
    });

    this.ws.on('clickedAction', (data) => {
      console.log('Received clicked event:', data);
      this.handleClickedAction(data);
    });

    this.ws.on('joinedTeam', (data) => {
      console.log('Received join event:', data);
      this.handleJoinedTeam(data);
    });
  }


  handleGameData(data: any) {
    if (Array.isArray(data)) {
      this.gameData = data.map((wordObject: any) => ({
        word: wordObject.word,
        color: !wordObject.clicked ? "white" : wordObject.color,
        clicked: wordObject.clicked
      }));
    }
  }

  updateThisData(data: any) {
    this.blueScoreInitial = data["initial_score_blue"];
    this.redScoreInitial = data["initial_score_red"];
    this.blueScore = data["score_blue"];
    this.redScore = data["score_red"];
    // this.redMembers = data["red_members"];
    // this.blueMembers = data["blue_members"];
  }

  handleRestartedGameData(data: any) {
    this.handleGameData(data);

    this.redMembers = [];
    this.redSpymaster = [];
    this.redScore = 0;

    this.blueMembers = [];
    this.blueSpymaster = [];
    this.blueScore = 0;
    const activeElements = document.querySelectorAll('.active');
    activeElements.forEach(element => {
      element.classList.remove('active', 'blue', 'red', 'yellow', 'black');
    });
  }


  handleClickedAction(data: any) {
    const word: string = data['word'];
    const color: string = data['color'];
    const element = this.gameData.find(item => item.word === word);

    if (data.color === this.redTeam) {
      this.redScore += 1;
    } else if (data.color === this.blueTeam) {
      this.blueScore += 1;
    }

    if (element) {
      element.clicked = true;
      const elementRef = document.getElementById(word);
      if (elementRef) {
        console.log('Updating element class');
        elementRef.classList.remove('white');
        elementRef.classList.add(color);
        elementRef.classList.add('active');
      }
    }
  }

  handleJoinedTeam(data: any) {
    const color: string = data['color'];
    const name: string = data["name"];

    if (color == this.redTeam) {

      this.redMembers.push({"name": name, 'role': "player"});

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

  joinTeam(event: any, team: string) {
    this.ws.emit('joinTeam', team);
  }

  restartGame() {
    this.ws.emit('restartGame');
  }


  protected readonly Object = Object;
}
