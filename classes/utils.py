import re
import tqdm
import random
import logging
from math import exp
from PIL import Image

from methods.get_tree import create_decision_tree_files, create_decision_tree


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def elo_to_int(str_elo):
    """
    Convert a string elo to an integer elo.
    """
    
    if str_elo == 'Unranked':
        return -1
    
    elif str_elo in ['Master', 'GrandMaster', 'Challenger']:
        return 7*4 + ['Master', 'GrandMaster', 'Challenger'].index(str_elo)
    
    else:
        elos = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Emerald', 'Diamond']
        numbers = ['I', 'II', 'III', 'IV']

        str_elo = re.findall(r"\w+", str_elo)
        elo, number = elos.index(str_elo[0]), numbers.index(str_elo[1])

        return 4 * elo + number
    
def int_to_elo(int_elo):
    """
    Convert an integer elo to a string elo.
    """
    
    if int_elo == -1:
        return 'Unranked'
    
    elif int_elo >= 28:
        return ['Master', 'GrandMaster', 'Challenger'][int((int_elo - 28) / 4)]
    
    else:
        elos = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Emerald', 'Diamond']
        elo = elos[int(int_elo / 4)]
        number = 4 - int_elo % 4

        return f'{elo} {number}'
    
def get_region(game):
    """
    Get the region of the game.
    """
    
    return game.game_id.split('/')[1]

def duration_to_int(length):
    """
    Convert a string duration to an integer duration.
    """
    
    length = length.replace('(', '').replace(')', '').split(':')
    return int(length[0]) * 60 + int(length[1])

def get_mean_elo(game):
    """
    Get the mean elo of the game.
    """
    
    elo = [elo_to_int(player.elo) for player in game.players]
    elo = [el for el in elo if el != -1]
    return sum(elo) / len(elo)

def show_interactions(interactions):
    """
    Show the interactions list in a grid.
    """
    
    for i in range(5):
        for j in range(5):
            log.info('⬛', end=' ') if interactions[i][j][0] else log.info('⬜', end=' ')
            log.info('⬛', end=' ') if interactions[i][j][1] else log.info('⬜', end=' ')
            log.info(' ', end='')
        log.info('')

def take_random_valid(games):
    """
    Take a random valid game from the list of games.
    """

    games = [game for game in games if get_region(game) == 'euw']
    games = [game for game in games if game.duration > 20*60]
    games = [game for game in games if round(get_mean_elo(game)) == 28]

    log.info(f'Valid games: {len(games)}')
    max_length = max([game.duration for game in games])
    log.info(f'Max length: {int(max_length / 60)}:{int(max_length % 60)}')
    
    return random.choice(games)

def accuracy_fix(features):
    """
    Return the fix of the accuracy for the number of features.
    """
    
    return 0.02 * exp(len(features)/2.85)

def chunk_split(a, n):
    """
    Split a list into n chunks.
    """
    
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def show_tree_stats(games, features):
    """
    Show the stats of the decision tree.
    """
    
    create_decision_tree_files(games, features)
    tree = create_decision_tree()
    acc = tree.get_accuracy()
    log.info(f'Fixed accuracy: {acc - accuracy_fix(features)}')
    log.info(f'Accuracy: {acc}')
    log.info(f'Features: {features}')
    log.info(f'Number of features: {len(features)}')
    log.info(f'3-fold cross validation: {tree.k_fold_cross_validation(3)}')
    log.info('')

def image_grid(imgs, rows, cols):
    """
    Create a grid of images.
    """

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid

def translate_features():
    """
    Translate a feature list returned by the genetic algorithm to a list of features, usable in python.
    """
    features = [
        
    ]

    for feature_list in features:
        log.info('[', end='')
        for feature in feature_list:
            log.info('(', end='')
            if feature[1] == 10:
                log.info(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
            else:
                log.info(f"'{feature[0]}', '{['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]}', {feature[2]}", end='')
            if feature != feature_list[-1]:
                log.info('), ', end='')
            else:
                log.info(')', end='')
        log.info('],')

def features_to_filename(features):
    """
    Convert a list of features to a filename.
    """
    
    features = [[feature[0][0], ['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5', 'DEATH'].index(feature[1]), feature[2]] for feature in features]

    return '_'.join([f'{feature[0]}-{feature[1]}-{feature[2]}' for feature in features])