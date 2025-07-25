import spacy

nlp = spacy.load("en_core_web_sm")


KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "genai", "copilot"],
    "productivity": ["notion", "workflow", "task", "calendar"],
    "social": ["community", "connect", "chat", "forum"],
    "devtools": ["api", "sdk", "developer", "open source"],
    "design": ["figma", "interface", "ux", "design"],
}

def extract_tags(text: str):
    doc = nlp(text.lower())
    tags = set()
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                tags.add(category)
    return list(tags)
