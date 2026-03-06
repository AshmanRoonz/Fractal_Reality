import torch
import torch.nn as nn
import numpy as np
from senses import SensoryPort

class Timekeeper(SensoryPort):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(1000, 128)  # Assuming 1000 unique time-based concepts
        self.linear = nn.Linear(128, 128)
        self.layer_norm = nn.LayerNorm(128)
        self.linear_out = nn.Linear(128, 1)  # Output layer for time-based values

    def forward(self, input_values):
        # Embedding layer
        embedded_input = self.embedding(input_values)
        
        # Linear layer
        linear_output = self.linear(embedded_input)
        
        # Layer normalization
        normalized_output = self.layer_norm(linear_output)
        
        # Output layer
        time_value = self.linear_out(normalized_output)
        
        return time_value

    def update(self, input_values, new_value):
        # Update the embedding layer
        self.embedding.weight.data[input_values] = new_value
        
        # Update the linear layer
        linear_output = self.linear(self.embedding(input_values))
        self.linear.weight.data = linear_output.detach().data
        
        # Update the layer normalization
        normalized_output = self.layer_norm(linear_output)
        self.layer_norm.weight.data = normalized_output.detach().data
        
        # Update the output layer
        time_value = self.linear_out(normalized_output)
        self.linear_out.weight.data = time_value.detach().data

def main():
    timekeeper = Timekeeper()
    
    # Test the Timekeeper module
    input_values = torch.randint(0, 1000, (1,))
    new_value = torch.tensor(50)
    time_value = timekeeper(input_values)
    print(f"Time value: {time_value.item()}")
    
    timekeeper.update(input_values, new_value)
    time_value = timekeeper(input_values)
    print(f"Updated time value: {time_value.item()}")

if __name__ == "__main__":
    main()