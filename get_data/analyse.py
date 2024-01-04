import json
import re
from matplotlib import pyplot as plt
import random
import datetime


class Game:
    def __init__(self):
        self.match_id = None
        self.type = None
        self.duration = None
        self.date = None
        self.players = None

    def __repr__(self):
        return f'{self.match_id} - {self.type}'

class Player:
    def __init__(self):
        self.champion = None
        self.summoner = None
        self.elo = None

    def __repr__(self):
        return f'{self.champion} - {self.summoner} - {self.elo}'
    
def elo_to_int(str_elo):
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
    return game.match_id.split('/')[1]

def get_saved_games():
    with open ('saved_games.json', 'r') as f:
        data = json.load(f)
    return data

def convert_to_games(data):
    games = []
    for game in data:
        g = Game()
        g.match_id = game['match_id']
        g.type = game['type']
        g.duration = game['duration']
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

def show_elo_distribution(games):
    elo_distribution = {i: 0 for i in range(-1, 31)}
    for game in games:
        for player in game.players:
            elo_distribution[elo_to_int(player.elo)] += 1
    plt.bar(elo_distribution.keys(), elo_distribution.values())
    elo_distribution = [0, 0.48, 1.1, 2.6, 3.3, 7.4, 5.3, 4.6, 3.3, 7.5, 5, 4.1, 2.8,
                        8, 5, 4, 2.6, 7.1, 4, 3.1, 2, 6.2, 2.9, 1.7, 1.4, 1.2, 0.57, 
                        0.54, 0.44, 0.48, 0.044, 0.019]
    # plt.bar(range(-1, 31), elo_distribution)
    plt.show()

def show_champion_distribution(games):
    champion_distribution = {}
    for game in games:
        for player in game.players:
            if player.champion not in champion_distribution:
                champion_distribution[player.champion] = 0
            champion_distribution[player.champion] += 1
    champion_distribution = dict(sorted(list(champion_distribution.items()), key=lambda x: x[1], reverse=True))
    print(champion_distribution)
    plt.bar(champion_distribution.keys(), champion_distribution.values())
    plt.show()

def length_to_int(length):
    length = length.replace('(', '').replace(')', '').split(':')
    return int(length[0]) * 60 + int(length[1])

def take_random(games):
    print(len(games))
    games = [game for game in games if get_region(game) == 'euw']

    for game in games:
        elo = [elo_to_int(player.elo) for player in game.players]
        if -1 in elo:
            games.remove(game)
            continue
        if round(sum(elo) / len(elo)) != 28:
            games.remove(game)
            continue

    print(len(games))
    return random.choice(games)

def main():
    data = get_saved_games()
    games = convert_to_games(data)
    print(f'Total games: {len(games)}')

    total_elo = 0
    total_players = 0
    regions = {}
    for game in games:
        region = get_region(game)
        if region not in regions:
            regions[region] = 0
        regions[region] += 1
        for player in game.players:
            if elo_to_int(player.elo) != -1:
                total_elo += elo_to_int(player.elo)
                total_players += 1

    average_elo = total_elo / total_players
    print(f'Average elo: {average_elo:.2f} ({int_to_elo(int(average_elo))} - {int_to_elo(int(average_elo) + 1)})')
    region = dict(sorted(list(regions.items()), key=lambda x: x[1], reverse=True))
    print(f'Regions: {region}')

    average_length = sum([length_to_int(game.duration) for game in games]) / len(games)
    print(f'Average length: {int(average_length / 60)}:{int(average_length % 60)}')
    max_length = max([length_to_int(game.duration) for game in games])
    print(f'Max length: {int(max_length / 60)}:{int(max_length % 60)}')

    # show_champion_distribution(games)
    # show_elo_distribution(games)

    game = take_random(games)
    print(game.match_id)
    print(game.date)
    print(datetime.datetime.fromtimestamp(int(game.date[:-3])))

if __name__ == '__main__':
    main()