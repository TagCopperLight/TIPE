import re
import tqdm
import random
import logging
from PIL import Image
import networkx as nx
from itertools import combinations


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
            print('⬛', end=' ') if interactions[i][j][0] else print('⬜', end=' ')
            print('⬛', end=' ') if interactions[i][j][1] else print('⬜', end=' ')
            print(' ', end='')
        print()

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

def translate_features():
    features = [
    ]

    for feature_list in features:
        print('[', end='')
        for feature in feature_list:
            print('(', end='')
            if feature[1] == 10:
                print(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
            else:
                print(f"'{feature[0]}', '{['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]}', {feature[2]}", end='')
            if feature != feature_list[-1]:
                print('), ', end='')
            else:
                print(')', end='')
        print('],')

def hash_graph(graph: nx.DiGraph) -> int:
    nodes = ['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5', 'DEATH']
    hash = 0

    for node in nodes:
        if node in graph.nodes:
            hash = (hash << 1) | 1
        hash = hash << 1

    for node1 in nodes:
        for node2 in nodes:
            if graph.has_edge(node1, node2):
                hash = (hash << 1) | 1
            hash = hash << 1
    
    return hash

class GraphCounter(dict):
    def __init__(self):
        super().__init__()

    def update(self, graphs):
        for graph in graphs:
            hashe = hash_graph(graph)
            if hashe in self:
                self[hashe][0] += 1
            else:
                self[hashe] = [1, graph]

def FSM(args):
    graphs, min_support, condition_nodes = args
    
    frequent_subgraph = nx.DiGraph()
    if not condition_nodes:
        return frequent_subgraph
    
    def find_subgraphs(graph, min_size=1, max_size=None):
        if max_size is None:
            max_size = len(graph.nodes)
        subgraphs = []
        for size in range(min_size, max_size + 1):
            for nodes in combinations(graph.nodes, size):
                subgraph = graph.subgraph(nodes)
                if all([node[0] in subgraph.nodes for node in condition_nodes]) and condition_nodes:
                    if nx.is_weakly_connected(subgraph):
                        subgraphs.append(subgraph)
        return subgraphs

    counter = GraphCounter()

    for graph in tqdm.tqdm(graphs, dynamic_ncols=True):
        subgraphs = find_subgraphs(graph, min_size=1)

        counter.update(subgraphs)

    for _, (support, subgraph) in counter.items():
        if support >= min_support:
            frequent_subgraph.add_nodes_from(subgraph.nodes)
            frequent_subgraph.add_edges_from(subgraph.edges)
    
    return frequent_subgraph

def image_grid(imgs, rows, cols):

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid