import re
import unicodedata

def clean_and_normalize(text: str) -> str:
    """Normalize unicode, strip extra whitespace, and clean up basic punctuation."""
    # Normalize unicode to NFKC (combines characters and normalizes widths)
    text = unicodedata.normalize("NFKC", text)
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Basic semantic chunking by character length with overlap."""
    words = text.split(' ')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1 # +1 for space
        
        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            # Start new chunk keeping overlap number of words
            overlap_words = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
            current_chunk = overlap_words
            current_length = sum(len(w) + 1 for w in current_chunk)
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks
