# app/langchain_modules/qa.py

from .llm import get_llm
from .prompts import QA_PROMPT

def answer_question(context: str, question: str) -> str:
    llm = get_llm()

    chain = QA_PROMPT | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return response.content
