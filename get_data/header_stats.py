import logging

from classes.utils import elo_to_int, get_region, get_mean_elo


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def show_elo_distribution(ax, games):
    """
    Show the distribution of ELOs in the games.
    """

    elo_distribution = [0 for i in range(-1, 31)]
    for game in games:
        for player in game.players:
            elo_distribution[elo_to_int(player.elo) + 1] += 1
    elo_distribution = [i / len(games) * 10 for i in elo_distribution]
    
    real_elo_distribution = [0, 0.48, 1.1, 2.6, 3.3, 7.4, 5.3, 4.6, 3.3, 7.5, 5, 4.1, 2.8,
                        8, 5, 4, 2.6, 7.1, 4, 3.1, 2, 6.2, 2.9, 1.7, 1.4, 1.2, 0.57, 
                        0.54, 0.44, 0.48, 0.044, 0.019]
    
    width = 0.35
    x = range(-1, 31)
    ax.bar([i - width / 2 for i in x], real_elo_distribution, width, label='Real distribution')
    ax.bar([i + width / 2 for i in x], elo_distribution, width, label='Observed distribution')
    ax.legend()

def show_champion_distribution(ax, games):
    """
    Show the distribution of champions in the games.
    """
    
    champion_distribution = {}

    for game in games:
        for player in game.players:
            if player.champion not in champion_distribution:
                champion_distribution[player.champion] = 0
            champion_distribution[player.champion] += 1

    champion_distribution = dict(sorted(list(champion_distribution.items()), key=lambda x: x[1], reverse=True))
    ax.bar(champion_distribution.keys(), champion_distribution.values(), label='Champion distribution')
    ax.legend()

def show_region_distribution(ax, games):
    """
    Show the distribution of regions in the games.
    """
    
    regions = {}
    for game in games:
        region = get_region(game)
        if region not in regions:
            regions[region] = 0
        regions[region] += 1
    regions = dict(sorted(list(regions.items()), key=lambda x: x[1], reverse=True))
    ax.bar(regions.keys(), regions.values(), label='Region distribution')
    ax.legend()

def show_duration_distribution(ax, games):
    """
    Show the distribution of durations in the games.
    """
    
    durations = [game.duration for game in games]
    ax.hist(durations, bins=100, label='Duration distribution')

    ax.set_xticks(range(0, 70*60, 60*5), range(0, 70, 5))
    ax.legend()

def get_average_elo(games):
    """
    Get the average ELO of the games.
    """
    
    elos = [get_mean_elo(game) for game in games]
    return sum(elos) / len(elos)

def get_average_duration(games):
    """
    Get the average duration of the games.
    """
    
    return sum([game.duration for game in games]) / len(games)

def get_maximum_duration(games):
    """
    Get the maximum duration of the games.
    """
    
    return max([game.duration for game in games])

def get_minimum_duration(games):
    """
    Get the minimum duration of the games.
    """
    
    return min([game.duration for game in games])