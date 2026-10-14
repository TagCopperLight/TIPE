import math
import pathlib
import logging
import networkx as nx
from PIL import Image, ImageOps
from matplotlib import pyplot as plt, font_manager
from matplotlib.patches import Circle, FancyArrowPatch

from classes.utils import image_grid
from methods.get_rules import get_rules
from classes.FSM import frequent_subgraph_mining
from methods.get_tree import create_decision_tree_files, create_decision_tree

IMAGES_PATH = pathlib.Path('graph_images')

# Colors of the dark figure: background, text, frame titles, hints, DEATH and idle players, edges, then team 1 and team 2
DARK_COLORS = {'background': '#05060B', 'text': '#D9D9D9', 'title': '#CBC6E6', 'hint': '#8B8C91', 'gray': '#3E4151',
               'edge': '#5A5A62', 'T1': '#73BFF9', 'T2': '#EDB3B6'}
DARK_FONTS = ['Monaco', 'Menlo', 'JetBrains Mono', 'DejaVu Sans Mono']


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


def get_circle_positions(radius=1.0):
    """
    Place team 1 on the left half of a circle, team 2 on the right half and DEATH in the middle.
    """

    positions = {'DEATH': (0.0, 0.0)}
    for i in range(5):
        left, right = math.radians(120 + i * 30), math.radians(60 - i * 30)
        positions[f'T1-R{i + 1}'] = (radius * math.cos(left), radius * math.sin(left))
        positions[f'T2-R{i + 1}'] = (radius * math.cos(right), radius * math.sin(right))
    return positions


def construct_dark_frequent_subgraphs_image(graphs, path, name, max_frames=15, columns=5, font_path=None):
    """
    Construct the image of the frequent subgraphs on a dark background, one panel per 2 minutes time frame.
    Every player keeps the same place in every panel, so the panels can be compared.
    """

    colors = DARK_COLORS
    if font_path is not None:
        font_manager.fontManager.addfont(font_path)
        fonts = [font_manager.FontProperties(fname=font_path).get_name()]
    else:
        installed = {font.name for font in font_manager.fontManager.ttflist}
        fonts = [font for font in DARK_FONTS if font in installed] or ['monospace']

    positions = get_circle_positions()
    node_radius = 0.075
    rows = math.ceil(min(len(graphs), max_frames) / columns)

    fig = plt.figure(figsize=(18, 18 * rows / columns * 1.08), dpi=200, facecolor=colors['background'])
    for time_frame, frame in enumerate(graphs[:max_frames]):
        merged_graph = nx.DiGraph()
        for graph in frame:
            merged_graph.add_nodes_from(graph.nodes)
            merged_graph.add_edges_from(graph.edges)
        nodes, edges = set(merged_graph.nodes), list(merged_graph.edges)

        ax = fig.add_subplot(rows, columns, time_frame + 1)
        ax.set_facecolor(colors['background'])
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_xlim(-1.55, 1.55)
        ax.set_ylim(-1.45, 1.6)
        ax.text(-1.5, 1.55, f'{2 * time_frame:02d}-{2 * time_frame + 2:02d} MIN', color=colors['title'], fontsize=11, family=fonts, va='top')

        for node, (x, y) in positions.items():
            if node == 'DEATH' and not nodes:
                continue
            if node not in nodes:
                ax.add_patch(Circle((x, y), 0.035, color=colors['gray'], lw=0, zorder=3))
                continue

            ax.add_patch(Circle((x, y), node_radius, color=colors['gray'] if node == 'DEATH' else colors[node[:2]], lw=0, zorder=3))
            if node == 'DEATH':
                label_x, label_y, align = 0, -0.24, 'center'
            elif abs(y) < 0.6:
                label_x, label_y, align = x + math.copysign(0.13, x), y, 'left' if x > 0 else 'right'
            else:
                label_x, label_y, align = x, y + math.copysign(0.2, y), 'center'
            ax.text(label_x, label_y, node, color=colors['text'], fontsize=8.5, family=fonts, ha=align, va='center', zorder=4)

        for source, target in edges:
            # Curve the two edges of a pair so they don't overlap
            rad = 0.25 if (target, source) in edges else 0.0
            ax.add_patch(FancyArrowPatch(positions[source], positions[target], connectionstyle=f'arc3,rad={rad}',
                                         arrowstyle='-|>,head_length=4,head_width=2.2', color=colors['edge'], lw=1.3,
                                         shrinkA=9, shrinkB=9, zorder=2))

        if not nodes:
            ax.text(0, 0, 'NO PATTERN', color=colors['hint'], fontsize=9, family=fonts, ha='center', va='center')

    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.01, wspace=0.05, hspace=0.12)

    if not path.exists():
        path.mkdir(parents=True)

    i = 1
    while path / f'{name}_dark_{i}.png' in path.iterdir():
        i += 1

    fig.savefig(path / f'{name}_dark_{i}.png', facecolor=colors['background'])
    plt.close(fig)


def construct_fs_from_corpus(games, trained_features, confidence=0.7, support=20, winner='T2', min_support=0.5, dark=False):
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

    construct_image = construct_dark_frequent_subgraphs_image if dark else construct_frequents_subgraphs_image
    construct_image(graphs, IMAGES_PATH / 'corpus', f'fs_{confidence}-{support}-{winner}-{min_support}')

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