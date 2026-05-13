from huggingface_hub import HfApi, ModelCard
import sys

def get_brief_description(model_id):
    try:
        card = ModelCard.load(model_id)
        content = card.data.text if hasattr(card, 'data') else card.content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        lines = content.split('\n')
        description = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                description = line
                break
        if description:
            if len(description) > 200:
                description = description[:197] + "..."
            return description
        else:
            return "No description available"
    except Exception:
        return "No description available"

def main():
    api = HfApi()
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
