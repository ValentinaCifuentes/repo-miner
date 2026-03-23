import re

def extract_words(identifier: str) -> list[str]:
    if not identifier:
        return []

    text = identifier.replace('_', ' ').replace('-', ' ')
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    words = text.lower().split()
    clean_words = [re.sub(r'[^a-z]', '', w) for w in words]
    
    return [w for w in clean_words if w]
