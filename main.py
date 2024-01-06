import networkx as nx
import matplotlib.pyplot as plt
from C45.c45.c45 import C45
from get_data import get_games, Game


def show_graph(graph):
    pos = nx.nx_agraph.graphviz_layout(G)
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

def create_graph_from_game(game: Game, time_frame: int):
    G = nx.DiGraph()
    for team in [1, 2]:
        for role in range(1, 6):
            G.add_node(f"T{team}-R{role}")
    G.add_node("DEATH")
    
    for blue_player, data in enumerate(game.time_frames[time_frame]):
        for red_player, data2 in enumerate(data):
            if data2[0] == 'TRUE':
                G.add_edge(f"T1-R{red_player+1}", f"T2-R{blue_player+1}")
            if data2[1] == 'TRUE':
                G.add_edge(f"T2-R{blue_player+1}", f"T1-R{red_player+1}")
    
    for player, data in enumerate(game.deaths_frames[time_frame]):
        if data == 'TRUE':
            if player < 5:
                G.add_edge(f"T1-R{player+1}", "DEATH")
            else:
                G.add_edge(f"T2-R{player-4}", "DEATH")
    return G


for i in range(1):
    print(f"Time frame {i}")
    G = create_graph_from_game(get_games()[0], 13)
    get_metrics(G)
    # show_graph(G)