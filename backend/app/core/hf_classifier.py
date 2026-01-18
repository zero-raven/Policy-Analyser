# app/core/hf_classifier.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configuration (Ported from backend_fastapi.py)
AVAILABLE_MODELS = {
    "bert": "Hacktrix-121/bert-base-uncased-opp115-multilabel",
    "deberta": "Hacktrix-121/deberta-v3-base-opp115-multilabel",
    "deberta-v2": "Hacktrix-121/deberta-v3-base-opp115-multilabel-v2"
}
DEFAULT_MODEL = "deberta-v2"

LABELS = [
    "First Party Collection/Use", "Third Party Sharing/Collection", "User Choice/Control", 
    "User Access, Edit & Deletion", "Data Retention", "Data Security", "Policy Change", 
    "Do Not Track", "International & Specific Audiences", "Miscellaneous and Other", "Contact Information", 
    "User Choices/Consent Mechanisms"
]

DEFAULT_OPP115_RISK = {
    0: "medium", 1: "high", 2: "medium", 3: "low", 4: "high", 
    5: "low", 6: "medium", 7: "high", 8: "medium", 9: "medium", 
    10: "low", 11: "low",
}

THRESHOLDS = {
    0: 0.30, 1: 0.35, 2: 0.25, 3: 0.40, 4: 0.38, 
    5: 0.40, 6: 0.38, 7: 0.25, 8: 0.35, 9: 0.30, 
    10: 0.35, 11: 0.40
}
THRESHOLD = 0.4

# Cache
model_cache = {}
tokenizer_cache = {}

def get_model_and_tokenizer(model_key: str):
    if model_key not in AVAILABLE_MODELS:
        model_key = DEFAULT_MODEL
    if model_key not in model_cache:
        model_name = AVAILABLE_MODELS[model_key]
        print(f"Loading model: {model_name}")
        model_cache[model_key] = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer_cache[model_key] = AutoTokenizer.from_pretrained(model_name)
    return model_cache[model_key], tokenizer_cache[model_key]

def get_risks(label_indices):
    return [DEFAULT_OPP115_RISK.get(i, "medium") for i in label_indices]

def risk_summary(risks):
    from collections import Counter
    counts = Counter(risks)
    total = sum(counts.values())
    return {lvl: round(100*counts.get(lvl,0)/total, 1) if total else 0 for lvl in ["high","medium","low"]}

def aggregate_results(chunk_results):
    if not chunk_results:
        return {"labels": [], "scores": [], "risks": [], "risk_percentage": {}, "relevant_chunks": {}}

    aggregated_scores = [0.0] * len(LABELS)
    # Track which chunk text produced the max score for each label
    best_chunks = [""] * len(LABELS)
    
    for result in chunk_results:
        scores = result["scores"]
        chunk_text = result.get("chunk", "")
        
        for i, score in enumerate(scores):
            # Max Pooling
            if score > aggregated_scores[i]:
                aggregated_scores[i] = score
                best_chunks[i] = chunk_text
    
    final_labels = []
    final_risks = []
    final_evidence = {}
    
    for i, avg_score in enumerate(aggregated_scores):
        if avg_score > THRESHOLDS.get(i, THRESHOLD):
            label = LABELS[i]
            final_labels.append(label)
            final_risks.append(DEFAULT_OPP115_RISK[i])
            final_evidence[label] = best_chunks[i]
            
    return {
        "labels": final_labels,
        "scores": aggregated_scores,
        "risks": final_risks,
        "risk_percentage": risk_summary(final_risks),
        "relevant_chunks": final_evidence
    }

def classify_chunks(chunks: list, model_name: str = "deberta-v2") -> dict:
    print(f"DEBUG: classify_chunks receiving {len(chunks)} chunks using model {model_name}")
    current_model, current_tokenizer = get_model_and_tokenizer(model_name)
    chunk_results = []
    
    # Simple sequential inference
    for i, chunk in enumerate(chunks):
        preview = chunk[:50].replace('\n', ' ')
        print(f"DEBUG: Processing chunk {i+1}/{len(chunks)}: '{preview}...'")
        inputs = current_tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = current_model(**inputs).logits
            scores = torch.sigmoid(logits).squeeze().cpu().numpy().tolist()
            # Store chunk text with scores for evidence tracking
            chunk_results.append({"scores": scores, "chunk": chunk})
            
    return aggregate_results(chunk_results)
