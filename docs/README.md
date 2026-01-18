# 🔐 PolicyLens - AI Privacy Policy Analyzer

An intelligent privacy policy analysis tool with **AI-powered chatbot** that helps users understand complex privacy policies through automatic classification, risk assessment, and conversational Q&A.

## 🌟 Features

### Core Analysis
- 🤖 **Multi-Model AI Classification**: BERT, DeBERTa, and DeBERTa-v2 support
- 🎯 **12 Privacy Categories**: Comprehensive OPP-115 dataset coverage
- ⚡ **Real-time Risk Assessment**: Automatic High/Medium/Low risk detection
- 📊 **Detailed Explanations**: AI-generated insights with evidence citations
- 📝 **Smart Summaries**: Extract company name, jurisdiction, and key practices

### Interactive Chatbot (NEW!)
- 💬 **RAG-Powered Q&A**: Ask questions about analyzed policies
- 🧠 **Intent Routing**: Automatic classification (RAG, Instruction, Guardrail)
- 🔍 **Context-Aware**: Uses actual policy chunks for accurate answers
- 🛡️ **Smart Guardrails**: Rejects off-topic queries gracefully

### Technology Stack
- **Backend**: FastAPI + LangGraph workflow orchestration
- **Frontend**: Streamlit with collapsible chat sidebar
- **AI Models**: Groq API (LLM) + Hugging Face Transformers (classification)
- **Architecture**: Modular, extensible, production-ready

## 📂 Project Structure

```
Priv_pol/
├── app/
│   ├── core/                    # Core processing modules
│   │   ├── web_scraper.py      # URL scraping & text extraction
│   │   ├── chunk_processor.py  # Semantic text chunking
│   │   └── hf_classifier.py    # Multi-label classification
│   │
│   ├── langchain_modules/      # LLM integration
│   │   ├── llm.py              # Groq API wrapper
│   │   ├── prompts.py          # Prompt templates
│   │   ├── explainer.py        # Risk explanation generator
│   │   ├── summarizer.py       # Policy summarization
│   │   └── qa.py               # Question-answering
│   │
│   ├── langgraph/              # Workflow orchestration
│   │   ├── graph.py            # Unified policy+chat graph
│   │   ├── nodes.py            # Graph node definitions
│   │   └── state.py            # State management
│   │
│   └── chatbot/                # Chatbot components
│       ├── intent_router.py    # Intent detection (keyword + LLM)
│       ├── rag_handler.py      # RAG query processing
│       ├── instruction.py      # Help/instruction responses
│       ├── guardrails.py       # Off-topic rejection
│       └── response_builder.py # Response formatting
│
├── backend_fastapi.py          # FastAPI REST API
├── frontend_streamlit.py       # Streamlit UI with chat
├── verify_pipeline.py          # System verification script
└── .env                        # Environment variables
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Groq API Key ([Get one here](https://console.groq.com))

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Priv_pol

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GROQ_API_KEY=your_api_key_here" > .env
```

### 3. Verify Installation

```bash
python verify_pipeline.py
```

You should see:
```
🎉 ALL SYSTEMS VERIFIED!
Features Available:
  ✓ Privacy policy analysis with risk classification
  ✓ AI-powered explanations and summaries
  ✓ Interactive chatbot with RAG capabilities
  ✓ Intent routing (RAG, Instruction, Guardrail)
```

### 4. Run the Application

**Start Backend (Terminal 1):**
```bash
uvicorn backend_fastapi:app --reload
```

**Start Frontend (Terminal 2):**
```bash
streamlit run frontend_streamlit.py
```

**Access:**
- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 💡 Usage

### Web Interface

1. **Choose Input Mode:**
   - **Enter URL**: Analyze any website's privacy policy
   - **Paste Text**: Classify text directly

2. **Analyze Policy:**
   - Enter URL (e.g., `https://google.com/policies/privacy`)
   - Click "🔍 Analyze URL"
   - View results: categories, risks, explanation, summary

