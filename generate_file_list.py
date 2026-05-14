import sys
from huggingface_hub import HfApi, list_repo_files, get_repo_files
import os
from datetime import datetime

def human_readable_size(size_bytes):
    """Convert bytes to human readable string."""
    if size_bytes is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_file_info(model_id, filename):
    """Get size of a single file using repo_file_info endpoint."""
    api = HfApi()
    try:
        # Fetch file metadata
        info = api.file_info(repo_id=model_id, path=filename)
        size = info.size if hasattr(info, 'size') else None
        return size
    except Exception:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_file_list.py <model_id>")
        sys.exit(1)

    model_id = sys.argv[1]
    print(f"Fetching file list for: {model_id}")

    api = HfApi()
    # Get all files in the repository (recursive)
    try:
        files = list(list_repo_files(model_id))
    except Exception as e:
        print(f"Error fetching file list: {e}")
        sys.exit(1)

    # Sort files alphabetically
    files.sort()

    # Collect file sizes
    print("Collecting file sizes (this may take a while for large repos)...")
    file_data = []
    for f in files:
        size_bytes = get_file_info(model_id, f)
        file_data.append((f, size_bytes))

    # Generate markdown output
    output = []
    output.append(f"# File List for `{model_id}`\n")
    output.append(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    output.append(f"Total files: {len(files)}\n")
    output.append("## Files\n")
    output.append("| File | Size | Direct Download URL |")
    output.append("|------|------|---------------------|")

    for filename, size in file_data:
        size_str = human_readable_size(size) if size else "Unknown"
        # Direct download URL (raw)
        url = f"https://huggingface.co/{model_id}/resolve/main/{filename}"
        output.append(f"| `{filename}` | {size_str} | [Download]({url}) |")

    # Write to file_list.md
    with open("file_list.md", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"File list saved to file_list.md ({len(files)} files)")

if __name__ == "__main__":
    main()
