import pathlib
import logging
import networkx as nx
from PIL import Image, ImageOps
from matplotlib import pyplot as plt

from classes.utils import image_grid
from methods.get_rules import get_rules
from classes.FSM import frequent_subgraph_mining
from methods.get_tree import create_decision_tree_files, create_decision_tree

IMAGES_PATH = pathlib.Path('graph_images')


log = logging.getLogger(__name__)
logging.basicConfig(format='[%(name)s] %(asctime)s <%(levelname)s> %(message)s', level=logging.INFO, datefmt='%H:%M:%S')


def construct_frequents_subgraphs_image(graphs, path, name):
    """
    Construct the image of the frequent subgraphs in a grid.
    """
    
    images = []
    for frame in graphs:
        merged_graph = nx.DiGraph()
        for graph in frame:
            merged_graph.add_nodes_from(graph.nodes)
            merged_graph.add_edges_from(graph.edges)
            
        fig = plt.figure()
        # pos = nx.nx_agraph.graphviz_layout(merged_graph)
        nx.draw(merged_graph, with_labels=True, font_weight='bold', font_size=18)
        fig.canvas.draw()
        image = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
        image = ImageOps.expand(image, border=1, fill='black')

        images.append(image)
        plt.close(fig)

    log.info(len(images))
    grid = image_grid(images, 6, 5)

    if not path.exists():
        path.mkdir(parents=True)

    i=1
    while path / f'{name}_{i}.png' in path.iterdir():
        i += 1
    
    grid.save(path / f'{name}_{i}.png')


def construct_fs_from_corpus(games, trained_features, confidence=0.7, support=20, winner='T2', min_support=0.5):
    """
    Construct the image of the corpus of features.
    """
    
    graphs = []
    total_rules = 0

    for features in trained_features:
        flatten_rule_list = []

        create_decision_tree_files(games, features)
        tree = create_decision_tree()
        rules = get_rules(tree, confidence, support)
        for rule in rules:
            if rules[rule]['path'][-1][0].label == winner:
                flatten_rule_list.append(rules[rule])
        total_rules += len(flatten_rule_list)

        for rule in flatten_rule_list:
            log.info(f'Rule: {rule}')
            frequent_subgraphs = frequent_subgraph_mining(games, rule, min_support)
            for time_frame, frequent_subgraph in enumerate(frequent_subgraphs):
                if len(graphs) <= time_frame:
                    graphs.append([])
                graphs[time_frame].append(frequent_subgraph)
    
    log.info(f'Total rules: {total_rules}')

    construct_frequents_subgraphs_image(graphs, IMAGES_PATH / 'corpus', f'fs_{confidence}-{support}-{winner}-{min_support}')

def construct_fs_from_rule(games, features, features_name, confidence=0.7, support=20, winner='T2', min_support=0.5):
    """
    Construct the image of the FS from a rule.
    """

    flatten_rule_list = []

    create_decision_tree_files(games, features)
    tree = create_decision_tree()
    rules = get_rules(tree, confidence, support)
    for rule in rules:
        if rules[rule]['path'][-1][0].label == winner:
            flatten_rule_list.append(rules[rule])

    for rule in flatten_rule_list:
        log.info(f'Rule: {rule}')
        frequent_subgraphs = frequent_subgraph_mining(games, rule, min_support)
        frequent_subgraphs = [[i] for i in frequent_subgraphs]
        construct_frequents_subgraphs_image(frequent_subgraphs, IMAGES_PATH / 'single_rule' / features_name, f'fs_{confidence}-{support}-{winner}-{min_support}')
    
    log.info(f'Total rules: {len(flatten_rule_list)}')

    