# app/langgraph/graph.py

from langgraph.graph import StateGraph, END

from .state import PolicyState
from .nodes import (
    scrape_node,
    chunk_node,
    classify_node,
    explain_node,
    summary_node,
    intent_node,
    rag_node,
    instruction_node,
    guardrail_node,
    chat_response_node,
)

# --- Routers ---

def master_router(state: PolicyState):
    """
    Decides whether to run the Analysis pipeline or Chatbot pipeline
    based on input keys.
    """
    if state.get("url"):
        return "analysis"
    elif state.get("user_message"):
        return "chat"
    else:
        return "end" # Invalid input

def chat_router(state: PolicyState):
    intent = state.get("intent")
    if intent == "INSTRUCTION":
        return "instruction"
    elif intent == "RAG_QUESTION":
        return "rag"
    else:
        return "guardrail"


def build_policy_graph():
    graph = StateGraph(PolicyState)

    # --- Analysis Nodes ---
    graph.add_node("scrape", scrape_node)
    graph.add_node("chunk", chunk_node)
    graph.add_node("classify", classify_node)
    graph.add_node("explain", explain_node)
    graph.add_node("summary", summary_node)

    # --- Chatbot Nodes ---
    graph.add_node("detect_intent", intent_node)
    graph.add_node("rag", rag_node)
    graph.add_node("instruction", instruction_node)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("format_chat", chat_response_node)

    # --- Entry Point (Virtual) ---
    # We use a dummy starting node or just conditional entry.
    # LangGraph requires a specific start node. 
    # Let's use a "router" node or just set entry point conditionally?
    # Actually, StateGraph.set_conditional_entry_point is what we want.
    
    graph.set_conditional_entry_point(
        master_router,
        {
            "analysis": "scrape",
            "chat": "detect_intent",
            "end": END
        }
    )

    # --- Analysis Flow ---
    graph.add_edge("scrape", "chunk")
    graph.add_edge("chunk", "classify")
    graph.add_edge("classify", "explain")
    graph.add_edge("explain", "summary")
    graph.add_edge("summary", END)

    # --- Chatbot Flow ---
    graph.add_conditional_edges(
        "detect_intent",
        chat_router,
        {
            "instruction": "instruction",
            "rag": "rag",
            "guardrail": "guardrail"
        }
    )

    graph.add_edge("rag", "format_chat")
    graph.add_edge("instruction", "format_chat")
    graph.add_edge("guardrail", "format_chat")
    graph.add_edge("format_chat", END)

    return graph.compile()


policy_graph = build_policy_graph()
