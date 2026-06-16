from utils.text_utils import clean_and_normalize

async def process_raw_text(text: str) -> str:
    """Entry point for processing pure text inputs."""
    # Could include language detection, initial profanity filters, etc.
    cleaned = clean_and_normalize(text)
    return cleaned
