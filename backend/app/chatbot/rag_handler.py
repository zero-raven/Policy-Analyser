from app.langchain_modules.qa import answer_question

def handle_rag_query(question: str, chunks: list[str]) -> str:
    """Handle RAG queries with proper context from policy chunks"""
    
    if not chunks or len(chunks) == 0:
        return """I don't have any privacy policy context loaded yet. 

Please analyze a privacy policy first by:
1. Going to the main page
2. Using "Enter URL" mode to analyze a website's privacy policy
3. Then come back and ask your questions!"""
    
    # Join chunks with clear separators
    context = "\n\n---\n\n".join(chunks)
    
    # Enhance the question with context hint
    enhanced_question = f"""Based on the privacy policy provided, {question}

Please provide a clear, specific answer citing relevant parts of the policy."""
    
    return answer_question(
        context=context,
        question=enhanced_question
    )
