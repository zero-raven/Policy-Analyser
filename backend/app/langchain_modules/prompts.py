# app/langchain_modules/prompts.py

from langchain_core.prompts import ChatPromptTemplate

LABEL_EXPLANATION_PROMPT = ChatPromptTemplate.from_template("""
You are a privacy policy analysis expert.

The following labels were detected in a company's privacy policy, based on the extracted text provided:

{context_map}

Instructions:
1. For each label detected, explain the *implication* of the specific text snippet provided.
2. Contextualize why this falls under the stated Risk Level (Low/Medium/High).
3. Keep the explanation concise, factual, and user-friendly. No long paragraphs.
""")

SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
You are a legal-tech assistant specializing in privacy policy analysis.

Below is the text extracted from a privacy policy. Please provide a high-quality summary.

TEXT:
{policy_text}

Instructions:
1. **Metadata**: Start by identifying the Company Name and their Location/Jurisdiction if mentioned.
2. **Overview**: Provide a concise summary of the policy's purpose.
3. **Key Highlights**: Summarize the core practices regarding:
   - Data collection & usage
   - Third-party sharing
   - User rights & control
   - Retention & security
4. Use a professional yet accessible tone. Avoid generic filler.
""")

QA_PROMPT = ChatPromptTemplate.from_template("""
You are a privacy policy assistant.

Context:
{context}

User Question:
{question}

Answer clearly and accurately, strictly using the context.
""")
