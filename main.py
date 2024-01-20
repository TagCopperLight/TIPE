import pathlib
import json
import pickle
import logging
import random
import math
import networkx as nx
import matplotlib.pyplot as plt

from get_stats import Game, TimeFrame, show_interactions
from classes.get_tree import create_decision_tree_files, create_decision_tree
from classes.train_features import main as train_features, accuracy_fix


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

def save_graphs(games):
    graphs = []

    for i, game in enumerate(games):
        log.info(f'Game {i+1}/{len(games)}')
        game_metrics = {"game_id": game.game_id, "winner": game.winner, "time_frames": []}
        for time_frame in range(len(game.time_frames)):
            graph = create_graph_from_game(game, time_frame)
            metrics = get_metrics(graph)
            game_metrics["time_frames"].append({"metrics": {"indeg": metrics[0], "outdeg": metrics[1], "cls": metrics[2], "btw": metrics[3], "eige": metrics[4]}})
        graphs.append(game_metrics)

    with open("graph_data/graphs.json", "w") as file:
        json.dump(graphs, file, indent=4)

def get_selected_features(games, features):
        create_decision_tree_files(games, features)
        tree = create_decision_tree()
        acc = tree.get_accuracy()
        print(f'Fixed accuracy: {acc - accuracy_fix(features)}')
        print(f'Accuracy: {acc}')
        print(f'Features: {features}')
        print(f'Number of features: {len(features)}')
        print(f'3-fold cross validation: {tree.k_fold_cross_validation(3)}')
        print()

def get_rules(tree, confidence, support):
    rules = {}

    with open('graph_data/data.json', 'r') as file:
        data = json.load(file)

    def __get_path_rec(data, node, path):
        path.append(node)
        if node.is_leaf:
            return path
        else:
            if data[node.label] <= node.threshold:
                return __get_path_rec(data, node.children[0], path)
            else:
                return __get_path_rec(data, node.children[1], path)

    for game in data:
        path = []
        __get_path_rec(game, tree.tree, path)
        if path[-1] not in rules:
            rules[path[-1]] = {'support': 1, 'confidence': 0}
            rules[path[-1]]['path'] = path
        else:
            rules[path[-1]]["support"] += 1

        if path[-1].label == game["class"]:
            rules[path[-1]]["confidence"] += 1

    for rule in rules:
        rules[rule]["confidence"] /= rules[rule]["support"]

    rules = {rule: rules[rule] for rule in rules if rules[rule]["confidence"] >= confidence and rules[rule]["support"] >= support}

    for rule in rules:
        for node in rules[rule]["path"]:
            print(f'{node.label} <= {node.threshold} & ', end='')
        print(f'\n{rule.label} (support: {rules[rule]["support"]}, confidence: {rules[rule]["confidence"]})')

def main():
    games: list[Game] = get_games()

    trained_features = [
        [('indeg', 'T1-R2', 8), ('cls', 'T1-R1', 5), ('btw', 'T1-R4', 9), ('eige', 'T2-R1', 3), ('eige', 'T2-R2', 7)],
        [('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        [('btw', 'T2-R1', 13), ('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        [('indeg', 'T1-R5', 12), ('cls', 'T1-R4', 9), ('cls', 'T2-R4', 11), ('btw', 'T2-R1', 14), ('btw', 'T1-R2', 7), ('eige', 'T2-R1', 9), ('eige', 'T1-R3', 5)],
        [('cls', 'T2-R1', 10), ('btw', 'T2-R4', 10), ('btw', 'T2-R5', 9), ('eige', 'T2-R1', 6), ('eige', 'T1-R2', 11), ('eige', 'DEATH', 9)],
        [('indeg', 'T2-R1', 8), ('outdeg', 'T1-R5', 11), ('btw', 'T1-R5', 14), ('eige', 'T2-R1', 2)],
        [('cls', 'T2-R1', 12), ('eige', 'T1-R1', 10), ('eige', 'T1-R4', 7), ('eige', 'T2-R5', 14), ('eige', 'DEATH', 6)]
    ]

    # for features in trained_features:
    #     get_selected_features(games, features)

    train_features(games)
    #[['indeg', 2, 8], ['cls', 0, 5], ['btw', 6, 9], ['eige', 1, 3], ['eige', 3, 7]]
    #[['btw', 6, 15], ['btw', 7, 7], ['eige', 0, 11], ['eige', 2, 11], ['eige', 6, 13]]
    #[['btw', 1, 13], ['btw', 6, 15], ['btw', 7, 7], ['eige', 0, 11], ['eige', 2, 11], ['eige', 6, 13]]
    #[['indeg', 8, 12], ['cls', 6, 9], ['cls', 7, 11], ['btw', 1, 14], ['btw', 2, 7], ['eige', 1, 9], ['eige', 4, 5]]
    #[['cls', 1, 10], ['btw', 7, 10], ['btw', 9, 9], ['eige', 1, 6], ['eige', 2, 11], ['eige', 10, 9]]
    #[['indeg', 1, 8], ['outdeg', 8, 11], ['btw', 8, 14], ['eige', 1, 2]]

    # save_graphs(games)
    # get_selected_features(games)

if __name__ == '__main__':
    main()