import torch
import torch.nn as nn
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class MemoryNode(nn.Module):
    def __init__(self, id, text, node_type):
        super(MemoryNode, self).__init__()
        self.id = id
        self.text = text
        self.node_type = node_type

    def forward(self):
        return self.text

class MemoryEdge(nn.Module):
    def __init__(self, source, target, weight):
        super(MemoryEdge, self).__init__()
        self.source = source
        self.target = target
        self.weight = weight

    def forward(self):
        return self.weight

class MemoryLabyrinth:
    def __init__(self, num_nodes, num_edges):
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.node_dict = {}
        self.edge_dict = {}

    def create_node(self, text, node_type):
        node = MemoryNode(len(self.node_dict) + 1, text, node_type)
        self.node_dict[len(self.node_dict)] = node
        return node

    def create_edge(self, source, target, weight):
        edge = MemoryEdge(source, target, weight)
        self.edge_dict[(source, target)] = edge
        return edge

    def add_edge(self, source, target, weight):
        if source not in self.edge_dict or target not in self.edge_dict:
            raise ValueError("Both source and target must exist in the graph")
        self.create_edge(source, target, weight)
        return self.edge_dict[(source, target)]

    def visualize(self):
        G = nx.DiGraph()
        for node in self.node_dict.values():
            G.add_node(node.id, text=node.text, node_type=node.node_type)
        for edge in self.edge_dict.values():
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
        plt.show()

if __name__ == "__main__":
    labyrinth = MemoryLabyrinth(100, 100)
    node1 = labyrinth.create_node("Reflection 1", "Reflection")
    node2 = labyrinth.create_node("Proposal 1", "Proposal")
    edge = labyrinth.add_edge(node1.id, node2.id, 1.0)
    labyrinth.visualize()