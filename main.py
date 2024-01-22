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
from classes.utils import FSM


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
        print(f'Number of rules: {len(get_rules(tree, 0.7, 20))}')
        print()

def get_rules(tree, confidence, support):
    rules = {}

    with open('graph_data/data.json', 'r') as file:
        data = json.load(file)

    def __get_path_rec(data, node, path):
        if node.is_leaf:
            path.append((node, 'leaf'))
            return path
        else:
            if data[node.label] <= node.threshold:
                path.append((node, '<='))
                return __get_path_rec(data, node.children[0], path)
            elif len(node.children) == 2:
                path.append((node, '>'))
                return __get_path_rec(data, node.children[1], path)

    for game in data:
        path = __get_path_rec(game, tree.tree, [])
        
        if path[-1][0] not in rules:
            rules[path[-1][0]] = {'support': 1, 'confidence': 0}
            rules[path[-1][0]]['path'] = path
        else:
            rules[path[-1][0]]["support"] += 1

        if path[-1][0].label == game["class"]:
            rules[path[-1][0]]["confidence"] += 1

    for rule in rules:
        rules[rule]["confidence"] /= rules[rule]["support"]

    rules = {rule: rules[rule] for rule in rules if rules[rule]["confidence"] >= confidence and rules[rule]["support"] >= support}

    # for rule in rules:
    #     print(f'IF ', end='')
    #     for node in rules[rule]["path"]:
    #         if node[1] == 'leaf':
    #             print(f'THEN {node[0].label} win', end='')
    #         else:
    #             print(f'{node[0].label} {node[1]} {node[0].threshold} & ', end='')
    #     print(f'\n{rule.label} (support: {rules[rule]["support"]}, confidence: {rules[rule]["confidence"]})')
    #     print(f'\n(support: {rules[rule]["support"]}, confidence: {rules[rule]["confidence"]})')
    # print()

    return rules

def frequent_subgraph_mining(games, rule):
    print(f'IF ', end='')
    for node in rule["path"]:
        if node[1] == 'leaf':
            print(f'THEN {node[0].label} win', end='')
        else:
            print(f'{node[0].label} {node[1]} {node[0].threshold} & ', end='')
    print(f'\n(support: {rule["support"]}, confidence: {rule["confidence"]})')
    print()

    games_satisfying_rules = []
    
    with open('graph_data/data.json', 'r') as file:
        data = json.load(file)

    with open('graph_data/graphs.json', 'r') as file:
        graphs = json.load(file)

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

    for saved_matrics, game in zip(data, games):
        if __verify_rule(saved_matrics, rule['path']):
            games_satisfying_rules.append((game, saved_matrics))

    for time_frame in range(nb_time_frames):
        graphs = [create_graph_from_game(game, time_frame) for game, _ in games_satisfying_rules]
        frequent_subgraph = FSM(graphs, 0.75*len(games_satisfying_rules))
        print(frequent_subgraph)

def main():
    games: list[Game] = get_games()

    trained_features = [
        # [('indeg', 'T1-R2', 8), ('cls', 'T1-R1', 5), ('btw', 'T1-R4', 9), ('eige', 'T2-R1', 3), ('eige', 'T2-R2', 7)],
        # [('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        # [('btw', 'T2-R1', 13), ('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        # [('indeg', 'T1-R5', 12), ('cls', 'T1-R4', 9), ('cls', 'T2-R4', 11), ('btw', 'T2-R1', 14), ('btw', 'T1-R2', 7), ('eige', 'T2-R1', 9), ('eige', 'T1-R3', 5)],
        # [('cls', 'T2-R1', 10), ('btw', 'T2-R4', 10), ('btw', 'T2-R5', 9), ('eige', 'T2-R1', 6), ('eige', 'T1-R2', 11), ('eige', 'DEATH', 9)],
        # [('indeg', 'T2-R1', 8), ('outdeg', 'T1-R5', 11), ('btw', 'T1-R5', 14), ('eige', 'T2-R1', 2)],
        # [('cls', 'T2-R1', 12), ('eige', 'T1-R1', 10), ('eige', 'T1-R4', 7), ('eige', 'T2-R5', 14), ('eige', 'DEATH', 6)],
        # [('outdeg', 'T2-R1', 5), ('outdeg', 'T1-R2', 10), ('cls', 'T2-R1', 5), ('cls', 'T2-R2', 3), ('cls', 'T1-R3', 13)],
        # [('outdeg', 'T1-R4', 12), ('outdeg', 'T1-R5', 7), ('cls', 'T2-R4', 11), ('btw', 'T1-R4', 13), ('btw', 'T2-R2', 6), ('eige', 'T1-R5', 5)],
        [('outdeg', 'T1-R1', 12), ('outdeg', 'T1-R5', 11), ('cls', 'T2-R4', 2), ('btw', 'T2-R5', 8), ('eige', 'DEATH', 9)]
        # [('outdeg', 'T1-R1', 12), ('btw', 'T1-R5', 7), ('btw', 'T2-R4', 5), ('eige', 'T1-R4', 9), ('eige', 'T1-R5', 8), ('eige', 'T2-R5', 1)],
        # [('outdeg', 'T1-R2', 5), ('btw', 'T1-R2', 11), ('eige', 'T1-R1', 0), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 7), ('eige', 'T2-R1', 12)],
        # [('outdeg', 'T1-R5', 11), ('outdeg', 'T1-R5', 14), ('btw', 'T1-R5', 14), ('btw', 'T2-R1', 8), ('eige', 'T1-R1', 11)],
        # [('indeg', 'DEATH', 10), ('cls', 'T1-R4', 8), ('btw', 'T1-R5', 7), ('eige', 'T1-R5', 0), ('eige', 'T1-R5', 5)]
    ]

    rule_list = []
    flatten_rule_list = []

    for features in trained_features:
        # get_selected_features(games, features)
        create_decision_tree_files(games, features)
        tree = create_decision_tree()
        rule_list.append(get_rules(tree, 0.7, 20))

    for rules in rule_list:
        for rule in rules:
            flatten_rule_list.append(rules[rule])
    
    flatten_rule_list.sort(key=lambda x: x["support"]*x['confidence'], reverse=True)
    frequent_subgraph_mining(games, flatten_rule_list[0])

    # train_features(games)

    # save_graphs(games)
    # get_selected_features(games)

if __name__ == '__main__':
    main()