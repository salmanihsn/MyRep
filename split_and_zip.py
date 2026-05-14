#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and exit on failure."""
    print(f"[INFO] {description} ...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result.stdout

def download_file(url, output_path):
    """Download a file using aria2c (resume capable, multi‑connection)."""
    # aria2c -x 16 -s 16 -k 1M -o <output> <url>
    cmd = f"aria2c -x 16 -s 16 -k 1M --console-log-level=error -o '{output_path}' '{url}'"
    run_command(cmd, f"Downloading {url}")

def create_split_zip(input_file, output_dir, part_size, password):
    """
    Create password‑protected split zip archives.
    Output files will be: output.zip, output.z01, output.z02, ...
    """
    base_name = Path(input_file).stem
    output_zip = os.path.join(output_dir, f"{base_name}.zip")
    # Use zip -P <password> -s <size> -r <output.zip> <input>
    # Note: -s accepts suffixes like '90m', '100m'
    cmd = f"zip -P '{password}' -s '{part_size}' '{output_zip}' '{input_file}'"
    run_command(cmd, f"Splitting and zipping with password (part size {part_size})")
    return output_zip

def main():
    parser = argparse.ArgumentParser(description="Download a file, split into password‑protected zip parts.")
    parser.add_argument("--url", required=True, help="URL of the file to download")
    parser.add_argument("--password", required=True, help="Password for the zip archive")
    parser.add_argument("--part-size", default="90m", help="Size of each part, e.g., 90m, 100m")
    parser.add_argument("--output-dir", default="Download-Files", help="Directory to store the split parts")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Download to a temporary location (outside the repo to avoid committing the original)
    temp_dir = Path("/tmp/download_split")
    temp_dir.mkdir(exist_ok=True)
    downloaded_file = temp_dir / Path(args.url).name
    download_file(args.url, str(downloaded_file))

    # Create split, password‑protected zip directly into the output directory
    create_split_zip(str(downloaded_file), args.output_dir, args.part_size, args.password)

    # Clean up temporary file
    os.remove(downloaded_file)
    print(f"[INFO] Done. Split zip parts are in '{args.output_dir}/'")

if __name__ == "__main__":
    main()
