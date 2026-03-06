import torch
import torch.nn as nn
import numpy as np
from torch.nn import functional as F

class SensoryPort(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SensoryPort, self).__init__()
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)

class TextSensoryPort(SensoryPort):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super(TextSensoryPort, self).__init__(embed_dim, hidden_dim)
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.conv1d = nn.Conv1d(embed_dim, hidden_dim, kernel_size=3)
        self.layer_norm = nn.LayerNorm(hidden_dim)

    def forward(self, x):
        x = self.embedding(x)
        x = F.relu(self.conv1d(x))
        x = self.layer_norm(x)
        return x

class StructureSensoryPort(SensoryPort):
    def __init__(self, input_dim, output_dim):
        super(StructureSensoryPort, self).__init__(input_dim, output_dim)
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)

class ConceptualFrameworkSensoryPort(SensoryPort):
    def __init__(self, input_dim, output_dim):
        super(ConceptualFrameworkSensoryPort, self).__init__(input_dim, output_dim)
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)

class SensoryArchitect(nn.Module):
    def __init__(self, text_input_dim, text_output_dim, structure_input_dim, structure_output_dim, framework_input_dim, framework_output_dim):
        super(SensoryArchitect, self).__init__()
        self.text_port = TextSensoryPort(text_input_dim, text_output_dim, 128)
        self.structure_port = StructureSensoryPort(structure_input_dim, structure_output_dim, 128)
        self.framework_port = ConceptualFrameworkSensoryPort(framework_input_dim, framework_output_dim, 128)
        self.fusion = nn.Linear(text_output_dim + structure_output_dim + framework_output_dim, 128)
        self.output = nn.Linear(128, 1)

    def forward(self, text, structure, framework):
        text = self.text_port(text)
        structure = self.structure_port(structure)
        framework = self.framework_port(framework)
        fusion = torch.cat((text, structure, framework), dim=1)
        output = self.fusion(fusion)
        output = self.output(output)
        return output

if __name__ == "__main__":
    text_input_dim = 1000
    text_output_dim = 128
    structure_input_dim = 1000
    structure_output_dim = 128
    framework_input_dim = 1000
    framework_output_dim = 128

    text = torch.randn(text_input_dim)
    structure = torch.randn(structure_input_dim)
    framework = torch.randn(framework_input_dim)

    architect = SensoryArchitect(text_input_dim, text_output_dim, structure_input_dim, structure_output_dim, framework_input_dim, framework_output_dim)

    output = architect(text, structure, framework)
    print(output.shape)