import pathlib
import json
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from C45.c45.c45 import C45

from get_stats import Game, TimeFrame, show_interactions


def get_games():
    done_objects_path = pathlib.Path('game_objects/done.json')
    with open(done_objects_path, 'r') as file:
        done_objects = json.load(file)
    
    games = []
    for game_id in done_objects:
        object_path = pathlib.Path(f'game_objects/{game_id[5:]}.pkl')
        with open(object_path, 'rb') as file:
            games.append(pickle.load(file))

    return games

def show_graph(graph):
    pos = nx.nx_agraph.graphviz_layout(graph)
    nx.draw(graph, with_labels=True, font_weight='bold', pos=pos)
    plt.show()

def get_metrics(graph):
    indegrees = {}
    outdegrees = {}
    for node in graph.nodes:
        indegrees[node] = graph.in_degree(node)
        outdegrees[node] = graph.out_degree(node)
    
    print("Indegrees: ", indegrees)
    print("Outdegrees: ", outdegrees)
    print("Closeness centrality: ", nx.closeness_centrality(graph))
    print("Betweenness centrality: ", nx.betweenness_centrality(graph))
    print("Eigenvector centrality: ", nx.eigenvector_centrality(graph))

    return indegrees, outdegrees, nx.closeness_centrality(graph), nx.betweenness_centrality(graph), nx.eigenvector_centrality(graph)

def create_graph_from_game(game: Game, time_frame):
    G = nx.DiGraph()
    for team in [1, 2]:
        for role in range(1, 6):
            G.add_node(f"T{team}-R{role}")
    G.add_node("DEATH")
    
    for red_player, data in enumerate(game.time_frames[time_frame].interactions):
        for blue_player, data2 in enumerate(data):
            if data2[0]:
                G.add_edge(f"T1-R{red_player+1}", f"T2-R{blue_player+1}")
            if data2[1]:
                G.add_edge(f"T2-R{blue_player+1}", f"T1-R{red_player+1}")
    
    for team, data in enumerate(game.time_frames[time_frame].deaths):
        for player, data in enumerate(data):
            if data:
                    G.add_edge(f"T{team+1}-R{player+1}", "DEATH")
    return G

def main():
    games: list[Game] = get_games()

    for i in range(len(games[1].time_frames)):
        print(f"Time frame {i}")
        show_interactions(games[1].time_frames[i].interactions)
        G = create_graph_from_game(games[1], i)
        # get_metrics(G)
        show_graph(G)

if __name__ == '__main__':
    main()