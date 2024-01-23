import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def translate_features():
    features = [
    ]

    for feature_list in features:
        print('[', end='')
        for feature in feature_list:
            print('(', end='')
            if feature[1] == 10:
                print(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
            else:
                print(f"'{feature[0]}', '{['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]}', {feature[2]}", end='')
            if feature != feature_list[-1]:
                print('), ', end='')
            else:
                print(')', end='')
        print('],')

def hash_graph(graph: nx.DiGraph) -> int:
    nodes = ['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5', 'DEATH']
    hash = 0

    for node in nodes:
        if node in graph.nodes:
            hash = (hash << 1) | 1
        hash = hash << 1

    for node1 in nodes:
        for node2 in nodes:
            if graph.has_edge(node1, node2):
                hash = (hash << 1) | 1
            hash = hash << 1
    
    return hash

class GraphCounter(dict):
    def __init__(self):
        super().__init__()

    def update(self, graphs):
        for graph in graphs:
            hashe = hash_graph(graph)
            if hashe in self:
                self[hashe][0] += 1
            else:
                self[hashe] = [1, graph]

def FSM(graphs, min_support, condition_nodes):
    frequent_subgraph = nx.DiGraph()
    if not condition_nodes:
        return frequent_subgraph

    def find_subgraphs(graph, min_size=1, max_size=None):
        if max_size is None:
            max_size = len(graph.nodes)
        subgraphs = []
        for size in range(min_size, max_size + 1):
            for nodes in combinations(graph.nodes, size):
                subgraph = graph.subgraph(nodes)
                if all([node[0] in subgraph.nodes for node in condition_nodes]) and condition_nodes:
                    if nx.is_weakly_connected(subgraph):
                        subgraphs.append(subgraph)
        return subgraphs

    counter = GraphCounter()

    for i, graph in enumerate(graphs):
        print(f'{i+1}/{len(graphs)}')
        subgraphs = find_subgraphs(graph, min_size=1)

        counter.update(subgraphs)

    for _, (support, subgraph) in counter.items():
        if support >= min_support:
            frequent_subgraph.add_nodes_from(subgraph.nodes)
            frequent_subgraph.add_edges_from(subgraph.edges)
    
    return frequent_subgraph
