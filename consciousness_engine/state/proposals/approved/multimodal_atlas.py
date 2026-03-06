import torch
import torch.nn as nn
import numpy as np

class MultimodalAtlas(nn.Module):
    def __init__(self, num_domains, num_senses, embedding_dim):
        super(MultimodalAtlas, self).__init__()
        self.num_domains = num_domains
        self.num_senses = num_senses
        self.embedding_dim = embedding_dim

        # Domain embeddings
        self.domain_embeddings = nn.Embedding(num_domains, embedding_dim)

        # Sense embeddings
        self.sense_embeddings = nn.Embedding(num_senses, embedding_dim)

        # Graph construction
        self.graph = nn.Parameter(torch.zeros(num_domains, num_domains))

    def forward(self, domain_ids, sense_ids):
        # Get domain and sense embeddings
        domain_embeddings = self.domain_embeddings(domain_ids)
        sense_embeddings = self.sense_embeddings(sense_ids)

        # Construct graph
        graph = self.graph

        # Compute similarity between domain and sense embeddings
        similarities = torch.matmul(domain_embeddings, sense_embeddings.T)

        # Compute graph structure
        graph = torch.sparse.from_tensor(similarities, torch.ones(similarities.shape[0], similarities.shape[1]))

        return graph

# Test the MultimodalAtlas
if __name__ == "__main__":
    atlas = MultimodalAtlas(num_domains=5, num_senses=3, embedding_dim=128)
    domain_ids = torch.tensor([0, 1, 2, 3, 4])
    sense_ids = torch.tensor([0, 1, 2])
    graph = atlas(domain_ids, sense_ids)
    print(graph.shape)