import enum
import json


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


def get_done_games():
    with open('get_data/data/done.json', 'r') as file:
        return json.load(file)

def main():
    done_games = get_done_games()
    
    print(len(done_games))
    print(done_games)