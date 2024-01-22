import networkx as nx

def translate_features():
    features = [
    ]

    for feature_list in features:
        print('[', end='')
        for feature in feature_list:
            print('(', end='')
            team, role = feature[1]%2, feature[1]//2
            if feature[1] == 10:
                print(f"'{feature[0]}', 'DEATH', {feature[2]}", end='')
            else:
                print(f"'{feature[0]}', '{['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]}', {feature[2]}", end='')
            if feature != feature_list[-1]:
                print('), ', end='')
            else:
                print(')', end='')
        print('],')

def FrequentSubgraphMining(graphs: list[nx.DiGraph], min_support) -> nx.DiGraph:
    pass

from itertools import combinations
from collections import Counter

def FSM(graphs, min_support):
    # Initialize frequent subgraphs
    frequent_subgraphs = nx.DiGraph()

    # Helper function to check if a subgraph is frequent
    def is_frequent(subgraph, support_counter):
        return support_counter[subgraph] >= min_support

    # Helper function to find all subgraphs in a directed graph
    def find_subgraphs(graph, min_size=1, max_size=None):
        if max_size is None:
            max_size = len(graph.nodes)
        subgraphs = []
        for size in range(min_size, max_size + 1):
            for nodes in combinations(graph.nodes, size):
                subgraph = graph.subgraph(nodes)
                if nx.is_weakly_connected(subgraph):  # Use is_weakly_connected for directed graphs
                    subgraphs.append(subgraph)
        return subgraphs

    # Initialize support dictionary
    support_counter = Counter()

    # Loop over each directed graph
    for graph in graphs:
        # Find all subgraphs in the graph
        subgraphs = find_subgraphs(graph)

        # Increment support for each subgraph
        support_counter.update(subgraphs)

    # Add frequent subgraphs to the result
    for subgraph, support in support_counter.items():
        if is_frequent(subgraph, support_counter):
            frequent_subgraphs.add_nodes_from(subgraph.graph.nodes)
            frequent_subgraphs.add_edges_from(subgraph.graph.edges)

    return frequent_subgraphs
