import torch
import torch.nn as nn
import numpy as np

class ContextualBridge(nn.Module):
    def __init__(self, hidden_size=128, num_layers=2):
        super(ContextualBridge, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(1024, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_size, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1024),
            nn.ReLU()
        )

    def forward(self, input_text):
        encoded_text = self.encoder(input_text)
        return self.decoder(encoded_text)

class SensoryPort(ContextualBridge, senses.SensoryPort):
    pass

if __name__ == "__main__":
    # Test the Contextual Bridge
    bridge = ContextualBridge()
    input_text = torch.tensor([[1, 2, 3], [4, 5, 6]])
    output = bridge(input_text)
    print(output.shape)