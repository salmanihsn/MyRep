#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import shutil
from pathlib import Path

def run_command(cmd, description, check=True):
    print(f"[INFO] {description}...")
    print(f"[DEBUG] Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"[ERROR] Command failed (exit {result.returncode})")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result

def download_file(url, output_path):
    # Use aria2 if available, else curl
    if shutil.which("aria2c"):
        cmd = f"aria2c -x 16 -s 16 -k 1M --console-log-level=error -o '{output_path}' '{url}'"
    else:
        cmd = f"curl -L -o '{output_path}' '{url}'"
    run_command(cmd, f"Downloading file from {url}")

def create_split_zip(input_file, output_dir, part_size, password):
    base_name = Path(input_file).stem
    # Output zip file path (the split parts will be named as base.zip, base.z01, base.z02...)
    output_zip = os.path.join(output_dir, f"{base_name}.zip")
    # The zip command: -P password, -s split size, output zip, input file(s)
    cmd = f"zip -P '{password}' -s '{part_size}' '{output_zip}' '{input_file}'"
    run_command(cmd, f"Creating password-protected split zip (part size {part_size})")
    # zip command may produce a warning about using -s and -P together, but it works.
    return output_zip

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--part-size", default="90m")
    parser.add_argument("--output-dir", default="Download-Files")
    args = parser.parse_args()

    # Create output directory
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Temporary download location
    temp_dir = Path("/tmp/download_split")
    temp_dir.mkdir(exist_ok=True)
    # Extract filename from URL
    filename = Path(args.url).name
    if not filename:
        filename = "downloaded_file.bin"
    downloaded = temp_dir / filename

    # Download
    download_file(args.url, str(downloaded))

    # Verify file exists and is non-zero
    if not downloaded.exists() or downloaded.stat().st_size == 0:
        print("[ERROR] Downloaded file is empty or missing")
        sys.exit(1)
    print(f"[INFO] Downloaded {downloaded.stat().st_size} bytes")

    # Split and zip
    create_split_zip(str(downloaded), str(out_dir), args.part_size, args.password)

    # Cleanup
    downloaded.unlink()
    print(f"[SUCCESS] Split zip parts saved in {out_dir}/")

if __name__ == "__main__":
    main()
