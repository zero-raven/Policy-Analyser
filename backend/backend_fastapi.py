from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI()
MODEL_NAME = "Hacktrix-121/bert-base-uncased-opp115-multilabel"
LABELS = [
    "First Party Collection/Use", "Third Party Sharing/Collection", "User Choice/Control", 
    "User Access, Edit & Deletion", "Data Retention", "Data Security", "Policy Change", 
    "Do Not Track", "International & Specific Audiences", "Miscellaneous and Other", "Contact Information", 
    "User Choices/Consent Mechanisms"
]
THRESHOLD = 0.5

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

class TextIn(BaseModel):
    text: str

class PredictionOut(BaseModel):
    labels: list
    scores: list

@app.post("/predict", response_model=PredictionOut)
async def predict(data: TextIn):
    inputs = tokenizer(data.text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        scores = torch.sigmoid(logits).squeeze().cpu().numpy().tolist()
        # Take all indices with probability above threshold as positive labels
        predicted_labels = [LABELS[i] for i, score in enumerate(scores) if score > THRESHOLD]
    return {"labels": predicted_labels, "scores": scores}
