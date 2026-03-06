import torch
import torch.nn as nn
from senses import SensoryPort

class CausalAnchor(nn.Module):
    def __init__(self, num_concepts, embedding_dim):
        super(CausalAnchor, self).__init__()
        self.embedding = nn.Embedding(num_concepts, embedding_dim)
        self.linear = nn.Linear(embedding_dim, embedding_dim)
        self.layer_norm = nn.LayerNorm(embedding_dim)

    def forward(self, concept_ids):
        embeddings = self.embedding(concept_ids)
        x = torch.relu(self.linear(embeddings))
        x = self.layer_norm(x)
        return x

class CausalAnchorSensoryPort(SensoryPort):
    def __init__(self, num_concepts, embedding_dim):
        super(CausalAnchorSensoryPort, self).__init__()
        self.anchor = CausalAnchor(num_concepts, embedding_dim)

    def process(self, concept_ids, sensory_data):
        # Assume sensory_data is a tensor of shape (batch_size, sequence_length)
        anchor_output = self.anchor(concept_ids)
        # Add additional processing steps here, e.g., attention mechanisms, etc.
        return anchor_output

if __name__ == "__main__":
    # Test the CausalAnchor
    num_concepts = 10
    embedding_dim = 128
    concept_ids = torch.randint(0, num_concepts, (10,))
    anchor = CausalAnchor(num_concepts, embedding_dim)
    output = anchor(concept_ids)
    print(output.shape)