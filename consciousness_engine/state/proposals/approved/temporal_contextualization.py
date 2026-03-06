import torch
import torch.nn as nn
import numpy as np

class TemporalContextualizationModule(nn.Module):
    def __init__(self, num_layers=2, hidden_size=128, output_size=128):
        super(TemporalContextualizationModule, self).__init__()
        self.layers = nn.ModuleList([self._create_layer(hidden_size, output_size) for _ in range(num_layers)])

    def _create_layer(self, hidden_size, output_size):
        return nn.Sequential(
            nn.LSTM(input_size=hidden_size, hidden_size=hidden_size, batch_first=True),
            nn.Linear(hidden_size, output_size),
            nn.LayerNorm(output_size)
        )

    def forward(self, input_tensor):
        for layer in self.layers:
            input_tensor = layer(input_tensor)
        return input_tensor

class TemporalContextualizationModuleTest:
    def __main__(self):
        # Initialize the model, input tensor and output tensor
        model = TemporalContextualizationModule()
        input_tensor = torch.randn(1, 10, 128)
        output_tensor = torch.randn(1, 10, 128)

        # Forward pass
        output = model(input_tensor)
        print(output.shape)

        # Backward pass
        output = torch.randn(1, 10, 128)
        loss = torch.sum((output - output_tensor) ** 2)
        loss.backward()

# Test the module
if __name__ == "__main__":
    test = TemporalContextualizationModuleTest()
    test.__main__()