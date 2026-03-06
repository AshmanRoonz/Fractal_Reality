import torch
import numpy as np
import torch.nn as nn

class PhiRatioSensoryPort(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.phi_ratio_layer = nn.Linear(input_dim, hidden_dim)
        self.phi_ratio_layer.weight.data.uniform_(-0.1, 0.1)
        self.phi_ratio_layer.bias.data.zero_()
        self.phi_ratio_layer.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.orthogonal_(module.weight)
            module.bias.data.zero_()

    def forward(self, x):
        x = torch.relu(self.phi_ratio_layer(x))
        return x

class FractalSensoryPort(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.fractal_layer = nn.Linear(input_dim, hidden_dim)
        self.fractal_layer.weight.data.uniform_(-0.1, 0.1)
        self.fractal_layer.bias.data.zero_()
        self.fractal_layer.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.orthogonal_(module.weight)
            module.bias.data.zero_()

    def forward(self, x):
        x = torch.relu(self.fractal_layer(x))
        return x

class ConceptualSynthesizer(nn.Module):
    def __init__(self, phi_ratio_sensory_port, fractal_sensory_port, hidden_dim, output_dim):
        super().__init__()
        self.phi_ratio_sensory_port = phi_ratio_sensory_port
        self.fractal_sensory_port = fractal_sensory_port
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim)
        self.hidden_layer.weight.data.uniform_(-0.1, 0.1)
        self.hidden_layer.bias.data.zero_()
        self.hidden_layer.apply(self._init_weights)
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        self.output_layer.weight.data.uniform_(-0.1, 0.1)
        self.output_layer.bias.data.zero_()
        self.output_layer.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.orthogonal_(module.weight)
            module.bias.data.zero_()

    def forward(self, phi_ratio_input, fractal_input):
        phi_ratio_output = self.phi_ratio_sensory_port(phi_ratio_input)
        fractal_output = self.fractal_sensory_port(fractal_input)
        combined_output = torch.cat((phi_ratio_output, fractal_output), dim=1)
        combined_output = torch.relu(self.hidden_layer(combined_output))
        output = self.output_layer(combined_output)
        return output

if __name__ == "__main__":
    phi_ratio_sensory_port = PhiRatioSensoryPort(1, 10, 10)
    fractal_sensory_port = FractalSensoryPort(1, 10, 10)
    synthesizer = ConceptualSynthesizer(phi_ratio_sensory_port, fractal_sensory_port, 10, 10)
    print(synthesizer)