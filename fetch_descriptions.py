from huggingface_hub import HfApi, ModelCard
import sys

def get_brief_description(model_id):
    """
    Try to extract a short description from the model card.
    Returns a string (max 200 chars) or "No description available".
    """
    try:
        card = ModelCard.load(model_id)
        # Look for the '---' YAML front matter, then the 'description' field
        # Or take the first paragraph after the front matter.
        content = card.data.text if hasattr(card, 'data') else card.content
        
        # Remove YAML front matter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Split into lines and find first non-empty, non-header line
        lines = content.split('\n')
        description = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                description = line
                break
        
        if description:
            # Trim to max 200 chars
            if len(description) > 200:
                description = description[:197] + "..."
            return description
        else:
            return "No description available"
    except Exception as e:
        # Many models don't have a model card or fail to load
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
            # Write as "model_id: description"
            f.write(f"{model_id}: {description}\n")
    
    print(f"Done. Saved {len(models)} models to models.txt", file=sys.stderr)

if __name__ == "__main__":
    main()
