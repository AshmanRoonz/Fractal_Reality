import torch
import torch.nn as nn
import numpy as np

class SynestheticSynthesizer(SensoryPort):
    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(1000, embedding_dim)  # assuming 1000 possible words
        self.fc1 = nn.Linear(embedding_dim + 128, hidden_dim)  # assuming 128 features in images
        self.fc2 = nn.Linear(hidden_dim, embedding_dim)

    def forward(self, text, image, sound):
        # Convert inputs to tensors
        text = torch.tensor(text, dtype=torch.long)
        image = torch.tensor(image, dtype=torch.long)
        sound = torch.tensor(sound, dtype=torch.long)

        # Embed text and image
        text_embedding = self.embedding(text)
        image_embedding = nn.Conv1d(3, 64, kernel_size=3)(image)  # assuming RGB images
        image_embedding = nn.ReLU()(image_embedding)
        image_embedding = self.embedding(image_embedding)

        # Concatenate and feed into network
        x = torch.cat((text_embedding, image_embedding), dim=1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)

        # Convert output to unified representation
        unified_embedding = torch.cat((x, sound), dim=1)

        return unified_embedding

if __name__ == '__main__':
    synthesizer = SynestheticSynthesizer(embedding_dim=64, hidden_dim=128)
    print(synthesizer)