import torch
import torch.nn as nn
import torch.nn.functional as F

class PatternWeaver(nn.Module):
    def __init__(self, knowledge_graph, pattern_size=10, relation_size=5):
        super(PatternWeaver, self).__init__()
        self.knowledge_graph = knowledge_graph
        self.pattern_size = pattern_size
        self.relation_size = relation_size
        self.embedding = nn.Embedding(len(knowledge_graph), 128)
        self.linear = nn.Linear(128, relation_size)

    def forward(self, context):
        context_embedding = self.embedding(context)
        pattern = F.relu(self.linear(context_embedding))
        return pattern

class PatternWeaverSensoryPort(nn.Module):
    def __init__(self, knowledge_graph):
        super(PatternWeaverSensoryPort, self).__init__()
        self.pattern_weaver = PatternWeaver(knowledge_graph)

    def get_pattern(self, context):
        return self.pattern_weaver(context)

def test_pattern_weaver():
    knowledge_graph = [1, 2, 3]
    pattern_weaver = PatternWeaverSensoryPort(knowledge_graph)
    context = torch.tensor([1, 2, 3])
    pattern = pattern_weaver.get_pattern(context)
    print(pattern)

if __name__ == "__main__":
    test_pattern_weaver()