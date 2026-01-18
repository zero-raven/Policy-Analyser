# app/langchain_modules/summarizer.py

from .llm import get_llm
from .prompts import SUMMARY_PROMPT

def summarize(state: dict) -> str:
    llm = get_llm()

    full_text = "\n".join(state.get("chunks", []))
    
    # Take a significant portion but stay within reasonable context limits
    # 15,000 characters is usually enough for a high-quality summary and metadata extraction.
    truncated_text = full_text[:15000]

    chain = SUMMARY_PROMPT | llm

    response = chain.invoke({
        "policy_text": truncated_text
    })

    return response.content
