# PolicyLens Workflow Architecture

## Unified LangGraph v2.0

The new unified workflow combines both **Privacy Policy Analysis** and **Interactive Chatbot** capabilities in a single graph with intelligent routing.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT (User Request)                      │
│                 url: str | user_message: str                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Master Router  │
                  │  (Entry Point) │
                  └────────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        url provided?           user_message provided?
              │                         │
              ▼                         ▼
    ┌─────────────────┐      ┌──────────────────┐
    │ ANALYSIS FLOW   │      │  CHATBOT FLOW    │
    └─────────────────┘      └──────────────────┘
```

---

## 🔄 Analysis Flow (URL-based)

Triggered when: `input contains 'url'`

```
START
  │
  ├─► Scrape Node
  │   └─► Extract privacy policy text from URL
  │
  ├─► Chunk Node  
  │   └─► Semantic chunking (512 tokens, sentence-aware)
  │
  ├─► Classify Node
  │   └─► HF Multi-label classification (OPP-115)
  │   └─► Risk assessment (High/Medium/Low)
  │
  ├─► Explain Node
  │   └─► AI-generated explanations with evidence
  │
  ├─► Summarize Node
  │   └─► Policy summary with metadata extraction
  │
  └─► END
```

**Output:**
- `labels`: List of detected privacy categories
- `risks`: Risk levels for each category
- `scores`: Confidence scores
- `explanation`: AI-generated detailed explanation
- `summary`: Policy overview with company/jurisdiction info
- `chunks`: Text chunks (used for chatbot context)

---

## 💬 Chatbot Flow (Message-based)

Triggered when: `input contains 'user_message'`

```
START
  │
  ├─► Detect Intent Node
  │   └─► Keyword-based + LLM classification
  │   └─► Returns: RAG_QUESTION | INSTRUCTION | OFF_TOPIC
  │
  ├─► Router (based on intent)
  │   │
  │   ├─► RAG Node
  │   │   └─► Query policy chunks
  │   │   └─► Generate context-aware answer
  │   │
  │   ├─► Instruction Node
  │   │   └─► Explain tool functionality
  │   │
  │   └─► Guardrail Node
  │       └─► Reject off-topic queries
  │
  ├─► Format Response Node
  │   └─► Build standardized JSON response
  │
  └─► END
```

**Output:**
- `answer`: The chatbot's response
- `type`: Response type (RAG/INSTRUCTION/GUARDRAIL)
- `sources`: Citations (for RAG responses)
- `risks`: Relevant risk information

---

## 🔀 Master Router Logic

```python
def master_router(state: PolicyState):
    if state.get("url"):
        return "analysis"  # → Scrape Node
    elif state.get("user_message"):
        return "chat"      # → Detect Intent Node
    else:
        return "end"       # Invalid input
```

---

## 🧠 Intent Detection (Chatbot)

### Keyword-based Fast Path
```python
RAG Keywords: 
  - data, privacy, collect, share, policy, information
  - personal, cookie, track, third party, retention
  - security, rights, delete, access, consent
  - gdpr, ccpa, what does, how does, why does

Instruction Keywords:
  - how to use, what is this, what does this tool, help me
```

### LLM Fallback
- Uses Groq API for ambiguous cases
- Defaults to RAG_QUESTION when uncertain
- Normalizes responses for consistency

---

## 📊 State Management

### PolicyState (TypedDict)
```python
{
    # Analysis Fields
    "url": str,
    "raw_text": str,
    "chunks": List[str],
    "labels": List[str],
    "scores": List[Dict],
    "risk_levels": List[str],
    "relevant_chunks": Dict,
    "explanation": str,
    "summary": str,
    
    # Chatbot Fields
    "user_message": str,
    "intent": str,
    "answer": str,
    "response_type": str,
    "chat_response": Dict
}
```

---

## 🎯 Key Features

### Unified Design
- **Single Graph**: One compiled graph handles both workflows
- **Shared State**: Analysis chunks feed chatbot RAG
- **Efficient**: No duplicate components or overhead

### Smart Routing
- **Automatic**: Based on input structure
- **Fast**: Keyword-based detection for common cases
- **Fallback**: LLM for complex queries

### Context Awareness
- **Session Persistence**: Chunks stored across requests
- **RAG Integration**: Chatbot answers from actual policy
- **Evidence-based**: Responses cite specific policy sections

---

## 📈 Comparison: v1.0 vs v2.0

| Feature | v1.0 (Analysis Only) | v2.0 (Unified) |
|---------|---------------------|----------------|
| **Workflows** | 1 (Linear Analysis) | 2 (Analysis + Chat) |
| **Entry Points** | Single (Scrape) | Conditional Router |
| **LLM Calls** | 2 (Explain, Summarize) | 2-3 (+ Intent/RAG) |
| **State Fields** | 8 | 15+ |
| **User Interaction** | One-time analysis | Interactive Q&A |
| **Context Reuse** | None | Chunks → RAG |
| **Response Types** | Analysis report | Report + Chat |

---

## 🔧 Implementation Files

- **Graph**: `app/langgraph/graph.py`
- **Nodes**: `app/langgraph/nodes.py`
- **State**: `app/langgraph/state.py`
- **Chatbot Modules**: `app/chatbot/*.py`
- **Core**: `app/core/*.py`
- **LLM**: `app/langchain_modules/*.py`

---

## 🚀 Usage Examples

### Analysis
```python
result = policy_graph.invoke({"url": "https://example.com/privacy"})
# Returns: labels, risks, explanation, summary, chunks
```

### Chat  
```python
result = policy_graph.invoke({
    "user_message": "What data do they collect?",
    "chunks": [...policy_chunks...]
})
# Returns: chat_response with answer, type, sources
```

---

**Generated:** PolicyLens v2.0 - Unified Workflow Architecture
