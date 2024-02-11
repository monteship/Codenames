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

  constructor(private http: HttpClient, private renderer: Renderer2) {
    this.ws = io('http://localhost:5000');
  }

  ngOnInit() {
    this.ws.on('connect', () => {
      console.log('WebSocket connection established');
      this.ws.emit('getGameData');
    });

    this.ws.on('gameData', (data) => {
      console.log("Get gameData from server")
      this.handleGameData(data);
    });

    this.ws.on('updateRender', (data) => {
      console.log('Received updateRender event:', data);
      this.handleUpdateRender(data);
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


  toggleClass(event: any, word: any): void {
    const hasClass = event.target.classList.contains('white');

    if (hasClass) {
      this.ws.emit('clicked', word.word);
    }
  }

  restartGame() {
    this.ws.emit('restart'); // Emit restart event
  }


  protected readonly Object = Object;
}
