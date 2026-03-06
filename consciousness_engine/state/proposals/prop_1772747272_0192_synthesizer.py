import torch
import torch.nn as nn
import numpy as np

class SensoryPort(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(1000, 64)  # assuming 1000 possible words
        self.fc1 = nn.Linear(64 + 128, 128)  # assuming 128 features in images
        self.fc2 = nn.Linear(128, 64)

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

class SynestheticSynthesizer(SensoryPort):
    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim

    def forward(self, text, image, sound):
        # Call parent class's forward method
        return super().forward(text, image, sound)

if __name__ == '__main__':
    synthesizer = SynestheticSynthesizer(embedding_dim=64, hidden_dim=128)
    print(synthesizer)
    print(synthesizer.forward('hello', 'image.jpg', 'sound.wav'))