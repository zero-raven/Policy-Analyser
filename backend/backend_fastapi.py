from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv
import os
from fastapi import HTTPException


from app.langchain_modules.summarizer import summarize
from app.langgraph.graph import policy_graph
from app.core.hf_classifier import AVAILABLE_MODELS, DEFAULT_MODEL, classify_chunks
from app.core.chunk_processor import chunk_text

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextIn(BaseModel):
    text: str
    model: str = DEFAULT_MODEL

class URLInput(BaseModel):
    url: str
    model: str = DEFAULT_MODEL

@app.post("/predict")
async def predict(data: TextIn):
    # This endpoint is for manual text paste (legacy/simple mode)
    # It does NOT use LangGraph usually, or we can wrap it.
    # To correspond with "Paste Text" mode which expects breakdown:
    
    # 1. Chunk
    chunks = chunk_text(data.text)
    
    # 2. Classify
    # classify_chunks returns {labels, scores, risks, risk_percentage}
    result = classify_chunks(chunks, model_name=data.model)
    
    # 3. Return (frontend expects: labels, scores, risks, risk_percentage, model_used)
    result["model_used"] = AVAILABLE_MODELS.get(data.model, data.model)
    result["chunks"] = chunks
    return result

@app.post("/analyze-url")
async def analyze_url(data: URLInput):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] [INFO] 🔍 Analyzing URL: {data.url}")
    
    # Invoke LangGraph
    # We pass 'url' as initial state. The graph nodes will populate the rest.
    try:
        final_state = policy_graph.invoke({"url": data.url})
    except Exception as e:
        print(f"[{timestamp}] [ERROR] Graph execution failed: {e}")
        return {"error": str(e)}

    # Map state to response
    results = {
        "labels": final_state.get("labels", []),
        "scores": final_state.get("scores", []),
        "risk_levels": final_state.get("risks", []),      # Map "risks" from state to "risk_levels" in response if needed,                                                           # but consistency suggests we just pass it through.
        "risks": final_state.get("risks", []),            # Correctly map the key from hf_classifier
        "risk_percentage": final_state.get("risk_percentage", {}), 
        "explanation": final_state.get("explanation", ""),
        "summary": final_state.get("summary", ""),
        "chunk_count": len(final_state.get("chunks", [])),
        "chunks": final_state.get("chunks", []),
        "url": final_state.get("url", "")
    }

    print(f"[{timestamp}] [INFO] 📊 Analysis Complete!")
    return results

@app.get("/models")
async def get_available_models():
    return {"available_models": list(AVAILABLE_MODELS.keys()), "default_model": DEFAULT_MODEL}

# --- Chatbot Integration ---
from app.langgraph.graph import policy_graph

class ChatRequest(BaseModel):
    message: str
    chunks: list[str] = []
    # Optional: session_id, risks, etc.

@app.post("/chat")
async def chat_endpoint(data: ChatRequest):
    print(f"DEBUG: Chat request: {data.message}")
    
    # Invoke Unified Policy Graph
    inputs = {
        "user_message": data.message,
        "chunks": data.chunks
    }
    
    try:
        final_state = policy_graph.invoke(inputs)
        return final_state.get("chat_response", {}) 
    except Exception as e:
        print(f"ERROR: Chatbot failed: {e}")
        return {"error": str(e)}


@app.post("/analyze-text")
async def analyze_text(req: dict):
    text = req.get("text")
    model = req.get("model", "bert")

    if not text or len(text) < 20:
        raise HTTPException(status_code=400, detail="Text too short")

    # SAME pipeline as /predict (do NOT call the endpoint)
    chunks = chunk_text(text)

    # IMPORTANT: match classify_chunks return signature
    result = classify_chunks(chunks, model)

    # classify_chunks may return dict OR tuple depending on your implementation
    if isinstance(result, dict):
        labels = result.get("labels", [])
        scores = result.get("scores", [])
        evidence = result.get("evidence", [])
    else:
        labels, scores, evidence = result

    # LLM-powered summary (safe-guarded)
    try:
        summary = summarize(chunks)
    except Exception as e:
        print("Summary error:", e)
        summary = None

    return {
        "labels": labels,
        "scores": scores,
        "evidence": evidence,
        "chunks": chunks,
        "summary": summary,
        "model_used": model
    }
