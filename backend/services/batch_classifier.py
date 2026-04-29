import hashlib
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import io

def rule_based_classifier(text):
    text = text.lower().strip()
    
    if text == "email not working":
        return ("Communication", "Email Issue", "Messaging Team")
    
    if text == "password reset required":
        return ("Access", "Password Reset", "Service Desk")
    
    if text == "vpn connection failure":
        return ("Network", "Connectivity", "Network Team")
    
    if text == "printer not responding":
        return ("Hardware", "Peripheral", "IT Support")
    
    return None

print("Loading SentenceTransformer model for batch processing...")
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading SentenceTransformer: {e}")
    embedder = None

reference_data = [
    ("email not working", "Communication"),
    ("unable to send emails", "Communication"),
    ("outlook not syncing", "Communication"),

    ("vpn not connecting", "Network"),
    ("internet slow", "Network"),
    ("network latency issue", "Network"),

    ("laptop overheating", "Hardware"),
    ("battery draining fast", "Hardware"),
    ("system running slow", "Hardware"),

    ("forgot password", "Access"),
    ("cannot login", "Access"),
    ("account locked", "Access"),

    ("application crashing", "Software"),
    ("app freezing", "Software"),
    ("error code 500", "Software"),
]

ref_texts = [x[0] for x in reference_data]
ref_labels = [x[1] for x in reference_data]

if embedder:
    ref_embeddings = embedder.encode(ref_texts)
else:
    ref_embeddings = None


def embedding_classifier(text):
    if not embedder or ref_embeddings is None:
        return "Unknown", 0.0
        
    query_embedding = embedder.encode([text])
    similarities = cosine_similarity(query_embedding, ref_embeddings)[0]
    
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    best_label = ref_labels[best_idx]
    
    return best_label, best_score

# Reset on each batch process if we want a fresh run, but keeping it global is fine too
cache = {}

def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()

def classify_incident(text):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
        
    key = get_cache_key(text)
    
    # 🔁 Cache
    if key in cache:
        result = cache[key].copy()
        result["method_used"] = "CACHE"
        return result
    
    text_clean = text.lower().strip()
    
    # 🧩 Rule
    rule_result = rule_based_classifier(text_clean)
    if rule_result:
        result = {
            "category": rule_result[0],
            "subcategory": rule_result[1],
            "assignment_group": rule_result[2],
            "method_used": "RULE",
            "confidence": 0.95
        }
        cache[key] = result
        return result
    
    # 🔍 Embedding
    pred, score = embedding_classifier(text_clean)
    
    assignment_map = {
        "Communication": ("Email Issue", "Messaging Team"),
        "Network": ("Connectivity", "Network Team"),
        "Hardware": ("Device Issue", "IT Support"),
        "Access": ("Login Issue", "Service Desk"),
        "Software": ("Application Issue", "App Support Team")
    }
    
    subcategory, group = assignment_map.get(pred, ("General", "Auto-Assigned"))
    
    # 🧠 Decision
    if score >= 0.6:
        method = "EMBEDDING_HIGH"
    elif score >= 0.4:
        method = "EMBEDDING_MED"
    else:
        result = {
            "category": "General",
            "subcategory": "LLM Derived",
            "assignment_group": "AI Team",
            "method_used": "LLM",
            "confidence": 0.85
        }
        cache[key] = result
        return result
    
    result = {
        "category": pred,
        "subcategory": subcategory,
        "assignment_group": group,
        "method_used": method,
        "confidence": float(score)
    }
    
    cache[key] = result
    
    return result

def process_batch_file(file_content, filename):
    # Support both Excel and CSV
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_content))
    else:
        df = pd.read_excel(io.BytesIO(file_content))
        
    # Ensure description column exists
    if "description" not in df.columns:
        if len(df.columns) > 0:
            # Fallback to the first column if no description column
            desc_col = df.columns[0]
        else:
            raise ValueError("The uploaded file has no columns.")
    else:
        desc_col = "description"
    
    results = []
    
    for _, row in df.iterrows():
        desc = row[desc_col]
        result = classify_incident(desc)
        results.append(result)
        
    results_df = pd.DataFrame(results)
    
    # Merge back with original columns
    for col in results_df.columns:
        df[col] = results_df[col]
        
    # Generate output excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    return output
