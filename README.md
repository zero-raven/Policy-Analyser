# Privacy Policy Clause Classifier

This project provides a web interface for classifying sections of Privacy Policies and Terms of Service documents using a fine-tuned BERT model. It consists of a FastAPI backend for model inference and a Streamlit frontend for user interaction.

## Components

### Frontend (`frontend_streamlit.py`)
A Streamlit-based web interface that allows users to:
- Input sections of privacy policies or terms of service
- Submit text for classification
- View classification results with confidence scores
- Visualize predictions through interactive bar charts

### Backend (`backend_fastapi.py`)
A FastAPI server that:
- Loads a custom fine-tuned BERT model for multi-label classification
- Processes incoming text requests
- Returns predicted categories with confidence scores
- Handles model inference using PyTorch

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
uvicorn backend_fastapi:app --reload
```

3. Launch the frontend:
```bash
streamlit run frontend_streamlit.py
```

## Usage

1. Open the Streamlit interface in your browser (typically http://localhost:8501)
2. Paste a section of privacy policy or terms of service into the text area
3. Click "Classify Section" to analyze the text
4. View the results, including:
   - Detected privacy categories
   - Confidence scores
   - Visual representation of all category probabilities

## Model

The system uses the [`Hacktrix-121/bert-base-uncased-opp115-multilabel`](https://huggingface.co/Hacktrix-121/bert-base-uncased-opp115-multilabel) model, which is trained on the [OPP-115 Privacy Policy Dataset](https://huggingface.co/datasets/opp_115) to identify 12 different privacy policy categories:
- First Party Collection/Use
- Third Party Sharing/Collection
- User Choice/Control
- User Access, Edit & Deletion
- Data Retention
- Data Security
- Policy Change
- Do Not Track
- International & Specific Audiences
- Miscellaneous and Other
- Contact Information
- User Choices/Consent Mechanisms

The model is fine-tuned on BERT base uncased for multi-label classification of privacy policy segments. The OPP-115 dataset consists of 115 privacy policies (267K words) annotated by skilled annotators for various privacy practice categories.

## Technical Requirements

- Python 3.7+
- FastAPI for the backend server
- Streamlit for the web interface
- PyTorch and Transformers for model inference
- See `requirements.txt` for complete dependencies