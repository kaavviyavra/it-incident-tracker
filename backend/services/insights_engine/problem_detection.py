import pandas as pd
from collections import Counter
import logging
from services.local_ai import cluster_similar_descriptions

logger = logging.getLogger(__name__)

# SAFE GUARDS: Prevent exponential cosine similarity calculation on lakh datasets.
MAX_TOTAL_CLUSTERING_ROWS = 1000
MAX_REPEAT_POOL = 300

def detect_recurring_problems(df: pd.DataFrame, desc_col: str, priority_col: str, sla_col: str) -> list:
    """
    Synthesizes semantic local AI clustering and frequency analytics to 
    detect emerging high-risk problem vectors safely.
    """
    candidates = []
    if not desc_col or desc_col not in df.columns or len(df) == 0:
        return candidates

    try:
        # 1. Fast Sanitization & Hashing Layer (O(N))
        cleaned = df[desc_col].astype(str).str.strip()
        unique_patterns = cleaned.value_counts()

        # 2. Subset to target rich repetitive items only for analysis
        # Takes max 300 unique sentences that actually repeat, preventing memory flooding
        repeat_patterns = unique_patterns[unique_patterns > 1].head(MAX_REPEAT_POOL)
        sentences_to_analyze = repeat_patterns.index.tolist()

        # Safety gate: if no repeats, just fallback safely
        if not sentences_to_analyze:
            return candidates

        # 3. Local AI Vector Cluster Layer
        # Limits calculation array to perfectly safe dimension bounds
        logger.info(f"Invoking local AI semantic grouping on {len(sentences_to_analyze)} core patterns.")
        semantic_clusters = cluster_similar_descriptions(sentences_to_analyze)

        # 4. Aggregate and format found clusters for display
        for idx, cluster in enumerate(semantic_clusters[:6]):
            # Compute combined frequency across the cluster siblings
            cluster_ticket_mask = cleaned.isin(cluster)
            matching_tickets = df[cluster_ticket_mask]
            
            total_frequency = len(matching_tickets)
            
            # Elect the most prevalent phrasing as canonical title
            canonical_title = cluster[0].capitalize()

            p_val = "Medium"
            if priority_col and priority_col in df.columns and len(matching_tickets) > 0:
                p_val = str(matching_tickets[priority_col].mode().iloc[0] if not matching_tickets[priority_col].mode().empty else "Medium")

            sla_breached = False
            if sla_col and sla_col in df.columns:
                sla_breached = any(matching_tickets[sla_col].astype(str).str.lower().isin(['true', 'yes', 'y', '1']))

            candidates.append({
                "id": f"PROB-AI-{100 + idx}",
                "type": "AI-Clustered Problem Node" if len(cluster) > 1 else "Recurring Incident Pattern",
                "description": canonical_title,
                "frequency": int(total_frequency),
                "impacted_priority": p_val,
                "sla_status": "Breached" if sla_breached else "Within SLA",
                "sub_variants_count": len(cluster)
            })

    except Exception as e:
        logger.error(f"Problem analysis bypass triggered: {str(e)}")
        pass
        
    return sorted(candidates, key=lambda x: x['frequency'], reverse=True)

