import torch
import torch.nn as nn
import numpy as np

class ConceptualAnchor(nn.Module):
    def __init__(self, embedding_dim=128, num_classes=1000):
        super(ConceptualAnchor, self).__init__()
        self.embedding = nn.Embedding(num_classes, embedding_dim)
        self.linear = nn.Linear(embedding_dim, embedding_dim)
        self.layer_norm = nn.LayerNorm(embedding_dim)

    def forward(self, concept_ids):
        embeddings = self.embedding(concept_ids)
        embeddings = self.linear(embeddings)
        embeddings = self.layer_norm(embeddings)
        return embeddings

class ConceptualAnchorSensoryPort(nn.Module):
    def __init__(self, embedding_dim=128, num_classes=1000):
        super(ConceptualAnchorSensoryPort, self).__init__()
        self.anchor = ConceptualAnchor(embedding_dim, num_classes)

    def get_conceptual_analogues(self, query_concept_id):
        query_embedding = self.anchor(query_concept_id)
        analogues = []
        for i in range(10):
            analogue_concept_id = np.random.randint(0, 1000)
            analogue_embedding = self.anchor(anologue_concept_id)
            analogue_embedding = analogue_embedding.detach()
            analogue_embedding = analogue_embedding.numpy()
            analogue_embedding = analogue_embedding / np.linalg.norm(analogue_embedding)
            analogue_embedding = analogue_embedding * query_embedding
            analogues.append(analogue_concept_id)
        return analogues

if __name__ == "__main__":
    anchor = ConceptualAnchorSensoryPort()
    query_concept_id = 123
    analogues = anchor.get_conceptual_analogues(query_concept_id)
    print(analogues)