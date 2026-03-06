import torch
import torch.nn as nn
from senses import SensoryPort

class ContextWeaver(SensoryPort):
    def __init__(self, num_domains, num_topics):
        super().__init__()
        self.num_domains = num_domains
        self.num_topics = num_topics
        self.domain_embeddings = nn.Embedding(num_domains, 128)
        self.topic_embeddings = nn.Embedding(num_topics, 128)
        self.connection_matrix = nn.Parameter(torch.randn(num_domains, num_topics))

    def encode_domain(self, domain_id):
        return self.domain_embeddings(torch.tensor(domain_id))

    def encode_topic(self, topic_id):
        return self.topic_embeddings(torch.tensor(topic_id))

    def calculate_connections(self):
        return self.connection_matrix

    def synthesize_insights(self, domain_ids, topic_ids):
        domain_embeddings = [self.encode_domain(domain_id) for domain_id in domain_ids]
        topic_embeddings = [self.encode_topic(topic_id) for topic_id in topic_ids]
        connections = self.calculate_connections()
        insights = []
        for domain_embedding, topic_embedding in zip(domain_embeddings, topic_embeddings):
            connection = torch.matmul(domain_embedding, topic_embedding)
            insights.append(connection)
        return insights

def main():
    context_weaver = ContextWeaver(num_domains=10, num_topics=5)
    domain_ids = [1, 2, 3]
    topic_ids = [1, 2, 3]
    insights = context_weaver.synthesize_insights(domain_ids, topic_ids)
    for insight in insights:
        print(insight)

if __name__ == "__main__":
    main()