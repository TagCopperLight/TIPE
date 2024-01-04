import csv
import json


class Game:
    def __init__(self):
        self.id = None
        self.game_id = None
        self.duration = None
        self.date = None
        self.winner = None

        self.time_frames = []
        self.deaths_frames = []

    def __repr__(self):
        return f'Game(id={self.id}, game_id={self.game_id}, duration={self.duration}, date={self.date}, winner={self.winner})'

def get_all_data():
    with open('stats.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        return data
    
def parse_data(data):
    games = []

    while len(data) > 0:
        game = Game()

        game.id = data[1][1]
        game.game_id = data[1][3]
        if game.game_id == '':
            game.game_id = None
        data = data[2:]

        game.time_frames = [[[[] for i in range(5)] for i in range(5)] for i in range(30)]
        game.deaths_frames = [[[] for i in range(10)] for i in range(30)]

        start_pos = 5
        for i in range(5):
            for time in range(30):
                for j in range(5):
                    game.time_frames[time][i][j] = (data[0][start_pos + 2*j], data[0][start_pos + 2*j + 1])
                game.deaths_frames[time][i] = data[0][start_pos + 10]
                start_pos += 12
            data = data[1:]
            start_pos = 5
        
        start_pos = 5
        for time in range(30):
            for j in range(5):
                game.deaths_frames[time][j+5] = data[0][start_pos + 2*j]
            start_pos += 12
        
        data = data[1:]

        games.append(game)

    return games

def add_data_from_games(games):
    new_games = []
    with open(r'get_data\\saved_games.json', 'r') as file:
        saved_games = json.load(file)
    
    for game in games:
        if game.game_id is None:
            continue
        for saved_game in saved_games:
            if game.game_id in saved_game['match_id']:
                game.duration = saved_game['duration']
                game.date = saved_game['date']
                # game.winner = saved_game['winner']

                new_games.append(game)
                break
    
    return new_games

if __name__ == '__main__':
    data = get_all_data()
    games = parse_data(data)
    games = add_data_from_games(games)
    print(games)