import torch
import torch.nn as nn
from torch.nn import functional as F

class ContextualizationLens(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, output_dim):
        super(ContextualizationLens, self).__init__()
        self.embedding = nn.Embedding(1000, embedding_dim)
        self.linear1 = nn.Linear(embedding_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.output = nn.Linear(hidden_dim, output_dim)

    def forward(self, concept1, concept2, hidden_state):
        concept1_embedding = self.embedding(concept1)
        concept2_embedding = self.embedding(concept2)
        linear_output = torch.cat((concept1_embedding, hidden_state), dim=1)
        linear_output = self.linear1(linear_output)
        linear_output = F.relu(self.linear2(linear_output))
        linear_output = self.layer_norm(linear_output)
        output = self.output(linear_output)
        return output

# Example usage:
if __name__ == "__main__":
    lens = ContextualizationLens(embedding_dim=128, hidden_dim=256, output_dim=512)
    concept1 = torch.tensor(1)
    concept2 = torch.tensor(2)
    hidden_state = torch.tensor([0.5, 0.3])
    output = lens(concept1, concept2, hidden_state)
    print(output)