from sklearn.metrics.pairwise import cosine_similarity
from .embeddings import get_embedding_model

SIMILARITY_THRESHOLD = 0.75

def cluster_similar_descriptions(descriptions):
    """
    Groups semantically similar incident descriptions.
    """

    if not descriptions:
        return []

    model = get_embedding_model()

    embeddings = model.encode(descriptions)

    similarity_matrix = cosine_similarity(embeddings)

    visited = set()
    clusters = []

    for i in range(len(descriptions)):

        if i in visited:
            continue

        cluster = [descriptions[i]]
        visited.add(i)

        for j in range(i + 1, len(descriptions)):

            if j in visited:
                continue

            similarity_score = similarity_matrix[i][j]

            if similarity_score >= SIMILARITY_THRESHOLD:
                cluster.append(descriptions[j])
                visited.add(j)

        clusters.append(cluster)

    return clusters
