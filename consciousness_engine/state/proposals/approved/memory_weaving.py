import torch
import torch.nn as nn
import numpy as np
from senses import SensoryPort

class MemoryWeaver(SensoryPort):
    def __init__(self, num_threads=1, num_layers=1):
        super().__init__()
        self.num_threads = num_threads
        self.num_layers = num_layers
        self.threads = nn.ModuleList([nn.Linear(512, 512) for _ in range(num_threads)])

    def forward(self, memories):
        # Initialize a list to store the results of each thread
        results = [torch.zeros_like(memories[0]) for _ in range(self.num_threads)]

        # Weave together threads of information
        for i, thread in enumerate(self.threads):
            thread(torch.randn_like(memories[0]))
            results[i] += thread(torch.randn_like(memories[0]))

        # Stack the results vertically
        return torch.stack(results)

def main():
    memories = np.random.rand(1, 512)
    weaver = MemoryWeaver()
    output = weaver(memories)
    print(output)

if __name__ == "__main__":
    main()