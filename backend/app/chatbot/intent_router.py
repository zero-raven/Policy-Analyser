from app.langchain_modules.llm import get_llm

INTENT_PROMPT = """
Classify the user's intent into ONE of the following categories:

- RAG_QUESTION: Questions about privacy policy, data collection, user rights, terms of service, cookies, tracking, third parties, security, retention, or any privacy-related topic
- INSTRUCTION: Questions about how to use this tool, what this project does, or technical help
- OFF_TOPIC: Unrelated topics like weather, jokes, poems, general knowledge

User message: {message}

Think carefully: If the question could be about privacy policies or data practices, classify it as RAG_QUESTION.

Respond with ONLY ONE of these exact words: RAG_QUESTION, INSTRUCTION, or OFF_TOPIC
"""

def detect_intent(message: str) -> str:
    """Detect user intent with keyword fallback for reliability"""
    message_lower = message.lower()
    
    # Quick keyword-based detection for common cases
    rag_keywords = [
        'data', 'privacy', 'collect', 'share', 'policy', 'information', 
        'personal', 'cookie', 'track', 'third party', 'retention', 'security',
        'rights', 'delete', 'access', 'consent', 'gdpr', 'ccpa', 'what does',
        'how does', 'why does', 'can they', 'do they', 'is my', 'are my'
    ]
    
    instruction_keywords = ['how to use', 'what is this', 'what does this tool', 'help me']
    
    # Check for obvious RAG questions
    if any(keyword in message_lower for keyword in rag_keywords):
        return "RAG_QUESTION"
    
    # Check for instruction questions
    if any(keyword in message_lower for keyword in instruction_keywords):
        return "INSTRUCTION"
    
    # Fall back to LLM for ambiguous cases
    try:
        llm = get_llm()
        response = llm.invoke(INTENT_PROMPT.format(message=message))
        intent = response.content.strip().upper()
        
        # Normalize response
        if "RAG" in intent or "QUESTION" in intent:
            return "RAG_QUESTION"
        elif "INSTRUCTION" in intent:
            return "INSTRUCTION"
        elif "OFF" in intent or "TOPIC" in intent:
            return "OFF_TOPIC"
        else:
            # Default to RAG if unclear
            return "RAG_QUESTION"
    except Exception as e:
        print(f"Intent detection error: {e}")
        # Default to RAG on error
        return "RAG_QUESTION"
