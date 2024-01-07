import json
import pathlib
import pickle

from get_data.get_stats import length_to_int


class TimeFrame:
    def __init__(self, length):
        self.length = length
        self.interactions = [[[False, False] for _ in range(5)] for _ in range(5)]
        self.deaths = [[False for _ in range(5)] for _ in range(2)]


class Game:
    def __init__(self):
        self.game_id = None
        self.duration = None
        self.date = None
        self.winner = None

        self.time_frames = []

    def __repr__(self):
        return f'Game(game_id={self.game_id}, duration={self.duration}, date={self.date}, winner={self.winner})'


def get_saved_games():
    saved_games_path = 'get_data/saved_games.json'
    with open(saved_games_path, 'r') as file:
        return json.load(file)

def get_game_objects():
    done_objects_path = pathlib.Path('game_objects/done.json')
    with open(done_objects_path, 'r') as file:
        return json.load(file)

def save_game_object(game):
    done_objects = get_game_objects()
    done_objects.append(game.game_id)
    done_objects_path = pathlib.Path('game_objects/done.json')
    with open(done_objects_path, 'w') as file:
        json.dump(done_objects, file, indent=4)

    object_path = pathlib.Path(f'game_objects/{game.game_id[5:]}.pkl')
    with open(object_path, 'wb') as file:
        pickle.dump(game, file)

def get_game_infos(game_id):
    saved_games = get_saved_games()

    for game in saved_games:
        if game['match_id'] == game_id:
            duration, date, winner, players = game['duration'], game['date'], game['winner'], game['players']

    p = {}

    for index, player in zip([0, 5, 1, 6, 2, 7, 3, 8, 4, 9], players):
        name = player['summoner'].split('#')[0]
        p[name] = index

    return duration, date, winner, p       

def get_done_games():
    done_path = 'get_data/data/done.json'
    with open(done_path, 'r') as file:
        return json.load(file)

def show_interactions(interactions):
    for i in range(5):
        for j in range(5):
            print('⬛', end=' ') if interactions[i][j][0] else print('⬜', end=' ')
            print('⬛', end=' ') if interactions[i][j][1] else print('⬜', end=' ')
            print(' ', end='')
        print()

def parse_game(game_id):
    game_data_path = f'get_data/data/{game_id[5:]}.json'
    with open(game_data_path, 'r') as file:
        events = json.load(file)
    
    game = Game()

    game.game_id = game_id
    game.duration, game.date, game.winner, players = get_game_infos(game_id)
    duration = length_to_int(game.duration)
    start_time = float([event for event in events if event['eventname'] == "OnNexusCrystalStart"][0]["timestamp"])*8 - 65

    for time_frame_id in range(duration//120 + 1):
        events_in_time_frame = [event for event in events if float(event['timestamp'])*8 - start_time >= time_frame_id*120]
        events_in_time_frame = [event for event in events_in_time_frame if float(event['timestamp'])*8 - start_time < (time_frame_id+1)*120]
        time_frame = TimeFrame(120)

        for event in events_in_time_frame:
            if event['eventname'] != "OnDamageGiven":
                continue
            if 'other' not in event.keys():
                continue
            if event['other'] not in players or event['source'] not in players:
                continue
            if event['other'] == event['source']:
                continue
            
            target = players[event['other']]
            target_team = target//5
            target = target%5
            source = players[event['source']]%5


            if target_team == 0:
                time_frame.interactions[target][source][0] = True
            else:
                time_frame.interactions[source][target][1] = True

        deaths = [event for event in events_in_time_frame if event['eventname'] == "OnChampionDie"]
        
        for death in deaths:
            source = death['source'] # Sometimes, there's a space at the end of the name
            if source[-1] == ' ':
                source = source[:-1]

            target = players[source]
            time_frame.deaths[target//5][target%5] = True

        game.time_frames.append(time_frame)


    return game

def main():
    done_games = get_done_games()
    done_objects = get_game_objects()

    for game_id in done_games:
        if game_id in done_objects:
            continue
        game = parse_game(game_id)
        print(game)
    
        save_game_object(game)

if __name__ == '__main__':
    main()