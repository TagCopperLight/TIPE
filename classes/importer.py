import json
import pickle
import pathlib

from classes.game import Game
from classes.player import Player
from classes.utils import duration_to_int

BATCH_DATA_PATH = pathlib.Path('get_data/games/batch_data.json')
SAVED_GAMES_PATH = pathlib.Path('get_data/saved_games.json')
DONE_OBJECTS_PATH = pathlib.Path('game_objects/done.json')
DONE_GAMES_FOLDER = pathlib.Path('get_data/data')


def write_batch_data(file):
    with open(BATCH_DATA_PATH, 'r') as f:
        batch_data = json.load(f)
        
    batch_data.append({'id': file[2], 'arg1': file[4], 'arg2': file[3], 'arg3': file[2], 'arg4': file[1]})

    with open(BATCH_DATA_PATH, 'w') as f:
        json.dump(batch_data, f, indent=4)


def get_saved_games():
    """
    Get the saved games from the saved_games.json file.
    """

    with open (SAVED_GAMES_PATH, 'r') as f:
        data = json.load(f)

    return data

def write_saved_games(data):
    """
    Write the saved games to the saved_games.json file.
    """

    with open(SAVED_GAMES_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def get_games():
    """
    Get the Game objects from the saved_games.json file.
    """

    data = get_saved_games()
    games = []
    for game in data:
        g = Game()
        g.game_id = game['match_id']
        g.type = game['type']
        g.duration = game['duration']
        g.duration = duration_to_int(g.duration)
        g.date = game['date']
        g.players = []
        for player in game['players']:
            p = Player()
            p.champion = player['champion']
            p.summoner = player['summoner']
            p.elo = player['elo']
            g.players.append(p)
        games.append(g)
    return games

def get_done_objects():
    """
    Get the done game objects from the done.json file.
    """

    with open(DONE_OBJECTS_PATH, 'r') as file:
        return json.load(file)
    
def add_done_object(game_id):
    """
    Add a game object to the done.json file.
    """

    done_objects = get_done_objects()
    done_objects.append(game_id)
    with open(DONE_OBJECTS_PATH, 'w') as file:
        json.dump(done_objects, file, indent=4)

def save_game_object(game):
    """
    Save a game object to a .pkl file.
    """

    add_done_object(game.game_id)
    object_path = pathlib.Path(f'game_objects/{game.game_id[5:]}.pkl')
    with open(object_path, 'wb') as file:
        pickle.dump(game, file)

def get_done_games():
    """
    Get the done games from the done.json file.
    """
    
    with open(DONE_GAMES_FOLDER / 'done.json', 'r') as file:
        return json.load(file)
    
def get_done_game(game_id):
    """
    Get a done game file.
    """

    with open(DONE_GAMES_FOLDER / f'{game_id[5:]}.json', 'r') as file:
        return json.load(file)
    