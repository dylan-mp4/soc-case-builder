import re


def get_version():
    with open('src/resources/version.py', 'r') as file:
        content = file.read()
        version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", content)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

if __name__ == "__main__":
    print(get_version())