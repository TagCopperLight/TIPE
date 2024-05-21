import json
import pathlib

from classes.game import Game
from classes.player import Player
from classes.utils import duration_to_int

SAVED_GAMES_PATH = pathlib.Path('get_data/saved_games.json')


def get_saved_games():
    """
    Get the saved games from the saved_games.json file.
    """

    with open (SAVED_GAMES_PATH, 'r') as f:
        data = json.load(f)

    return data

def get_games():
    """
    Get the Game objects from the saved_games.json file.
    """

    data = get_saved_games()
    games = []
    for game in data:
        g = Game()
        g.match_id = game['match_id']
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