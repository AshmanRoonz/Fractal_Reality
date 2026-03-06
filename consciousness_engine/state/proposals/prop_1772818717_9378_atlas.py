import torch
import torch.nn as nn
import numpy as np

class ConceptualAtlas(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(ConceptualAtlas, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.conv1d = nn.Conv1d(embedding_dim, embedding_dim, kernel_size=3)

    def forward(self, text):
        embedded_text = self.embedding(text)
        padded_text = nn.functional.pad(embedded_text, (0, embedding_dim - embedded_text.shape[-1]))
        conv_output = self.conv1d(padded_text)
        return conv_output

class ConceptualAtlasModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(ConceptualAtlasModel, self).__init__()
        self.atlas = ConceptualAtlas(vocab_size, embedding_dim)
        self.linear = nn.Linear(embedding_dim, vocab_size)

    def forward(self, text):
        output = self.atlas(text)
        return self.linear(output)

if __name__ == "__main__":
    vocab_size = 10000
    embedding_dim = 128
    text = torch.randint(0, vocab_size, (1, 10))
    model = ConceptualAtlasModel(vocab_size, embedding_dim)
    print(model(text).shape)