3. **Chat with Policy:**
   - Open sidebar: "💬 Policy Chat Assistant"
   - Ask questions like:
     - "What data do they collect?"
     - "How is my information shared?"
     - "Can I delete my data?"
   - Get AI-powered answers based on actual policy content

### API Endpoints

**Analyze URL:**
```bash
curl -X POST http://localhost:8000/analyze-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/privacy", "model": "bert"}'
```

**Chat with Policy:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What data do they collect?",
    "chunks": ["chunk1 text...", "chunk2 text..."]
  }'
```

## 🏗️ Architecture

### Unified LangGraph Workflow

```
Input (URL or Message)
         │
         ▼
    Master Router ───────┐
         │               │
         ├─ URL? ────────┤─── Chat Message?
         │               │
         ▼               ▼
   Analysis Flow    Chatbot Flow
         │               │
    Scrape URL      Detect Intent
         │               │
    Chunk Text      ┌────┴────┐
         │          │         │         │
    Classify    RAG Query  Instruction  Guardrail
         │          │         │         │
    Explain        └─────────┴─────────┘
         │                   │
    Summarize          Format Response
         │                   │
         └───────────────────┘
                     │
                     ▼
                  Output
```

### Chatbot Intelligence

**Intent Detection:**
- **Keyword-based**: Fast path for common privacy questions (25+ keywords)
- **LLM fallback**: Groq API for ambiguous cases
- **Default to RAG**: Favor answering over rejecting

**Response Types:**
- **RAG**: Context-aware answers from policy chunks
- **INSTRUCTION**: Help with using the tool
- **GUARDRAIL**: Polite rejection of off-topic queries

## 🔧 Configuration

### Models
Available classification models in `app/core/hf_classifier.py`:
- `bert`: BERT-base-uncased (fastest)
- `deberta`: DeBERTa-v3-base (balanced)
- `deberta-v2`: DeBERTa-v3-base-v2 (most accurate)

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key
```

## 📊 Privacy Categories (OPP-115)

The system classifies policies into 12 categories:

| Category | Risk Level | Description |
|----------|-----------|-------------|
| First Party Collection/Use | Medium | How company collects and uses data |
| Third Party Sharing/Collection | High | Data shared with third parties |
| User Choice/Control | Medium | User control over data |
| User Access, Edit & Deletion | Low | Data access and deletion rights |
| Data Retention | High | How long data is kept |
| Data Security | Low | Security measures |
| Policy Change | Medium | How policy changes are communicated |
| Do Not Track | High | Honor Do Not Track signals |
| International & Specific Audiences | Medium | Geographic/demographic specifics |
| Contact Information | Low | How to contact company |
| User Choices/Consent Mechanisms | Low | Consent mechanisms |
| Miscellaneous and Other | Medium | Other privacy-related content |

## 🌐 Browser Extension

See [EXTENSION_INTEGRATION.md](./EXTENSION_INTEGRATION.md) for:
- Complete Chrome extension implementation
- API integration examples
- Real-time policy analysis in-browser
- Chatbot integration for extensions

## 🧪 Testing

Run comprehensive system verification:
```bash
python verify_pipeline.py
```

Tests:
- ✅ Environment variables
- ✅ Module imports (core, LangChain, LangGraph, chatbot)
- ✅ Functional tests (chunking, classification, intent detection)
- ✅ Graph integration (analysis flow, chat flow)

## 📝 Development

### Adding New Features

**New Privacy Category:**
1. Update `DEFAULT_OPP115_LABELS` in `app/core/hf_classifier.py`
2. Add risk mapping in `RISK_MAPPING` (frontend)

**New Chatbot Intent:**
1. Add handler in `app/chatbot/`
2. Update router in `app/langgraph/graph.py`
3. Add node in `app/langgraph/nodes.py`

**Custom LLM Provider:**
1. Modify `app/langchain_modules/llm.py`
2. Update `.env` with new API keys

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **OPP-115 Dataset**: Privacy policy annotation corpus
- **Hugging Face**: Pre-trained classification models
- **Groq**: Fast LLM inference
- **LangChain**: LLM orchestration framework
- **LangGraph**: Workflow state management

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Built with ❤️ for privacy transparency**
