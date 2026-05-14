import sys
from huggingface_hub import HfApi, list_repo_files
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

def get_file_sizes(model_id, files, api):
    """Get sizes for each file, returns dict. If fails, sizes remain None."""
    sizes = {}
    for i, filename in enumerate(files):
        try:
            print(f"Fetching size for {i+1}/{len(files)}: {filename}", file=sys.stderr)
            info = api.file_info(repo_id=model_id, path=filename)
            sizes[filename] = info.size if hasattr(info, 'size') else None
        except Exception as e:
            print(f"  Warning: Could not get size for {filename}: {e}", file=sys.stderr)
            sizes[filename] = None
    return sizes

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_file_list.py <model_id>")
        sys.exit(1)

    model_id = sys.argv[1]
    print(f"Fetching file list for: {model_id}", file=sys.stderr)

    api = HfApi()
    try:
        # Get all files recursively
        files = list(list_repo_files(model_id))
        print(f"Found {len(files)} files", file=sys.stderr)
    except Exception as e:
        print(f"ERROR fetching file list: {e}", file=sys.stderr)
        # Write error to file_list.md so user sees it
        with open("file_list.md", "w", encoding="utf-8") as f:
            f.write(f"# Error\n\nCould not fetch file list for `{model_id}`.\n\nDetails:\n```\n{str(e)}\n```")
        sys.exit(1)

    # Sort for readability
    files.sort()

    # Try to get file sizes (optional; if it fails, show "Unknown")
    sizes = {}
    try:
        sizes = get_file_sizes(model_id, files, api)
    except Exception as e:
        print(f"Warning: Could not retrieve file sizes: {e}", file=sys.stderr)
        # Continue without sizes

    # Generate markdown
    output = []
    output.append(f"# File List for `{model_id}`\n")
    output.append(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    output.append(f"**Total files:** {len(files)}\n")
    output.append("## Files\n")
    output.append("| File | Size | Direct Download URL |")
    output.append("|------|------|---------------------|")

    for filename in files:
        size = sizes.get(filename) if filename in sizes else None
        size_str = human_readable_size(size) if size else "Unknown"
        # URL encode the filename to handle spaces and special chars
        import urllib.parse
        encoded_filename = urllib.parse.quote(filename)
        url = f"https://huggingface.co/{model_id}/resolve/main/{encoded_filename}"
        # Markdown escape pipe characters in filename
        safe_filename = filename.replace('|', '\\|')
        output.append(f"| `{safe_filename}` | {size_str} | [Download]({url}) |")

    # Write to file
    with open("file_list.md", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"Success! File list saved to file_list.md", file=sys.stderr)

if __name__ == "__main__":
    main()
