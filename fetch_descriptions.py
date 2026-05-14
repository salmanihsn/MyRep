from huggingface_hub import HfApi, ModelCard
import re
import sys

def clean_text(text):
    """Remove markdown images, HTML tags, and excessive whitespace."""
    # Remove markdown images ![alt](url)
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def get_brief_description(model_id):
    try:
        card = ModelCard.load(model_id)
    except Exception:
        return "No description available"

    # Strategy 1: Use YAML description field if present
    if hasattr(card, 'data') and card.data and hasattr(card.data, 'description'):
        desc = card.data.description
        if desc and isinstance(desc, str):
            desc = clean_text(desc)
            if desc:
                if len(desc) > 200:
                    desc = desc[:197] + "..."
                return desc

    # Strategy 2: Parse the model card text
    text = getattr(card, 'text', '') or getattr(card, 'content', '')
    if not text:
        return "No description available"

    lines = text.split('\n')
    description = ""
    for line in lines:
        # Skip YAML front matter
        if line.strip().startswith('---'):
            continue
        # Clean the line
        cleaned = clean_text(line)
        # Skip empty or very short lines
        if len(cleaned) < 15:
            continue
        # Skip lines that are mostly punctuation or special chars
        if cleaned.startswith(('*', '-', '#', '=', '|')):
            continue
        # Skip lines that look like badges or buttons
        if '[![' in cleaned or 'https://' in cleaned and len(cleaned) < 50:
            continue
        # Found a likely description
        description = cleaned
        break

    if description:
        if len(description) > 200:
            description = description[:197] + "..."
        return description
    else:
        return "No description available"

def main():
    api = HfApi()
    print("Fetching model list...", file=sys.stderr)
    models = list(api.list_models(limit=50))

    with open("models.txt", "w", encoding="utf-8") as f:
        for i, model in enumerate(models):
            model_id = model.id
            print(f"Processing {i+1}/{len(models)}: {model_id}", file=sys.stderr)
            desc = get_brief_description(model_id)
            f.write(f"{model_id}: {desc}\n")

    print(f"Done. Saved {len(models)} models to models.txt", file=sys.stderr)

if __name__ == "__main__":
    main()
