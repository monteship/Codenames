import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {GameData, Codename} from './models';
import {GameService} from './game.service';


@Component({
  standalone: true,
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [CommonModule, HttpClientModule,
    FormsModule]
})

export class AppComponent implements OnInit {
  name: string | null = localStorage.getItem('username');
  redTeam: string = 'red';
  blueTeam: string = 'blue';

  redSpymaster: string = "Spymaster";
  blueSpymaster: string = "Spymaster";
  redPlayers: string[] | null = [];
  bluePlayers: string[] | null = [];

  redSpymasterButtonDisabled: boolean = false;
  blueSpymasterButtonDisabled: boolean = false;

  gameData: GameData | null = null;

  constructor(private gameService: GameService) {

  }

  ngOnInit() {
    this.gameService.connect();
    this.gameService.onAuth().subscribe(data => {
      localStorage.setItem('token', data.token);
      localStorage.setItem('username', data.username);
      this.name = data.username;
    });
    this.gameService.onGameDataUpdate().subscribe(data => {
      this.gameData = data
    });
    this.gameService.onPlayersUpdate().subscribe(players => {
      this.redPlayers = players.red?.players ?? null;
      this.bluePlayers = players.blue?.players ?? null;

      this.redSpymaster = players.red?.spymaster?.join() ?? "Spymaster";
      this.blueSpymaster = players.blue?.spymaster?.join() ?? "Spymaster";

      this.redSpymasterButtonDisabled = this.redSpymaster !== "Spymaster";
      this.blueSpymasterButtonDisabled = this.blueSpymaster !== "Spymaster";
    });
  }


  spymasterReveal() {
    return this.name == this.redSpymaster || this.name === this.blueSpymaster;

  }

  updateName() {
    this.gameService.changeUsername(this.name);
  }

  toggleClass(codename: Codename): void {
    console.log('Toggle ', codename.name);
    if (!codename.state && codename.color === 'black') {
      this.gameService.endGame();
    }
    if (!codename.state) {
      this.gameService.clickAction(codename.name);
    }
  }

  becomeSpymaster() {
    this.gameService.joinSpymaster();
  }

  becomePlayer(team: string) {
    this.gameService.joinPlayers(team);
  }

  restartGame() {
    this.gameService.restartGame();
  }
}
