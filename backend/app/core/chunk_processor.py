# app/core/chunk_processor.py
from typing import List
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def validate_chunk(chunk: str, min_chars: int = 30) -> bool:
    """
    Validate a chunk for quality:
    - Must have minimum character count
    - Must contain at least one verb-like pattern (basic heuristic)
    - Must not be just whitespace or punctuation
    """
    if len(chunk.strip()) < min_chars:
        return False
    
    # Check for verb-like patterns (words ending in common verb suffixes or common verbs)
    verb_patterns = [
        r'\b(is|are|was|were|be|been|being)\b',  # to be
        r'\b(have|has|had|having)\b',  # to have
        r'\b(do|does|did|doing)\b',  # to do
        r'\b(will|would|shall|should|can|could|may|might|must)\b',  # modals
        r'\b\w+(ed|ing|ize|ise|ate|ify)\b',  # common verb endings
        r'\b(collect|share|use|store|retain|delete|access|provide|require|allow|enable|process)\b',  # privacy-specific verbs
    ]
    
    text_lower = chunk.lower()
    for pattern in verb_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False


def ensure_sentence_complete(text: str) -> str:
    """
    Ensure text ends with a complete sentence by trimming to the last sentence boundary.
    If no sentence boundary found, return as-is.
    """
    text = text.strip()
    if not text:
        return text
    
    # Already ends with sentence terminator
    if text[-1] in '.!?':
        return text
    
    # Find the last sentence boundary
    last_period = text.rfind('. ')
    last_question = text.rfind('? ')
    last_exclaim = text.rfind('! ')
    
    # Also check for period/question/exclaim at very end (could be followed by quote or nothing)
    for i in range(len(text) - 1, max(0, len(text) - 5), -1):
        if text[i] in '.!?':
            return text[:i+1]
    
    last_boundary = max(last_period, last_question, last_exclaim)
    
    if last_boundary > len(text) * 0.3:  # Only trim if we keep at least 30% of the text
        return text[:last_boundary + 1]
    
    return text  # Return as-is if no good boundary found


def ensure_sentence_start(text: str) -> str:
    """
    Ensure text starts with a sentence beginning (capital letter after cleanup).
    Trims leading fragments if detected.
    """
    text = text.strip()
    if not text:
        return text
    
    # If starts with lowercase and doesn't look like a proper start, try to find a sentence start
    if text[0].islower():
        # Look for ". X" or "? X" or "! X" pattern where X is uppercase
        match = re.search(r'[.!?]\s+([A-Z])', text)
        if match and match.start() < len(text) * 0.3:  # Fragment is small
            return text[match.start() + 2:]  # Start from the capital letter
    
    return text


def chunk_paragraphs_char_based(
    paragraphs: List[str],
    chunk_size_chars: int = 1500,
    chunk_overlap_chars: int = 200,
    min_chunk_chars: int = 50,
    validate: bool = True,
) -> List[str]:
    """
    Convert scraped paragraphs into coherent, validated chunks optimized for 
    HuggingFace transformer classification (512 token limit).
    """
    if not paragraphs:
        return []

    # Clean and filter paragraphs
    clean_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if len(p) > 20:  # Skip very short fragments
            clean_paragraphs.append(p)
    
    if not clean_paragraphs:
        return []

    # Join paragraphs with blank lines to preserve structure
    full_text = "\n\n".join(clean_paragraphs)

    # Use RecursiveCharacterTextSplitter with sentence-aware separators
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        separators=[
            "\n\n\n",  # Major section breaks
            "\n\n",     # Paragraph breaks
            "\n",       # Line breaks
            ". ",       # Sentence end
            "? ",       # Question end
            "! ",       # Exclamation end
            "; ",       # Semicolon (clause break)
            ", ",       # Comma (phrase break)
            " ",        # Word break (last resort)
        ],
        length_function=len,
    )

    raw_chunks = splitter.split_text(full_text)
    
    # Post-process chunks for quality
    processed_chunks = []
    for chunk in raw_chunks:
        # Ensure sentence completeness
        chunk = ensure_sentence_start(chunk)
        chunk = ensure_sentence_complete(chunk)
        chunk = chunk.strip()
        
        # Validate chunk
        if validate:
            if validate_chunk(chunk, min_chunk_chars):
                processed_chunks.append(chunk)
        else:
            if len(chunk) >= min_chunk_chars:
                processed_chunks.append(chunk)
    
    return processed_chunks

# Adapter for Lang Graph
def chunk_text(text: str) -> List[str]:
    """
    Splits the full text into processable chunks.
    Assumes text is already joined by newlines.
    """
    # Simply split by newlines to get "paragraphs" back if possible, 
    # or pass as single list item if raw text.
    # Our chunker expects list of paragraphs.
    if "\n\n" in text:
        paragraphs = text.split("\n\n")
    else:
        paragraphs = text.split("\n")
        
    print(f"DEBUG: chunk_text receiving text length {len(text)}, generated {len(paragraphs)} initial paragraphs.")
    
    chunks = chunk_paragraphs_char_based(paragraphs)
    print(f"DEBUG: chuck_paragraphs_char_based returned {len(chunks)} chunks.")
    return chunks
