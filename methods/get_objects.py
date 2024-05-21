import logging

from classes.game import Game
import classes.importer as importer
from classes.time_frame import TimeFrame
from classes.utils import duration_to_int


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def get_game_infos(game_id):
    """
    Get the duration, date, winner and players of a game.
    """
    
    saved_games = importer.get_saved_games()

    for game in saved_games:
        if game['match_id'] == game_id:
            duration, date, winner, players = game['duration'], game['date'], game['winner'], game['players']

    p = {}

    for index, player in zip([0, 5, 1, 6, 2, 7, 3, 8, 4, 9], players):
        name = player['summoner'].split('#')[0]
        p[name] = index

    return duration, date, winner, p

def parse_game(game_id):
    """
    Parse a game json file and return a Game object.
    """
    
    game = Game()
    events = importer.get_done_game(game_id)

    game.game_id = game_id
    game.duration, game.date, game.winner, players = get_game_infos(game_id)
    game.duration = duration_to_int(game.duration)
    start_time = float([event for event in events if event['eventname'] == "OnNexusCrystalStart"][0]["timestamp"])*8 - 65

    for time_frame_id in range(game.duration//120 + 1):
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
            if source[0] == ' ':
                source = source[1:]

            target = players[source]
            time_frame.deaths[target//5][target%5] = True

        game.time_frames.append(time_frame)

    return game

def parse_all_games():
    """
    Parse all games that have been saved and not parsed yet.
    """
    
    done_games = importer.get_done_games()
    done_objects = importer.get_done_objects()

    for game_id in done_games:
        if game_id in done_objects:
            continue
        game = parse_game(game_id)
        log.info(f'Parsed game {str(game)}')
    
        importer.save_game_object(game)