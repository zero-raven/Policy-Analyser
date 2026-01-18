# app/langgraph/nodes.py

from app.core.web_scraper import scrape_policy
from app.core.chunk_processor import chunk_text
from app.core.hf_classifier import classify_chunks

from app.langchain_modules.explainer import explain
from app.langchain_modules.summarizer import summarize

from app.chatbot.intent_router import detect_intent
from app.chatbot.rag_handler import handle_rag_query
from app.chatbot.instruction import handle_instruction_query
from app.chatbot.guardrails import handle_off_topic


def scrape_node(state: dict) -> dict:
    text = scrape_policy(state["url"])
    return {**state, "raw_text": text}


def chunk_node(state: dict) -> dict:
    chunks = chunk_text(state["raw_text"])
    return {**state, "chunks": chunks}


def classify_node(state: dict) -> dict:
    result = classify_chunks(state["chunks"])
    return {**state, **result}


def explain_node(state: dict) -> dict:
    explanation = explain(state)
    return {**state, "explanation": explanation}


def summary_node(state: dict) -> dict:
    summary = summarize(state)
    return {**state, "summary": summary}

from app.chatbot.response_builder import build_response

def intent_node(state: dict) -> dict:
    intent = detect_intent(state["user_message"])
    return {"intent": intent}

def rag_node(state: dict) -> dict:
    # Use 'chunks' if available (provided via context), otherwise empty list
    chunks = state.get("chunks", [])
    answer = handle_rag_query(state["user_message"], chunks)
    return {"answer": answer, "response_type": "RAG"}

def instruction_node(state: dict) -> dict:
    answer = handle_instruction_query(state["user_message"])
    return {"answer": answer, "response_type": "INSTRUCTION"}

def guardrail_node(state: dict) -> dict:
    answer = handle_off_topic(state["user_message"])
    return {"answer": answer, "response_type": "GUARDRAIL"}

def chat_response_node(state: dict) -> dict:
    # Build final response dict
    final_json = build_response(
        answer=state.get("answer"),
        response_type=state.get("response_type"),
        sources=["Policy Text"] if state.get("response_type") == "RAG" else [],
        risks={} # Simplify for now, or pass from state
    )
    return {"chat_response": final_json}