import logging
import matplotlib.pyplot as plt

from classes.game import Game
import classes.importer as importer
from classes.utils import int_to_elo
from classes.time_frame import TimeFrame
import get_data.header_stats as hstats
from classes.get_graphs import save_graphs
from classes.get_objects import parse_all_games


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

def main():
    # header_stats()
    # get_objects()
    # get_graphs()
    pass

if __name__ == "__main__":
    main()