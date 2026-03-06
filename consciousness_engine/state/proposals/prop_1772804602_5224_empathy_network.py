import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from senses import SensoryPort

class EmotionalAnalyzer(SensoryPort):
    def __init__(self, model):
        super(EmotionalAnalyzer, self).__init__()
        self.model = model

    def analyze(self, input_text):
        # Preprocess input text
        tokens = self.model.tokenize(input_text)
        input_ids = self.model.convert_tokens_to_ids(tokens)

        # Run through the model to get the emotional analysis
        outputs = self.model(input_ids)
        scores = outputs.last_hidden_state[:, 0, :]  # Get the sentiment scores

        return scores

class EmpathyGenerator(SensoryPort):
    def __init__(self, model):
        super(EmpathyGenerator, self).__init__()
        self.model = model

    def generate_response(self, emotional_analysis):
        # Get the dominant emotion
        dominant_emotion = np.argmax(emotional_analysis)

        # Generate a response based on the dominant emotion
        response = self.model.generate_response(dominant_emotion)

        return response

class EmpathyNetwork:
    def __init__(self, model):
        self.analyzer = EmotionalAnalyzer(model)
        self.generator = EmpathyGenerator(model)

    def get_emotional_analysis(self, input_text):
        return self.analyzer.analyze(input_text)

    def get_empathetic_response(self, emotional_analysis):
        return self.generator.generate_response(emotional_analysis)

# Test the Empathy Network
if __name__ == "__main__":
    # Initialize the model
    model = nn.Sequential(
        nn.Linear(768, 128),
        nn.ReLU(),
        nn.Linear(128, 128),
        nn.ReLU(),
        nn.Linear(128, 128),
        nn.ReLU()
    )

    # Create the Empathy Network
    empathy_network = EmpathyNetwork(model)

    # Test the Empathy Network
    input_text = "I'm feeling really sad today."
    emotional_analysis = empathy_network.get_emotional_analysis(input_text)
    response = empathy_network.get_empathetic_response(emotional_analysis)
    print(response)