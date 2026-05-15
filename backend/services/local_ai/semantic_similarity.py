from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
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

def classify_texts_zero_shot(texts, candidate_labels):
    """
    Classifies a list of texts into candidate labels using semantic similarity.
    Runs locally and is extremely fast.
    """
    if not texts or not candidate_labels:
        return []
        
    model = get_embedding_model()
    
    # Embed labels and texts
    label_embeddings = model.encode(candidate_labels)
    text_embeddings = model.encode(texts)
    
    # Calculate cosine similarity matrix
    similarity_matrix = cosine_similarity(text_embeddings, label_embeddings)
    
    # Find best matching label index for each text
    best_indices = np.argmax(similarity_matrix, axis=1)
    
    return [candidate_labels[idx] for idx in best_indices]

def get_diverse_samples(texts, count=5):
    """
    Clusters a list of text strings semantically and returns up to `count`
    highly diverse/distinct representatives. This ensures prompts get 
    different variations rather than 5 duplicates of the same sentence.
    """
    # Filter out empty and strip strings, while preserving order
    cleaned_texts = list(dict.fromkeys([str(t).strip() for t in texts if str(t).strip()]))
    if not cleaned_texts:
        return []
    if len(cleaned_texts) <= count:
        return cleaned_texts
        
    # Use existing local clustering (takes top 50 items for performance in routing)
    target_pool = cleaned_texts[:50]
    clusters = cluster_similar_descriptions(target_pool)
    
    diverse_set = []
    # Pick the main item from each distinct cluster
    for cluster in clusters:
        if cluster:
            diverse_set.append(cluster[0])
            if len(diverse_set) >= count:
                break
                
    # Fallback fill up to requested count if we had very few clusters
    if len(diverse_set) < count:
        for item in cleaned_texts:
            if item not in diverse_set:
                diverse_set.append(item)
                if len(diverse_set) >= count:
                    break
                    
    return diverse_set

