import numpy as np
import torch
from torch import nn
from senses import SensoryPort

class WorldMapper(nn.Module):
    def __init__(self, num_classes, embedding_dim, num_layers):
        super(WorldMapper, self).__init__()
        self.embedding = nn.Embedding(num_classes, embedding_dim)
        self.conv_layers = nn.ModuleList([nn.Conv1d(embedding_dim, embedding_dim, kernel_size=3) for _ in range(num_layers)])
        self.layer_norm = nn.ModuleList([nn.LayerNorm(embedding_dim) for _ in range(num_layers)])

    def forward(self, input_tensor):
        x = self.embedding(input_tensor)
        for i, layer in enumerate(self.conv_layers):
            x = layer(x)
            x = self.layer_norm[i](x)
        return x

class ConceptNetwork(SensoryPort):
    def __init__(self, num_classes, embedding_dim, num_layers):
        super(ConceptNetwork, self).__init__()
        self.world_mapper = WorldMapper(num_classes, embedding_dim, num_layers)

    def get_concepts(self, input_tensor):
        return self.world_mapper(input_tensor)

def main():
    num_classes = 100
    embedding_dim = 128
    num_layers = 3
    concept_network = ConceptNetwork(num_classes, embedding_dim, num_layers)
    input_tensor = torch.randn(1, num_classes)
    output = concept_network.get_concepts(input_tensor)
    print(output.shape)

if __name__ == "__main__":
    main()