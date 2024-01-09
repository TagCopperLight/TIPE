import pathlib
import json
import pickle
import logging
import random
import math
import networkx as nx
import matplotlib.pyplot as plt
from c45 import C45

from get_stats import Game, TimeFrame, show_interactions


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

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

def create_graph_from_game(game: Game, time_frame):
    G = nx.DiGraph()
    for team in [1, 2]:
        for role in range(1, 6):
            G.add_node(f"T{team}-R{role}")
    G.add_node("DEATH")
    
    if time_frame >= len(game.time_frames):
        return G

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

def get_metrics(graph):
    indegrees = {}
    outdegrees = {}
    for node in graph.nodes:
        indegrees[node] = graph.in_degree(node)
        outdegrees[node] = graph.out_degree(node)
    
    # print("Indegrees: ", indegrees)
    # print("Outdegrees: ", outdegrees)
    # print("Closeness centrality: ", nx.closeness_centrality(graph))
    # print("Betweenness centrality: ", nx.betweenness_centrality(graph))
    # print("Eigenvector centrality: ", nx.eigenvector_centrality(graph, max_iter=100000))

    return indegrees, outdegrees, nx.closeness_centrality(graph), nx.betweenness_centrality(graph), nx.eigenvector_centrality(graph, max_iter=100000)

def show_graph(graph):
    pos = nx.nx_agraph.graphviz_layout(graph)
    nx.draw(graph, with_labels=True, font_weight='bold', pos=pos)
    plt.show()

def create_decision_tree_files(games, features):
    features_names = {}
    for feature in features:
        features_names[feature] = f'{feature[0]} of {feature[1]} in time frame {feature[2]}'

    names = {"classes": ["T1", "T2"], "features": list(features_names.values())}
    with open("graph_data/names.json", "w") as file:
        json.dump(names, file, indent=4)

    data = []
    for game in games:
        game_metrics = {"class": "T1"} if game.winner == 'blue' else {"class": "T2"}
        for feature in features:
            graph = create_graph_from_game(game, feature[2])
            metrics = get_metrics(graph)
            if feature[0] == 'indeg':
                game_metrics[features_names[feature]] = metrics[0][feature[1]]
            elif feature[0] == 'outdeg':
                game_metrics[features_names[feature]] = metrics[1][feature[1]]
            elif feature[0] == 'cls':
                game_metrics[features_names[feature]] = metrics[2][feature[1]]
            elif feature[0] == 'btw':
                game_metrics[features_names[feature]] = metrics[3][feature[1]]
            elif feature[0] == 'eige':
                game_metrics[features_names[feature]] = metrics[4][feature[1]]
        
        data.append(game_metrics)

    with open("graph_data/data.json", "w") as file:
        json.dump(data, file, indent=4)
        
def create_decision_tree():
    with open("graph_data/names.json", "r") as file:
        names = json.load(file)

    with open("graph_data/data.json", "r") as file:
        data = json.load(file)

    c45 = C45(data, names["classes"], names["features"])
    c45.generate_tree()
    # c45.print_tree()
    log.info(f'Accuracy : {c45.get_accuracy()}')

    return c45.get_accuracy()

def main():
    games: list[Game] = get_games()
    best_accuracy = 0
    best_features = []

    for i in range(100):
        nb_features = random.randint(1, 30)
        # log.info(f'Number of features: {nb_features}')

        features = []

        for i in range(nb_features):
            feature = random.choice(['indeg', 'outdeg', 'cls', 'btw', 'eige'])
            team = random.randint(1, 2)
            role = random.randint(1, 5)
            time_frame = random.randint(0, 15)
            # log.info(f'Feature {i+1}: {feature} of T{team}-R{role} in time frame {time_frame}')

            features.append((feature, f'T{team}-R{role}', time_frame))
        

        # log.info('Creating files ...')
        create_decision_tree_files(games, features)
        # log.info('Files created')
        # log.info('Creating decision tree ...')
        acc = create_decision_tree() - math.sqrt(math.log(nb_features, 2))
        # log.info('Decision tree created')
        if acc > best_accuracy:
            best_accuracy = acc
            best_features = features
            log.info(f'New best accuracy: {best_accuracy}')
            log.info(f'New best features: {best_features}')

        log.info(f'Best accuracy: {best_accuracy}')

if __name__ == '__main__':
    main()