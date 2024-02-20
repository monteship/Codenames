export interface Codename {
  name: string;
  color: string;
  state: boolean;
}

export interface GameData {
  red_initial_score: number;
  blue_initial_score: number;
  red_score: number;
  blue_score: number;
  codenames: Codename[];
}

export interface Team {
  players: string[];
  spymaster: string;
}

export interface Players {
  red: Team;
  blue: Team;
  grey: Team;
}

