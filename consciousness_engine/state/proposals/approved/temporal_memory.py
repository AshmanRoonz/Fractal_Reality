import torch
import torch.nn as nn
import numpy as np
from torch.nn import functional as F
from senses import SensoryPort

class TemporalMemory(nn.Module):
    def __init__(self, embedding_dim, sequence_length, hidden_dim):
        super(TemporalMemory, self).__init__()
        self.embedding = nn.Embedding(sequence_length, embedding_dim)
        self.rnn = nn.GRU(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])
        return out

class TemporalMemoryPort(SensoryPort):
    def __init__(self, embedding_dim, sequence_length, hidden_dim):
        super(TemporalMemoryPort, self).__init__()
        self.tm = TemporalMemory(embedding_dim, sequence_length, hidden_dim)

    def process(self, input_seq, context_seq):
        input_seq = self.tm.embedding(input_seq)
        context_seq = self.tm.embedding(context_seq)
        return torch.cat((input_seq, context_seq), dim=1)

def main():
    embedding_dim = 128
    sequence_length = 10
    hidden_dim = 256
    tm = TemporalMemory(embedding_dim, sequence_length, hidden_dim)
    tm_port = TemporalMemoryPort(embedding_dim, sequence_length, hidden_dim)

    input_seq = torch.randint(0, 10, (1, 5))
    context_seq = torch.randint(0, 10, (1, 5))
    output = tm_port.process(input_seq, context_seq)
    print(output.shape)

if __name__ == "__main__":
    main()