import json
import enum
import random
import logging

from get_data.liveevents import generate_json
from get_data.analyse import get_saved_games, convert_to_games, get_region, get_mean_elo


log = logging.getLogger('main')
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def get_done_games():
    with open('get_data/data/done.json', 'r') as file:
        return json.load(file)

def add_done_game(game_id):
    done_games = get_done_games()
    done_games.append(game_id)
    with open('get_data/data/done.json', 'w') as file:
        json.dump(done_games, file, indent=4)


class Vocabulary(enum.Enum):
    TOP = 0
    JUNGLE = 1
    MID = 2
    ADC = 3
    SUPPORT = 4
    RED = 0
    BLUE = 1


class TimeFrame:
    def __init__(self, length):
        self.length = length
        self.interactions = [[(False, False) for _ in range(5)] for _ in range(5)]
        self.deaths = [[False for _ in range(5)] for _ in range(2)]


class Game:
    def __init__(self):
        self.id = None
        self.game_id = None
        self.duration = None
        self.date = None
        self.winner = None

        self.time_frames = []

    def __repr__(self):
        return f'Game(id={self.id}, game_id={self.game_id}, duration={self.duration}, date={self.date}, winner={self.winner})'


def main():
    done_games = get_done_games()
    data = get_saved_games()
    games = convert_to_games(data)

    print(f'Total games: {len(games)}')
    print(f'EUW games: {len([game for game in games if get_region(game) == "euw"])}')

    games = [game for game in games if get_region(game) == 'euw']
    games = [game for game in games if game.duration > 20*60]
    games = [game for game in games if round(get_mean_elo(game)) == 28]
    games = [game for game in games if game.match_id not in done_games]

    print(f'Valid games: {len(games)}')

    game = random.choice(games)
    print(f'Random Game: {game}')

    shortened_id = game.match_id[5:]

    generate_json(shortened_id, game.duration)

    add_done_game(game.match_id)

if __name__ == '__main__':
    main()