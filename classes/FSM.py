import re
import tqdm
import networkx as nx
from multiprocessing import Pool
from itertools import combinations

import importer as importer
from methods.get_graphs import create_graph_from_game


def hash_graph(graph):
    """
    Create a hash from a graph, to compare them.
    """
    
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
    """
    Herited from dict, to count the number of times a graph appears.
    Using the base function for comparing graph equality is too slow, so we hash the graphs
    and count occurrences of the hashs in a dict.
    """
    
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
    """
    Frequent subgraph mining function.
    """
    
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


def frequent_subgraph_mining(games, rule, minimum_support):
    """
    Apply the frequent subgraph mining algorithm to the games.
    Using multiprocessing to speed up the process.
    """
    
    games_satisfying_rules = []
    
    data = importer.get_graphs_files()[1]
    
    graphs = importer.get_graphs()

    nb_time_frames = max([len(game['time_frames']) for game in graphs])

    def __verify_rule(data, path):
        for node in path:
            if node[1] == 'leaf':
                if node[0].label != data["class"]:
                    return False
            elif node[1] == '<=':
                if data[node[0].label] > node[0].threshold:
                    return False
            elif node[1] == '>':
                if data[node[0].label] <= node[0].threshold:
                    return False
        return True
    
    condition_nodes = []
    for node in rule['path'][:-1]:
        _, player, frame = re.search(r'([a-z]+) of ([a-zA-z0-9-]+) in time frame ([0-9]+)', node[0].label).groups()
        condition_nodes.append((player, frame))

    for saved_matrics, game in zip(data, games):
        if __verify_rule(saved_matrics, rule['path']):
            games_satisfying_rules.append((game, saved_matrics))

    args = []
    
    for time_frame in range(nb_time_frames):
        condition_nodes_in_frame = [node for node in condition_nodes if node[1] == str(time_frame)]
        graphs = [create_graph_from_game(game, time_frame) for game, _ in games_satisfying_rules]
        args.append((graphs, minimum_support*len(games_satisfying_rules), condition_nodes_in_frame))

    processes = 6
    with Pool(processes=processes) as pool:
        frequent_subgraphs = pool.map(FSM, [arg for arg in args], chunksize=1)
        pool.close()
    
    return frequent_subgraphs