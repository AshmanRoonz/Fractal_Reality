import torch
import torch.nn as nn
from torch.nn import functional as F
from torch import optim
from numpy import random
from senses import SensoryPort

class TextEmbedder(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(TextEmbedder, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)

    def forward(self, text):
        return self.embedding(text)

class ImageEmbedder(nn.Module):
    def __init__(self, num_channels, embedding_dim):
        super(ImageEmbedder, self).__init__()
        self.conv1d = nn.Conv1d(num_channels, embedding_dim, kernel_size=3)

    def forward(self, image):
        return F.relu(self.conv1d(image))

class AudioEmbedder(nn.Module):
    def __init__(self, num_channels, embedding_dim):
        super(AudioEmbedder, self).__init__()
        self.conv1d = nn.Conv1d(num_channels, embedding_dim, kernel_size=3)

    def forward(self, audio):
        return F.relu(self.conv1d(audio))

class SensorySynthesizer(SensoryPort):
    def __init__(self, text_vocab_size, image_height, audio_channels):
        super(SensorySynthesizer, self).__init__()
        self.text_embedder = TextEmbedder(text_vocab_size, 128)
        self.image_embedder = ImageEmbedder(image_channels=image_height, embedding_dim=128)
        self.audio_embedder = AudioEmbedder(audio_channels, embedding_dim=128)
        self.linear = nn.Linear(128 + 128 + 128, 128)

    def forward(self, text, image, audio):
        text_embedding = self.text_embedder(text)
        image_embedding = self.image_embedder(image)
        audio_embedding = self.audio_embedder(audio)
        combined_embedding = torch.cat((text_embedding, image_embedding, audio_embedding), dim=1)
        return F.relu(self.linear(combined_embedding))

if __name__ == "__main__":
    # Test the Sensory Synthesizer
    text = random.randint(0, 10000, size=(1,))
    image = torch.randn(3, 224, 224)
    audio = torch.randn(1, 16000)
    synthesizer = SensorySynthesizer(text_vocab_size=10000, image_height=224, audio_channels=1)
    output = synthesizer(text, image, audio)
    print(output.shape)