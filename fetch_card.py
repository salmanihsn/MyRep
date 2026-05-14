import sys
from huggingface_hub import HfApi, ModelCard, hf_hub_download
import os

def fetch_full_model_card(model_id):
    """Fetch the full model card (README.md) content for a given model ID."""
    try:
        # Method 1: Use ModelCard.load (returns parsed object with text/content)
        card = ModelCard.load(model_id)
        # Prefer the 'text' attribute (excludes YAML front matter) or fallback to 'content'
        content = getattr(card, 'text', None) or getattr(card, 'content', '')
        if not content:
            # If still empty, try downloading raw README
            content = hf_hub_download(
                repo_id=model_id,
                filename="README.md",
                repo_type="model"
            )
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        return content
    except Exception as e:
        return f"# Error\n\nCould not fetch model card for `{model_id}`.\n\nError details:\n```\n{str(e)}\n```"

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_card.py <model_id>")
        sys.exit(1)

    model_id = sys.argv[1]
    print(f"Fetching model card for: {model_id}")
    card_content = fetch_full_model_card(model_id)

    # Create a safe filename (replace / with _)
    safe_id = model_id.replace('/', '_')
    filename = f"model_card_{safe_id}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(card_content)

    print(f"Saved model card to {filename}")
    # Also write to a fixed name for easy committing
    with open("model_card.md", 'w', encoding='utf-8') as f:
        f.write(card_content)

if __name__ == "__main__":
    main()
