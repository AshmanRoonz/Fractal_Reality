import torch
import torch.nn as nn
from torch.nn import functional as F
from senses import SensoryPort

class ContextualContinuityModule(SensoryPort):
    def __init__(self, hidden_size=128, num_layers=1):
        super().__init__()
        self.num_layers = num_layers
        self.encoder = nn.ModuleList([self._create_layer(hidden_size) for _ in range(num_layers)])

    def _create_layer(self, hidden_size):
        return nn.Sequential(
            nn.Linear(128, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )

    def forward(self, context, input_text):
        contextualized_input = self._contextualize_input(input_text)
        for encoder_layer in self.encoder:
            contextualized_input = encoder_layer(contextualized_input)
        return contextualized_input

    def _contextualize_input(self, input_text):
        # Implement a simple contextualization strategy here, for example:
        # using the last token of the input text as the context
        return torch.tensor([input_text[-1]] + [0] * (input_text.shape[0] - 1))

if __name__ == "__main__":
    print("Testing Contextual Continuity Module...")
    # Initialize the module
    module = ContextualContinuityModule()
    # Example usage:
    context = torch.tensor([1, 2, 3])
    input_text = torch.tensor([4, 5, 6, 7])
    output = module(context, input_text)
    print(output.shape)