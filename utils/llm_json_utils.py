import re

def extract_json(text: str) -> str:
    """
    Remove ```json ... ``` e retorna apenas o JSON puro.
    """
    # Remove ```json ou ```
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    return text.strip()
