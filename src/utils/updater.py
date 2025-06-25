import sys
import os
import time
import requests
import zipfile

def main():
    if len(sys.argv) < 2:
        print("No download URL provided.")
        sys.exit(1)
    download_url = sys.argv[1]
    app_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(app_dir, "update.zip")
    print("Downloading update...")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Extracting update...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(app_dir)
    os.remove(zip_path)
    print("Update complete. Restarting app...")
    os.execv(sys.executable, [sys.executable, os.path.join(app_dir, "main.py")])

if __name__ == "__main__":
    # Wait a moment to ensure the main app has exited
    time.sleep(2)
    main()