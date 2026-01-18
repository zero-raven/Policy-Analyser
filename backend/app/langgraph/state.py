# app/langgraph/state.py

from typing import TypedDict, List, Dict

class PolicyState(TypedDict):
    # Analysis Fields
    url: str
    raw_text: str
    chunks: List[str]
    labels: List[str]
    scores: List[Dict]
    risk_levels: List[str]
    relevant_chunks: Dict
    explanation: str
    summary: str

    # Chatbot Fields
    user_message: str
    intent: str
    answer: str
    response_type: str
    chat_response: Dict  # The final JSON response for chat
