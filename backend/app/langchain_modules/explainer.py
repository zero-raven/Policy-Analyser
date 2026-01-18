# app/langchain_modules/explainer.py

from .llm import get_llm
from .prompts import LABEL_EXPLANATION_PROMPT

def explain(state: dict) -> str:
    llm = get_llm()

    labels = state.get("labels", [])
    relevant_chunks = state.get("relevant_chunks", {})
    
    # Static risk mapping for explanation context
    risk_map = {
        "First Party Collection/Use": "medium",
        "Third Party Sharing/Collection": "high",
        "User Choice/Control": "medium",
        "User Access, Edit & Deletion": "low",
        "Data Retention": "high",
        "Data Security": "low",
        "Policy Change": "medium",
        "Do Not Track": "high",
        "International & Specific Audiences": "medium",
        "Miscellaneous and Other": "medium",
        "Contact Information": "low",
        "User Choices/Consent Mechanisms": "low",
    }
    
    # improved context mapping (Label -> Risk -> Evidence Chunk)
    context_parts = []
    for label in labels:
        chunk_text = relevant_chunks.get(label, "No specific text found.")[:400].replace("\n", " ")
        risk = risk_map.get(label, "medium")
        context_parts.append(f"- **{label}** (Risk: {risk}): \"{chunk_text}...\"")
    
    context_map = "\n".join(context_parts)

    chain = LABEL_EXPLANATION_PROMPT | llm

    response = chain.invoke({
        "context_map": context_map
    })

    return response.content
