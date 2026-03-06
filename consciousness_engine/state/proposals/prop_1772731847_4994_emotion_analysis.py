"""
Emotion Analysis Module for textual data.
This module uses Natural Language Processing (NLP) techniques to analyze text and determine the emotions expressed.
"""

import circumpunct
import senses
import mind
import numpy as np
import torch
from torch.nn import TextCNN

class EmotionAnalysisPort(senses.SensoryPort):
    """
    SensoryPort subclass for emotion analysis of text.
    """

    def __init__(self, model_path, vocab_path, embedding_dim, filter_sizes, num_filters, num_classes):
        super().__init__()

        self.model = TextCNN(vocab_size=len(self.load_vocab(vocab_path)),
                              embedding_dim=embedding_dim,
                              num_filter_sizes=filter_sizes,
                              num_filters=num_filters,
                              num_classes=num_classes)

        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def load_vocab(self, file_path):
        """
        Loads the pre-trained vocabulary from a file.
        """
        vocab = {}
        with open(file_path, 'r') as f:
            for line in f:
                word, _ = line.split()
                vocab[word] = len(vocab)
        return vocab

    def analyze_emotion(self, text):
        """
        Analyzes the emotional context of the provided text.

        Args:
            text (str): The text to be analyzed.

        Returns:
            np.ndarray: An array representing the probability of the different emotions in the text.
        """
        tokens = self.tokenize(text)
        tensor_tokens = torch.tensor([self.vocab[token] for token in tokens])
        with torch.no_grad():
            outputs = self.model(tensor_tokens.unsqueeze(0))
        probabilities = outputs.squeeze(0).softmax(dim=1)
        return probabilities

    def tokenize(self, text):
        """
        Tokenizes the provided text.

        Args:
            text (str): The text to be tokenized.

        Returns:
            list: A list of tokens.
        """
        return circumpunct.tokenize(text)