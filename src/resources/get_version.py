import re
import os

def get_version():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(base_dir, "version.py")
    with open(version_file, 'r', encoding='utf-8') as file:
        content = file.read()
        version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", content)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

if __name__ == "__main__":
    print(get_version())