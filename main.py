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

VOID_METRICS = {
    'indeg': {'T1-R1': 0, 'T1-R2': 0, 'T1-R3': 0, 'T1-R4': 0, 'T1-R5': 0, 'T2-R1': 0, 'T2-R2': 0, 'T2-R3': 0, 'T2-R4': 0, 'T2-R5': 0, 'DEATH': 0},
    'outdeg': {'T1-R1': 0, 'T1-R2': 0, 'T1-R3': 0, 'T1-R4': 0, 'T1-R5': 0, 'T2-R1': 0, 'T2-R2': 0, 'T2-R3': 0, 'T2-R4': 0, 'T2-R5': 0, 'DEATH': 0},
    'cls': {'T1-R1': 0.0, 'T1-R2': 0.0, 'T1-R3': 0.0, 'T1-R4': 0.0, 'T1-R5': 0.0, 'T2-R1': 0.0, 'T2-R2': 0.0, 'T2-R3': 0.0, 'T2-R4': 0.0, 'T2-R5': 0.0, 'DEATH': 0.0},
    'btw': {'T1-R1': 0.0, 'T1-R2': 0.0, 'T1-R3': 0.0, 'T1-R4': 0.0, 'T1-R5': 0.0, 'T2-R1': 0.0, 'T2-R2': 0.0, 'T2-R3': 0.0, 'T2-R4': 0.0, 'T2-R5': 0.0, 'DEATH': 0.0},
    'eige': {'T1-R1': 0.30151134457776363, 'T1-R2': 0.30151134457776363, 'T1-R3': 0.30151134457776363, 'T1-R4': 0.30151134457776363, 'T1-R5': 0.30151134457776363, 'T2-R1': 0.30151134457776363, 'T2-R2': 0.30151134457776363, 'T2-R3': 0.30151134457776363, 'T2-R4': 0.30151134457776363, 'T2-R5': 0.30151134457776363, 'DEATH': 0.30151134457776363}
}


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

    with open('graph_data/graphs.json', 'r') as file:
        graphs = json.load(file)

    data = []
    for game in games:
        data_to_tree = {"class": "T1"} if game.winner == 'blue' else {"class": "T2"}
        for feature in features:
            game_metrics = [graph for graph in graphs if graph["game_id"] == game.game_id][0]

            if feature[2] < len(game_metrics["time_frames"]):
                metrics = game_metrics["time_frames"][feature[2]]["metrics"]
            else:
                metrics = VOID_METRICS

            if feature[0] == 'indeg':
                data_to_tree[features_names[feature]] = metrics['indeg'][feature[1]]
            elif feature[0] == 'outdeg':
                data_to_tree[features_names[feature]] = metrics['outdeg'][feature[1]]
            elif feature[0] == 'cls':
                data_to_tree[features_names[feature]] = metrics['cls'][feature[1]]
            elif feature[0] == 'btw':
                data_to_tree[features_names[feature]] = metrics['btw'][feature[1]]
            elif feature[0] == 'eige':
                data_to_tree[features_names[feature]] = metrics['eige'][feature[1]]
        
        data.append(data_to_tree)

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

    return c45

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

def get_selected_features(games):
    best_accuracy = 0
    best_features = []
    best_tree = None

    for i in range(1):
        log.info(f'Iteration {i+1}/500')
        nb_features = random.randint(1, 10)
        nb_features = 0
        # log.info(f'Number of features: {nb_features}')

        features = []

        for i in range(nb_features):
            feature = random.choice(['indeg', 'outdeg', 'cls', 'btw', 'eige'])
            team = random.randint(1, 2)
            role = random.randint(1, 5)
            time_frame = random.randint(0, 30)
            # log.info(f'Feature {i+1}: {feature} of T{team}-R{role} in time frame {time_frame}')

            features.append((feature, f'T{team}-R{role}', time_frame))
        
        # features = [('indeg', 'T1-R2', 12), ('outdeg', 'T1-R2', 21), ('indeg', 'T2-R3', 0), ('cls', 'T2-R5', 10), ('indeg', 'T2-R5', 11), ('eige', 'T1-R4', 7), ('btw', 'T1-R4', 7), ('outdeg', 'T2-R1', 16)]
        features = [('cls', 'T1-R1', 11), ('btw', 'T2-R2', 4), ('cls', 'T2-R4', 1), ('indeg', 'T1-R2', 10), ('eige', 'T2-R1', 12)]

        # log.info('Creating files ...')
        create_decision_tree_files(games, features)
        # log.info('Files created')
        # log.info('Creating decision tree ...')
        tree = create_decision_tree()
        acc = tree.get_accuracy()
        # Penalty for too many features
        penalty = 0.02 * math.exp(nb_features/3)
        acc -= penalty
        log.info(f'Penalty: {penalty}')

        log.info(f'Accuracy: {acc}')
        # log.info('Decision tree created')
        if acc > best_accuracy:
            best_accuracy = acc
            best_features = features
            best_tree = tree
            log.info(f'New best accuracy: {best_accuracy}')
            log.info(f'New best features: {best_features}')
            
        log.info(f'Best accuracy: {best_accuracy}')
        log.info(f'Best True accuracy: {best_tree.get_accuracy()}')

    log.info(f'Best accuracy: {best_accuracy}')
    log.info(f'True accuracy: {best_tree.get_accuracy()}')
    log.info(f'Best features: {best_features}')
    best_tree.print_tree()

    print(best_tree.k_fold_cross_validation(10))

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
    # get_selected_features(games)
    tree = create_decision_tree()
    get_rules(tree, 0.5, 20)

    # save_graphs(games)
    # get_selected_features(games)

if __name__ == '__main__':
    main()