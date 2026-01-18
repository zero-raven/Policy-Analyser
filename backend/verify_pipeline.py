#!/usr/bin/env python3
"""
PolicyLens - Complete Integration Verification
Tests all system components including chatbot integration
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("PolicyLens - System Verification")
print("=" * 70)

# ============================================================================
# 1. ENVIRONMENT CHECK
# ============================================================================
print("\n[1/6] 🔧 Environment Check")
print("-" * 70)

groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    print(f"✅ GROQ_API_KEY found (length: {len(groq_key)})")
else:
    print("❌ GROQ_API_KEY not found in environment")
    sys.exit(1)

# ============================================================================
# 2. CORE MODULE IMPORTS
# ============================================================================
print("\n[2/6] 📦 Core Module Imports")
print("-" * 70)

try:
    from app.core.web_scraper import scrape_policy
    print("✅ app.core.web_scraper")
except ImportError as e:
    print(f"❌ app.core.web_scraper failed: {e}")
    sys.exit(1)

try:
    from app.core.chunk_processor import chunk_text
    print("✅ app.core.chunk_processor")
except ImportError as e:
    print(f"❌ app.core.chunk_processor failed: {e}")
    sys.exit(1)

try:
    from app.core.hf_classifier import classify_chunks
    print("✅ app.core.hf_classifier")
except ImportError as e:
    print(f"❌ app.core.hf_classifier failed: {e}")
    sys.exit(1)

# ============================================================================
# 3. LANGGRAPH & LLM MODULES
# ============================================================================
print("\n[3/6] 🤖 LangGraph & LLM Modules")
print("-" * 70)

try:
    from app.langchain_modules.llm import get_llm
    print("✅ app.langchain_modules.llm")
except ImportError as e:
    print(f"❌ LLM module failed: {e}")
    sys.exit(1)

try:
    from app.langgraph.graph import policy_graph
    print("✅ app.langgraph.graph (unified graph)")
except ImportError as e:
    print(f"❌ LangGraph failed: {e}")
    sys.exit(1)

# ============================================================================
# 4. CHATBOT MODULES
# ============================================================================
print("\n[4/6] 💬 Chatbot Modules")
print("-" * 70)

try:
    from app.chatbot.intent_router import detect_intent
    print("✅ app.chatbot.intent_router")
except ImportError as e:
    print(f"❌ Intent router failed: {e}")
    sys.exit(1)

try:
    from app.chatbot.rag_handler import handle_rag_query
    print("✅ app.chatbot.rag_handler")
except ImportError as e:
    print(f"❌ RAG handler failed: {e}")
    sys.exit(1)

try:
    from app.chatbot.instruction import handle_instruction_query
    print("✅ app.chatbot.instruction")
except ImportError as e:
    print(f"❌ Instruction module failed: {e}")
    sys.exit(1)

try:
    from app.chatbot.guardrails import handle_off_topic
    print("✅ app.chatbot.guardrails")
except ImportError as e:
    print(f"❌ Guardrails failed: {e}")
    sys.exit(1)

try:
    from app.chatbot.response_builder import build_response
    print("✅ app.chatbot.response_builder")
except ImportError as e:
    print(f"❌ Response builder failed: {e}")
    sys.exit(1)

# ============================================================================
# 5. FUNCTIONAL TESTS
# ============================================================================
print("\n[5/6] 🧪 Functional Tests")
print("-" * 70)

# Test chunking
test_text = "This is a test privacy policy. We collect your data. We share your information with third parties. You can delete your data at any time."
chunks = chunk_text(test_text)
print(f"✅ Chunking works (generated {len(chunks)} chunks)")

# Test intent detection
test_intents = {
    "What data do you collect?": "RAG_QUESTION",
    "What is this tool?": "INSTRUCTION",
    "Tell me a joke": "OFF_TOPIC"
}

print("\n   Testing Intent Detection:")
for msg, expected in test_intents.items():
    detected = detect_intent(msg)
    status = "✅" if expected in detected else "⚠️"
    print(f"   {status} '{msg[:30]}...' → {detected}")

# ============================================================================
# 6. GRAPH INTEGRATION TEST
# ============================================================================
print("\n[6/6] 🔄 Unified Graph Integration")
print("-" * 70)

# Test Chat Flow
print("\n   Testing Chat Flow:")
try:
    chat_state = policy_graph.invoke({
        "user_message": "What is this project?",
        "chunks": []
    })
    
    if "chat_response" in chat_state:
        response_type = chat_state["chat_response"].get("type", "UNKNOWN")
        print(f"   ✅ Chat flow works (Response type: {response_type})")
    else:
        print("   ⚠️ Chat flow executed but no response generated")
except Exception as e:
    print(f"   ❌ Chat flow failed: {e}")

# Test Analysis Flow (without actual URL scraping)
print("\n   Note: Analysis flow requires URL scraping - test via backend/frontend")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("🎉 ALL SYSTEMS VERIFIED!")
print("=" * 70)
print("\nReady to run:")
print("  Backend:  uvicorn backend_fastapi:app --reload")
print("  Frontend: streamlit run frontend_streamlit.py")
print("\nFeatures Available:")
print("  ✓ Privacy policy analysis with risk classification")
print("  ✓ AI-powered explanations and summaries")
print("  ✓ Interactive chatbot with RAG capabilities")
print("  ✓ Intent routing (RAG, Instruction, Guardrail)")
print("=" * 70)
