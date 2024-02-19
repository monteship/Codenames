import {Injectable} from '@angular/core';
import {io, Socket} from 'socket.io-client';
import {Observable} from 'rxjs';
import {GameData, Players} from './models';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private socket: Socket;

  constructor() {
    this.socket = io("http://192.168.1.229:5000", {
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      }
    });
  }

  connect(): void {
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });
  }

  onAuth(): Observable<{ token: string, username: string }> {
    return new Observable<{ token: string, username: string }>(observer => {
      this.socket.on('auth', (data: { token: string, username: string }) => {
        observer.next(data);
      });
    });
  }

  onGameDataUpdate(): Observable<GameData> {
    return new Observable<GameData>(observer => {
      this.socket.on('updateGameData', (data: GameData) => {
        observer.next(data);
      });
    });
  }


  onPlayersUpdate(): Observable<Players> {
    return new Observable<Players>(observer => {
      this.socket.on('playersUpdate', (data: Players) => {
        observer.next(data);
      });
    });
  }

  changeUsername(username: string | null): void {
    this.socket.emit('changeUsername', username);
  }

  clickAction(word: string): void {
    console.log('Clicked word ', word);
    this.socket.emit('clickAction', word);
  }

  endGame(): void {
    this.socket.emit('endGame');
  }

  joinSpymaster(): void {
    this.socket.emit('joinSpymaster');
  }

  joinPlayers(team: string): void {
    this.socket.emit('joinPlayers', team);
  }

  restartGame(): void {
    this.socket.emit('restartGame');
  }

}
