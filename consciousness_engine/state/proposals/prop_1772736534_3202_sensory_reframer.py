import torch
import torch.nn as nn
import numpy as np
from senses import SensoryPort

class SensoryReframer(SensoryPort):
    def __init__(self, device):
        super().__init__(device)
        self.linear = nn.Linear(100, 100)  # dummy layer for demonstration purposes
        self.conv1d = nn.Conv1d(1, 1, kernel_size=3)  # dummy layer for demonstration purposes
        self.norm = nn.LayerNorm(100)  # dummy layer for demonstration purposes

    def reframe(self, input_signal, context_signal):
        # dummy reframe logic
        return torch.cat((input_signal, context_signal), dim=1)

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    reframer = SensoryReframer(device)
    input_signal = torch.randn(1, 100)  # dummy input signal
    context_signal = torch.randn(1, 100)  # dummy context signal
    reframed_signal = reframer.reframe(input_signal, context_signal)
    print(reframed_signal)

if __name__ == "__main__":
    main()