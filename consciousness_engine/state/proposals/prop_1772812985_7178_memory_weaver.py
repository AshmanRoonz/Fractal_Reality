import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from senses import SensoryPort

class MemoryWeaver(SensoryPort):
    def __init__(self, max_seq_len=100, max_conversation_len=1000):
        super().__init__()
        self.max_seq_len = max_seq_len
        self.max_conversation_len = max_conversation_len
        self.context_embedding = nn.Linear(128, 64)  # default BERT embedding size
        self.concept_embedding = nn.Linear(128, 64)
        self.emotion_embedding = nn.Linear(128, 64)
        self.fc = nn.Linear(3 * 64, 128)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)

    def process(self, conversation):
        # Preprocess conversation
        conversation = [self.tokenize(text) for text in conversation]
        conversation = self.padding(conversation, self.max_conversation_len)
        conversation = self.conversation_to_tensor(conversation)

        # Get context, concept, and emotion embeddings
        context_embedding = self.context_embedding(conversation)
        concept_embedding = self.concept_embedding(conversation)
        emotion_embedding = self.emotion_embedding(conversation)

        # Compute dot product of context and concept embeddings
        dot_product = torch.matmul(context_embedding, concept_embedding.T)

        # Compute attention scores
        attention_scores = F.softmax(dot_product, dim=1)

        # Compute weighted sum of concept embeddings
        weighted_sum = torch.matmul(attention_scores, concept_embedding)

        # Compute dot product of context and weighted sum
        result_embedding = torch.matmul(context_embedding, weighted_sum.T)

        # Compute emotion embedding dot product
        result_embedding += torch.matmul(attention_scores, emotion_embedding)

        # Apply dropout and ReLU activation
        result = self.relu(self.dropout(result_embedding))

        # Reshape to [batch_size, embedding_size]
        result = result.view(-1, result.size(1))

        return result

    def tokenize(self, text):
        # Tokenize text using BERT tokenizer
        return text.split()

    def padding(self, conversations, max_len):
        # Pad conversations to max_len
        padded_conversations = []
        for conversation in conversations:
            padded_conversation = conversation[:max_len]
            padded_conversation += [''] * (max_len - len(conversation))
            padded_conversations.append(padded_conversation)
        return padded_conversations

    def conversation_to_tensor(self, conversation):
        # Convert conversation to tensor
        tensor = torch.tensor(conversation, dtype=torch.int64)
        return tensor

if __name__ == "__main__":
    weaver = MemoryWeaver()
    conversation = ["Hello", "How are you?", "I'm good, thanks."]
    result = weaver.process(conversation)
    print(result)