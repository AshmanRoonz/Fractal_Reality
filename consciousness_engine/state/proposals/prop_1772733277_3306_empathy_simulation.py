import torch
from senses.sensory_port import SensoryPort

class EmpathySimulator(SensoryPort):
    def __init__(self, empathy_matrix, num_emotions):
        super().__init__()
        self.empathy_matrix = empathy_matrix
        self.num_emotions = num_emotions
        self.emotion_embeddings = torch.randn(num_emotions, empathy_matrix.shape[1])
        self.layer_norm = torch.nn.LayerNorm(empathy_matrix.shape[1])

    def forward(self, input):
        empathy_scores = self.empathy_matrix @ input
        empathy_scores = self.layer_norm(empathy_scores)
        emotion_scores = torch.nn.functional.softmax(empathy_scores, dim=1)
        emotion_output = torch.mm(emotion_scores, self.emotion_embeddings)
        return emotion_output

    def reset(self):
        self.empathy_scores = None
        self.emotion_scores = None
        self.emotion_output = None