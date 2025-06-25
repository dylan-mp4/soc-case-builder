import sys
import os
import time
import requests
import zipfile
import shutil

def main():
    if len(sys.argv) < 2:
        print("No download URL provided.")
        sys.exit(1)
    download_url = sys.argv[1]
    # Get the parent directory of 'utils' (should be the main app directory)
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
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
    # Move the contents of the extracted soc_case_builder folder up one level
    extracted_dir = os.path.join(app_dir, "soc_case_builder")
    if os.path.isdir(extracted_dir):
        for item in os.listdir(extracted_dir):
            s = os.path.join(extracted_dir, item)
            d = os.path.join(app_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        shutil.rmtree(extracted_dir)
    print("Update complete. Restarting app...")
    exe_path = os.path.join(app_dir, "soc_case_builder.exe")
    os.execv(exe_path, [exe_path])

if __name__ == "__main__":
    # Wait a moment to ensure the main app has exited
    time.sleep(2)
    main()