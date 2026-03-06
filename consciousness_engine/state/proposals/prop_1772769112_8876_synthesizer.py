import torch
import numpy as np
from torch import nn
from senses import SensoryPort

class PhiRatioSensoryPort(SensoryPort):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__(input_dim, hidden_dim, output_dim)
        self.phi_ratio_layer = nn.Linear(input_dim, hidden_dim)
        self.phi_ratio_layer.apply(lambda x: nn.init.orthogonal_(x))
        self.phi_ratio_layer.weight.data mul= 0.1

    def forward(self, x):
        x = torch.relu(self.phi_ratio_layer(x))
        return x

class FractalSensoryPort(SensoryPort):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__(input_dim, hidden_dim, output_dim)
        self.fractal_layer = nn.Linear(input_dim, hidden_dim)
        self.fractal_layer.apply(lambda x: nn.init.orthogonal_(x))
        self.fractal_layer.weight.data mul= 0.1

    def forward(self, x):
        x = torch.relu(self.fractal_layer(x))
        return x

class ConceptualSynthesizer(nn.Module):
    def __init__(self, phi_ratio_sensory_port, fractal_sensory_port, hidden_dim, output_dim):
        super().__init__()
        self.phi_ratio_sensory_port = phi_ratio_sensory_port
        self.fractal_sensory_port = fractal_sensory_port
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim)
        self.hidden_layer.apply(lambda x: nn.init.orthogonal_(x))
        self.hidden_layer.weight.data mul= 0.1
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        self.output_layer.apply(lambda x: nn.init.orthogonal_(x))
        self.output_layer.weight.data mul= 0.1

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