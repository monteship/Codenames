import {Component, OnInit, Renderer2} from '@angular/core';
import {HttpClient} from '@angular/common/http';
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
  gameData: any[] = [];
  ws: Socket;
  redTeam: string = 'RED';
  blueTeam: string = 'BLUE';
  redMembers: any[] = [];
  blueMembers: any[] = [];
  redScore: number = 0;
  blueScore: number = 0;

  constructor(private http: HttpClient, private renderer: Renderer2) {
    this.ws = io('192.168.1.229:5000');
  }

  ngOnInit() {
    this.ws.on('connect', () => {
      console.log('WebSocket connection established');
      this.ws.emit('update');
    });


    this.ws.on('updated', (data) => {
      console.log("Get updated from server")
      this.handleGameData(data);
    });

    this.ws.on('restarted', (data) => {
      console.log("Get restarted from server")
      this.handleRestartedGameData(data);
    });

    this.ws.on('clickedAction', (data) => {
      console.log('Received clicked event:', data);
      this.handleUpdateRender(data);
    });

    this.ws.on('joinTeam', (user) => {
      if (user.team === this.redTeam) {
        this.redMembers.push(user.member);
      } else {
        this.blueMembers.push(user.member);
      }
    });

    this.ws.on('updateScore', (data) => {
      this.handleUpdateScore(data)
    });
    this.ws.on('gameEnded', () => {
      this.handleGameEnd()
    });
  }

  handleUpdateScore(data: any) {
    if (data.color === this.redTeam) {
      this.redScore += 1;
    } else if (data.color === this.blueTeam) {
      this.blueScore += 1;
    }
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

  handleRestartedGameData(data: any) {
    if (Array.isArray(data)) {
      this.gameData = data.map((wordObject: any) => ({
        word: wordObject.word,
        color: "white",
        clicked: wordObject.clicked
      }));
    }
    this.gameData = [...this.gameData];
    this.redMembers = [];
    this.blueMembers = [];
    this.redScore = 0;
    this.blueScore = 0;
  }

  handleUpdateRender(data: any) {
    const word: string = data['data']['word'];
    const color: string = data['data']['color'];
    const element = this.gameData.find(item => item.word === word);


    if (element) {
      element.clicked = true;
      const elementRef = document.getElementById(word);
      console.log('Element reference:', elementRef);

      if (elementRef) {
        console.log('Updating element class');
        elementRef.classList.remove('white');
        elementRef.classList.add(color);
        elementRef.classList.add('active');
      }
    }
  }

  handleGameEnd() {

  }

  toggleClass(event: any, word: any): void {
    if (word.clicked) {
      return
    }
    if (event.target.classList.contains('white')) {
      this.ws.emit('clickAction', word.word);
      this.handleUpdateScore(word);
    }
    if (word.color === 'black') {
      this.ws.emit('endGame');
    }
  }

  restartGame() {
    this.ws.emit('restart');
  }


  protected readonly Object = Object;
}
