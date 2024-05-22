import time
import logging
import matplotlib.pyplot as plt

from classes.game import Game
import classes.importer as importer
from classes.utils import int_to_elo
import get_data.header_stats as hstats
from classes.time_frame import TimeFrame
from methods.get_graphs import save_graphs
from classes.utils import features_to_filename
from methods.get_objects import parse_all_games
from methods.train_features import train_features
from methods.get_FSM_images import construct_fs_from_corpus, construct_fs_from_rule

TRAINED_FEATURES = [
    [('indeg', 'T1-R2', 8), ('cls', 'T1-R1', 5), ('btw', 'T1-R4', 9), ('eige', 'T2-R1', 3), ('eige', 'T2-R2', 7)],
    [('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
    [('btw', 'T2-R1', 13), ('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
    [('indeg', 'T1-R5', 12), ('cls', 'T1-R4', 9), ('cls', 'T2-R4', 11), ('btw', 'T2-R1', 14), ('btw', 'T1-R2', 7), ('eige', 'T2-R1', 9), ('eige', 'T1-R3', 5)],
    [('cls', 'T2-R1', 10), ('btw', 'T2-R4', 10), ('btw', 'T2-R5', 9), ('eige', 'T2-R1', 6), ('eige', 'T1-R2', 11), ('eige', 'DEATH', 9)],
    [('indeg', 'T2-R1', 8), ('outdeg', 'T1-R5', 11), ('btw', 'T1-R5', 14), ('eige', 'T2-R1', 2)],
    [('cls', 'T2-R1', 12), ('eige', 'T1-R1', 10), ('eige', 'T1-R4', 7), ('eige', 'T2-R5', 14), ('eige', 'DEATH', 6)],
    [('outdeg', 'T2-R1', 5), ('outdeg', 'T1-R2', 10), ('cls', 'T2-R1', 5), ('cls', 'T2-R2', 3), ('cls', 'T1-R3', 13)],
    [('outdeg', 'T1-R4', 12), ('outdeg', 'T1-R5', 7), ('cls', 'T2-R4', 11), ('btw', 'T1-R4', 13), ('btw', 'T2-R2', 6), ('eige', 'T1-R5', 5)],
    [('outdeg', 'T1-R1', 12), ('outdeg', 'T1-R5', 11), ('cls', 'T2-R4', 2), ('btw', 'T2-R5', 8), ('eige', 'DEATH', 9)],
    [('outdeg', 'T1-R1', 12), ('btw', 'T1-R5', 7), ('btw', 'T2-R4', 5), ('eige', 'T1-R4', 9), ('eige', 'T1-R5', 8), ('eige', 'T2-R5', 1)],
    [('outdeg', 'T1-R2', 5), ('btw', 'T1-R2', 11), ('eige', 'T1-R1', 0), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 7), ('eige', 'T2-R1', 12)],
    [('outdeg', 'T1-R5', 11), ('outdeg', 'T1-R5', 14), ('btw', 'T1-R5', 14), ('btw', 'T2-R1', 8), ('eige', 'T1-R1', 11)],
    [('indeg', 'DEATH', 10), ('cls', 'T1-R4', 8), ('btw', 'T1-R5', 7), ('eige', 'T1-R5', 0), ('eige', 'T1-R5', 5)]
]


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def header_stats():
    log.info('Header stats')
    log.info()
    games = importer.get_games()
    log.info(f'Total games: {len(games)}')
    avg_elo = hstats.get_average_elo(games)
    log.info(f'Average elo: {avg_elo:.2f} ({int_to_elo(int(avg_elo))} - {int_to_elo(int(avg_elo) + 1)})')
    log.info(f'Average duration: {int(hstats.get_average_duration(games) / 60)}:{int(hstats.get_average_duration(games) % 60)}')
    log.info(f'Maximum duration: {int(hstats.get_maximum_duration(games) / 60)}:{int(hstats.get_maximum_duration(games) % 60)}')
    log.info(f'Minimum duration: {int(hstats.get_minimum_duration(games) / 60)}:{int(hstats.get_minimum_duration(games) % 60)}')

    _, axs = plt.subplots(2, 2)
    hstats.show_elo_distribution(axs[0, 0], games)
    hstats.show_champion_distribution(axs[0, 1], games)
    hstats.show_region_distribution(axs[1, 0], games)
    hstats.show_duration_distribution(axs[1, 1], games)

    plt.show()

def get_objects():
    log.info('Parsing games...')
    parse_all_games()

def get_graphs():
    log.info('Getting graphs...')
    games = importer.get_done_game_objects()
    save_graphs(games)

def train():
    log.info('Training features...')

    games = importer.get_done_game_objects()
    features = [['indeg', 'outdeg', 'cls', 'btw', 'eige'], list(range(11)), list(range(30))]

    t0 = time.perf_counter()
    m, a, t = train_features(games, 1000, 2, features, 0.8, 0.8, 0.0005)
    log.info(f'Training time: {time.perf_counter() - t0:.2f}s')

    return m, a, t

def train_stats(maxes, avgs, true_maxes):
    plt.plot(maxes, label='Max')
    plt.plot(avgs, label='Avg')
    plt.plot(true_maxes, label='True Max')

    plt.legend()

    plt.show()

def main():
    # header_stats()
    # get_objects()
    # get_graphs()

    train_stats(*train())
    
    # for features in TRAINED_FEATURES:
    #     construct_fs_from_rule(importer.get_done_game_objects(), features, features_to_filename(features))

    # construct_fs_from_corpus(importer.get_done_game_objects(), TRAINED_FEATURES)
    # construct_fs_from_corpus(importer.get_done_game_objects(), TRAINED_FEATURES, winner='T1')

if __name__ == "__main__":
    main()