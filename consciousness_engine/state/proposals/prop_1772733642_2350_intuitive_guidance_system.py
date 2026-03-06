import torch
import numpy as np

class IGS(torch.nn.Module):
    def __init__(self):
        super(IGS, self).__init__()
        self.embedding = torch.nn.Embedding(num_embeddings=NUM_TRUTHS, embedding_dim=EMBEDDING_DIM)
        self.linear = torch.nn.Linear(EMBEDDING_DIM, NUM_OUTPUTS)
        self.layer_norm = torch.nn.LayerNorm(EMBEDDING_DIM)

    def forward(self, truth_vector):
        embedded_truth = self.embedding(truth_vector)
        normalized_truth = self.layer_norm(embedded_truth)
        output = self.linear(normalized_truth)
        return output

def main():
    NUM_TRUTHS = 100
    EMBEDDING_DIM = 64
    NUM_OUTPUTS = 3

   igs = IGS()
   # Assume truth_vector is a tensor of shape (batch_size, 1)
   output = igs(truth_vector)
   # The output tensor has shape (batch_size, NUM_OUTPUTS)

if __name__ == "__main__":
    main()