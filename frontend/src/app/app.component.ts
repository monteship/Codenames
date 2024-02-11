import {Component, OnInit, Renderer2} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {CommonModule} from '@angular/common';

import {HttpClientModule} from '@angular/common/http';

@Component({
  standalone: true,
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [CommonModule, HttpClientModule]
})
export class AppComponent implements OnInit {
  gameData: any;

  constructor(private http: HttpClient, private renderer: Renderer2) {
  }

  ngOnInit() {
    this.getGameData();
  }

  getGameData() {
    this.http.get<any>('http://localhost:5000/')
      .subscribe((data: any[]) => {
        this.gameData = data.map((row: any[]) =>
          row.map((word: any) => {
            const key = Object.keys(word)[0];
            const color: string = String(Object.values(word)[0]);
            return {[key]: color, clicked: false};
          })
        );
      });
  }

  toggleClass(event: any, word: any): void {
    const color: string = String(Object.values(word)[0]); // Cast to string
    const hasClass = event.target.classList.contains('white');

    if (hasClass) {
      this.renderer.removeClass(event.target, 'white');
      this.renderer.addClass(event.target, color);
      this.renderer.addClass(event.target, 'active');
    }
  }


  restartGame() {
    this.http.post<any>('http://localhost:5000/restart', {})
      .subscribe(data => {
        this.gameData = data;
      });
  }

  protected readonly Object = Object;


}
