# Changelog

All notable changes to PolicyLens are documented here.

## [2.0.0] - 2026-01-16

### 🎉 Major Features Added

#### Interactive RAG Chatbot
- **Conversational Q&A**: Ask natural language questions about analyzed privacy policies
- **Intent Routing**: Automatic classification into RAG questions, instructions, or off-topic
- **Context-Aware Responses**: Uses actual policy chunks for accurate, cited answers
- **Smart Guardrails**: Politely handles off-topic queries

#### Enhanced LangGraph Architecture
- **Unified Workflow**: Single graph handles both analysis and chat flows
- **Master Router**: Intelligent routing based on input type (URL vs message)
- **Chatbot Nodes**: Intent detection, RAG, instruction, and guardrail nodes
- **State Management**: Comprehensive state tracking for both workflows

#### Frontend Improvements
- **Sidebar Chat Interface**: Collapsible chat assistant in Streamlit sidebar
- **Context Status**: Shows number of policy sections loaded
- **Better Formatting**: 
  - RAG answers with bold headers
  - Color-coded response types (info, warning, error)
  - Suggested example questions
- **Chat Controls**: Clear chat and refresh buttons
- **Error Handling**: Timeout protection and connection error messages

#### Backend Enhancements
- **Unified `/chat` Endpoint**: Single endpoint for all chat interactions
- **Chunks in Response**: Analysis endpoints now return chunks for chatbot context
- **Response Builder**: Standardized response formatting
- **Better Logging**: Intent detection and flow tracking

### 🔧 Technical Improvements

#### Intent Detection
- **Keyword-based Fast Path**: 25+ privacy-related keywords for instant detection
- **LLM Fallback**: Groq API for ambiguous cases
- **Default to RAG**: Favors answering questions over rejection
- **Error Recovery**: Graceful handling of detection failures

#### RAG Handler
- **Empty Chunk Detection**: Helpful messages when no policy loaded
- **Enhanced Context**: Better chunk separation and formatting
- **Prompt Engineering**: Explicit instructions to cite policy sections

#### Code Organization
- Moved chatbot logic to `app/chatbot/` module
- Separated concerns: intent, RAG, instruction, guardrails
- Improved error handling throughout
- Added comprehensive type hints

### 📚 Documentation
- **Updated README**: Complete feature overview and architecture
- **Extension Guide**: Added chatbot endpoint integration
- **Verification Script**: Comprehensive system testing including chatbot
- **Code Comments**: Better inline documentation

### 🐛 Bug Fixes
- Fixed duplicate `/chat` endpoint in backend
- Resolved state typing issues in graph nodes
- Corrected chunk passing between frontend and backend
- Fixed session state initialization in Streamlit

### 🗑️ Removed
- `verify_chatbot.py` - Merged into main verification script
- Legacy chatbot graph file - Unified into main graph
- Duplicate chat state definitions

---

## [1.0.0] - 2025-12-08

### Initial Release

#### Core Features
- Privacy policy URL scraping
- Semantic text chunking (512-token limit)
- Multi-label classification (OPP-115 dataset)
- Risk level assessment (High/Medium/Low)
- AI-powered explanations
- Policy summaries with metadata extraction

#### Architecture
- Modular `app/` structure
- LangGraph workflow orchestration
- FastAPI backend
- Streamlit frontend
- Hugging Face Transformers integration

#### Models
- BERT-base-uncased
- DeBERTa-v3-base
- DeBERTa-v3-base-v2

#### Components
- Web scraper with robust extraction
- Chunk processor with sentence awareness
- HF classifier with 3 model options
- LLM integration via Groq API
- Risk mapping system

---

## Version History

- **2.0.0**: Major release with RAG chatbot integration
- **1.0.0**: Initial release with policy analysis
