import re
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from multiprocessing import Pool

import classes.importer as importer
from classes.utils import FSM, image_grid
from classes.get_objects import Game, TimeFrame, show_interactions
from classes.get_tree import create_decision_tree_files, create_decision_tree
from classes.train_features import main as train_features, accuracy_fix, chunk_split


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

def frequent_subgraph_mining(games, rule, minimum_support):
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
        # frequent_subgraph = FSM(graphs, minimum_support*len(games_satisfying_rules), condition_nodes_in_frame)
        # frequent_subgraphs.append(frequent_subgraph)
        frequent_subgraphs = pool.map(FSM, [arg for arg in args], chunksize=1)
        pool.close()
    
    return frequent_subgraphs

def consruct_frequents_subgraphs_image(games, trained_features, winner='T2'):
    graphs = []
    total_rules = 0

    for features in trained_features:
        flatten_rule_list = []

        create_decision_tree_files(games, features)
        tree = create_decision_tree()
        rules = get_rules(tree, 0.7, 20)
        for rule in rules:
            if rules[rule]['path'][-1][0].label == winner:
                flatten_rule_list.append(rules[rule])
        total_rules += len(flatten_rule_list)

        # flatten_rule_list.sort(key=lambda x: x["support"]*x['confidence'], reverse=True)

        for rule in flatten_rule_list:
            print(f'Rule: {rule}')
            frequent_subgraphs = frequent_subgraph_mining(games, rule, 0.5)
            for time_frame, frequent_subgraph in enumerate(frequent_subgraphs):
                if len(graphs) <= time_frame:
                    graphs.append([])
                graphs[time_frame].append(frequent_subgraph)
    
    print(f'Total rules: {total_rules}')
    images = []
    for frame in graphs:
        merged_graph = nx.DiGraph()
        for graph in frame:
            merged_graph.add_nodes_from(graph.nodes)
            merged_graph.add_edges_from(graph.edges)
            
        fig = plt.figure()
        pos = nx.nx_agraph.graphviz_layout(merged_graph)
        nx.draw(merged_graph, with_labels=True, font_weight='bold', pos=pos, font_size=18)
        fig.canvas.draw()
        image = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
        image = ImageOps.expand(image, border=1, fill='black')

        images.append(image)
        plt.close(fig)

    print(len(images))
    grid = image_grid(images, 6, 5)
    grid.save('graph_data/frequent_subgraphs.png')

def main():
    games: list[Game] = importer.get_done_game_objects()

    trained_features = [
        [('indeg', 'T1-R2', 8), ('cls', 'T1-R1', 5), ('btw', 'T1-R4', 9), ('eige', 'T2-R1', 3), ('eige', 'T2-R2', 7)],
        [('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        [('btw', 'T2-R1', 13), ('btw', 'T1-R4', 15), ('btw', 'T2-R4', 7), ('eige', 'T1-R1', 11), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 13)],
        [('indeg', 'T1-R5', 12), ('cls', 'T1-R4', 9), ('cls', 'T2-R4', 11), ('btw', 'T2-R1', 14), ('btw', 'T1-R2', 7), ('eige', 'T2-R1', 9), ('eige', 'T1-R3', 5)],
        [('cls', 'T2-R1', 10), ('btw', 'T2-R4', 10), ('btw', 'T2-R5', 9), ('eige', 'T2-R1', 6), ('eige', 'T1-R2', 11), ('eige', 'DEATH', 9)],
        [('indeg', 'T2-R1', 8), ('outdeg', 'T1-R5', 11), ('btw', 'T1-R5', 14), ('eige', 'T2-R1', 2)],
        [('cls', 'T2-R1', 12), ('eige', 'T1-R1', 10), ('eige', 'T1-R4', 7), ('eige', 'T2-R5', 14), ('eige', 'DEATH', 6)],
        [('outdeg', 'T2-R1', 5), ('outdeg', 'T1-R2', 10), ('cls', 'T2-R1', 5), ('cls', 'T2-R2', 3), ('cls', 'T1-R3', 13)],
        [('outdeg', 'T1-R4', 12), ('outdeg', 'T1-R5', 7), ('cls', 'T2-R4', 11), ('btw', 'T1-R4', 13), ('btw', 'T2-R2', 6), ('eige', 'T1-R5', 5)],
        [('outdeg', 'T1-R1', 12), ('outdeg', 'T1-R5', 11), ('cls', 'T2-R4', 2), ('btw', 'T2-R5', 8), ('eige', 'DEATH', 9)],
        [('outdeg', 'T1-R1', 12), ('btw', 'T1-R5', 7), ('btw', 'T2-R4', 5), ('eige', 'T1-R4', 9), ('eige', 'T1-R5', 8), ('eige', 'T2-R5', 1)],
        [('outdeg', 'T1-R2', 5), ('btw', 'T1-R2', 11), ('eige', 'T1-R1', 0), ('eige', 'T1-R2', 11), ('eige', 'T1-R4', 7), ('eige', 'T2-R1', 12)],
        [('outdeg', 'T1-R5', 11), ('outdeg', 'T1-R5', 14), ('btw', 'T1-R5', 14), ('btw', 'T2-R1', 8), ('eige', 'T1-R1', 11)],
        [('indeg', 'DEATH', 10), ('cls', 'T1-R4', 8), ('btw', 'T1-R5', 7), ('eige', 'T1-R5', 0), ('eige', 'T1-R5', 5)]
    ]

    # consruct_frequents_subgraphs_image(games, trained_features)
    tree = create_decision_tree_files(games, trained_features[1])
    tree = create_decision_tree()
    get_rules(tree, 0.7, 20, verbose=True)
    # train_features(games)