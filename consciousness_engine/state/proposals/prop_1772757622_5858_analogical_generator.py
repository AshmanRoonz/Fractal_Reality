import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class AnalogicalRelationshipGenerator(nn.Module):
    def __init__(self, embedding_dim=100, hidden_dim=128, num_layers=2):
        super(AnalogicalRelationshipGenerator, self).__init__()
        self.embedding = nn.Embedding(1000, embedding_dim)  # dummy embedding for demonstration
        self.linear1 = nn.Linear(embedding_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, 1)  # output layer for analogy score

    def forward(self, concept1, concept2):
        # encode concepts using embedding
        concept1_embedding = self.embedding(concept1)
        concept2_embedding = self.embedding(concept2)

        # compute similarity between concepts using dot product
        similarity = torch.matmul(concept1_embedding, concept2_embedding.T) / (concept1_embedding.norm(dim=1) * concept2_embedding.norm(dim=1))

        # apply transformations and get output
        output = F.relu(self.linear1(similarity))
        output = F.relu(self.linear2(output))
        output = self.fc(output)

        return output

class SensoryPort(AnalogicalRelationshipGenerator):
    def __init__(self, *args, **kwargs):
        super(SensoryPort, self).__init__(*args, **kwargs)
        # initialize dummy data
        self.dummy_data = np.random.rand(1000, embedding_dim)

    def generate_analogy(self, concept1, concept2):
        analogy_score = self(concept1, concept2)
        return analogy_score

if __name__ == "__main__":
    # test the analogy generator
    generator = AnalogicalRelationshipGenerator()
    concept1 = torch.tensor([1, 2, 3])
    concept2 = torch.tensor([4, 5, 6])
    analogy_score = generator.generate_analogy(concept1, concept2)
    print(analogy_score)