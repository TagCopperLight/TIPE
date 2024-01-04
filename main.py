import networkx as nx
import matplotlib.pyplot as plt
from C45.c45.c45 import C45


def create_graph():
    G = nx.DiGraph()
    for team in [1, 2]:
        for role in range(1, 6):
            G.add_node(f"T{team}-R{role}")
    G.add_node("DEATH")
    return G

def add_edges_exemples(graph):
    graph.add_edge("T1-R1", "T2-R1")
    graph.add_edge("T1-R1", "T2-R2")
    graph.add_edge("T1-R1", "T1-R5")

    graph.add_edge("T1-R2", "DEATH")
    graph.add_edge("T1-R2", "T1-R4")

    graph.add_edge("T1-R3", "T2-R5")
    graph.add_edge("T1-R3", "T2-R3")

    graph.add_edge("T1-R4", "T1-R2")
    graph.add_edge("T1-R4", "T2-R4")

    graph.add_edge("T1-R5", "T1-R4")

    graph.add_edge("T2-R1", "DEATH")

    graph.add_edge("T2-R2", "T2-R5")

    graph.add_edge("T2-R3", "T1-R3")
    graph.add_edge("T2-R3", "DEATH")

    graph.add_edge("T2-R4", "T1-R1")
    graph.add_edge("T2-R4", "T1-R5")

    graph.add_edge("T2-R5", "T2-R2")
    graph.add_edge("T2-R5", "T2-R1")

    return graph

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

def show_graph(graph):
    pos = nx.nx_agraph.graphviz_layout(G)
    nx.draw(graph, with_labels=True, font_weight='bold', pos=pos)
    plt.show()

G = create_graph()
G = add_edges_exemples(G)
get_metrics(G)
show_graph(G)