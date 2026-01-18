PROJECT_DESCRIPTION = """
This project analyzes website privacy policies in real-time.
It extracts policy text, classifies privacy risks using AI,
and explains them in simple language for users.
"""

def handle_instruction_query(message: str) -> str:
    return f"""
{PROJECT_DESCRIPTION}

You asked:
"{message}"

You can:
• Ask questions about the privacy policy
• Understand privacy risks
• See explanations in simple terms
"""
