import json
import time
import logging

from classes.utils import take_random_valid
from get_data.liveevents import generate_json
from get_data.header_stats import get_saved_games, convert_to_games, get_region, get_mean_elo


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def get_done_games():
    with open('get_data/data/done.json', 'r') as file:
        return json.load(file)

def add_done_game(game_id):
    done_games = get_done_games()
    done_games.append(game_id)
    with open('get_data/data/done.json', 'w') as file:
        json.dump(done_games, file, indent=4)

def main():
    done_games = get_done_games()
    data = get_saved_games()
    games = convert_to_games(data)

    games = [game for game in games if game.game_id not in done_games]

    game = take_random_valid(games)
    print(f'Random Game: {game}')

    shortened_id = game.game_id[5:]

    generate_json(shortened_id, game.duration)

    add_done_game(game.game_id)

if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(15)
    except Exception as e:
        log.error(e)