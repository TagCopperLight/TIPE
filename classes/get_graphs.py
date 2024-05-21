import logging
import networkx as nx
from matplotlib import pyplot as plt

import classes.importer as importer


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def show_graph(graph):
    pos = nx.nx_agraph.graphviz_layout(graph)
    nx.draw(graph, with_labels=True, font_weight='bold', pos=pos)
    plt.show()

def create_graph_from_game(game, time_frame):
    G = nx.DiGraph()
    for team in [1, 2]:
        for role in range(1, 6):
            G.add_node(f'T{team}-R{role}')
    G.add_node('DEATH')
    
    if time_frame >= len(game.time_frames):
        return G

    for red_player, data in enumerate(game.time_frames[time_frame].interactions):
        for blue_player, data2 in enumerate(data):
            if data2[0]:
                G.add_edge(f'T1-R{red_player+1}', f'T2-R{blue_player+1}')
            if data2[1]:
                G.add_edge(f'T2-R{blue_player+1}', f'T1-R{red_player+1}')
    
    for team, data in enumerate(game.time_frames[time_frame].deaths):
        for player, data in enumerate(data):
            if data:
                    G.add_edge(f'T{team+1}-R{player+1}', 'DEATH')
    return G

def get_metrics(graph):
    indegrees = {}
    outdegrees = {}
    for node in graph.nodes:
        indegrees[node] = graph.in_degree(node)
        outdegrees[node] = graph.out_degree(node)
    
    return (indegrees,
            outdegrees,
            nx.closeness_centrality(graph),
            nx.betweenness_centrality(graph),
            nx.eigenvector_centrality(graph, max_iter=100000))

def save_graphs(games):
    graphs = []

    for i, game in enumerate(games):
        log.info(f'Game {i+1}/{len(games)}')
        game_metrics = {'game_id': game.game_id, 'winner': game.winner, 'time_frames': []}
        for time_frame in range(len(game.time_frames)):
            graph = create_graph_from_game(game, time_frame)
            metrics = get_metrics(graph)
            game_metrics['time_frames'].append({'metrics': {'indeg': metrics[0], 'outdeg': metrics[1], 'cls': metrics[2], 'btw': metrics[3], 'eige': metrics[4]}})
        graphs.append(game_metrics)

    importer.write_graphs(graphs)