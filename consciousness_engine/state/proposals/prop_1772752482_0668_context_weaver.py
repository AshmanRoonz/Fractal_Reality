import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class ContextWeaver(nn.Module):
    def __init__(self, num_nodes, num_edges, activation=nn.ReLU()):
        super(ContextWeaver, self).__init__()
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.activation = activation
        self.G = nx.Graph()
        self.G.add_nodes_from(range(num_nodes))
        self.G.add_edges_from(range(num_edges))

    def forward(self, node_features, edge_features):
        """
        Compute the context vector for each node using the edge features.
        """
        # Compute the edge weights
        edge_weights = torch.matmul(edge_features, torch.transpose(edge_features, 1, 2))
        edge_weights = self.activation(edge_weights)

        # Compute the context vector for each node
        context_vectors = torch.zeros(self.num_nodes, self.num_nodes)
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if i != j:
                    context_vectors[i, j] = torch.matmul(node_features[i], torch.transpose(edge_features[j], 1, 2))
        context_vectors = self.activation(context_vectors)

        return context_vectors

class ContextWeaverModel(nn.Module):
    def __init__(self, num_nodes, num_edges, num_features):
        super(ContextWeaverModel, self).__init__()
        self.context_weaver = ContextWeaver(num_nodes, num_edges)
        self.linear = nn.Linear(num_features, num_features)

    def forward(self, node_features, edge_features):
        context_vectors = self.context_weaver(node_features, edge_features)
        output = self.linear(context_vectors)
        return output

def visualize_context_weaver(context_vectors):
    # Convert the context vectors to a networkx graph
    G = nx.Graph()
    G.add_nodes_from(range(len(context_vectors)))
    for i in range(len(context_vectors)):
        for j in range(len(context_vectors[i])):
            if context_vectors[i, j] > 0:
                G.add_edge(i, j)

    # Draw the graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()

if __name__ == "__main__":
    # Test the ContextWeaverModel
    node_features = torch.randn(2, 5)
    edge_features = torch.randn(2, 5)
    model = ContextWeaverModel(2, 2, 5)
    output = model(node_features, edge_features)
    print(output)
    visualize_context_weaver(output)