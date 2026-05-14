from huggingface_hub import HfApi, ModelCard
import sys

def get_brief_description(model_id):
    """
    Try to extract a short description from the model card.
    Returns a string (max 200 chars) or "No description available".
    """
    try:
        # Attempt to load the model card
        card = ModelCard.load(model_id)
    except Exception as e:
        # Catch any exception (like EntryNotFoundError) and return the default message
        return "No description available"

    # If card is loaded successfully, try to get the text content
    # Prefer card.text (excludes metadata header) over card.content
    text = getattr(card, 'text', '')
    if not text:
        text = getattr(card, 'content', '')

    if not text:
        return "No description available"

    # Split the text into lines and find a likely description
    lines = text.split('\n')
    description = ""
    for line in lines:
        line = line.strip()
        # Look for lines that are not empty, not markdown headers, and not YAML front matter
        if line and not line.startswith('---') and not line.startswith('#') and len(line) > 10:
            description = line
            break

    if description:
        # Trim to max 200 chars
        if len(description) > 200:
            description = description[:197] + "..."
        return description
    else:
        return "No description available"

def main():
    api = HfApi()
    # Fetch first 50 models (you can change the number)
    print("Fetching model list...", file=sys.stderr)
    models = list(api.list_models(limit=50))

    with open("models.txt", "w", encoding="utf-8") as f:
        for i, model in enumerate(models):
            model_id = model.id
            print(f"Processing {i+1}/{len(models)}: {model_id}", file=sys.stderr)
            description = get_brief_description(model_id)
            f.write(f"{model_id}: {description}\n")

    print(f"Done. Saved {len(models)} models to models.txt", file=sys.stderr)

if __name__ == "__main__":
    main()
