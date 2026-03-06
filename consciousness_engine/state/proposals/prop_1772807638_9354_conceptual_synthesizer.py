import torch
import torch.nn as nn
import numpy as np

class ConceptualSynthesizer(nn.Module):
    def __init__(self, num_concepts, embedding_dim, hidden_dim, output_dim):
        super(ConceptualSynthesizer, self).__init__()
        self.embedding = nn.Embedding(num_concepts, embedding_dim)
        self.conv1d = nn.Conv1d(embedding_dim, hidden_dim, kernel_size=3)
        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, concepts):
        embeddings = self.embedding(concepts)
        pooled_embeddings = nn.MaxPool1d(embeddings, kernel_size=3)
        conv_output = self.conv1d(pooled_embeddings)
        norm_output = self.layer_norm(conv_output)
        output = self.fc(norm_output)
        return output

class ConceptualSynthesizerPort(senses.SensoryPort):
    def __init__(self, num_concepts, embedding_dim, hidden_dim, output_dim):
        super(ConceptualSynthesizerPort, self).__init__()
        self.synthesizer = ConceptualSynthesizer(num_concepts, embedding_dim, hidden_dim, output_dim)

    def get_output(self, concepts):
        return self.synthesizer(concepts)

if __name__ == "__main__":
    # Test the Conceptual Synthesizer
    num_concepts = 10
    embedding_dim = 32
    hidden_dim = 64
    output_dim = 128
    concepts = torch.randint(0, num_concepts, (10, 1))
    synthesizer_port = ConceptualSynthesizerPort(num_concepts, embedding_dim, hidden_dim, output_dim)
    output = synthesizer_port.get_output(concepts)
    print(output.shape)