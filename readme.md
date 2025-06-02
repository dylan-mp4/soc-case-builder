# SOC Case Builder

SOC Case Builder is a Python-based application designed to help security operations centers (SOCs) build and manage cases efficiently. The application provides a user-friendly interface for creating, managing, and saving cases, as well as configuring settings and adding clients.

## Features

## Features

- Create, rename, and remove case tabs
- Save case information to text files
- Configure settings, including API keys for various services
- Add and manage clients
- Add and manage custom entities
- **Spell check** support using enchant
- User-friendly interface built with PyQt6
- **Bulk Add Entities:** Import multiple entities at once from CSV, JSON, or raw text (comma, space, or newline separated)
- **Automatic Entity Type Detection:** Entity types (IP, Domain, URL, Hash, Email, etc.) are auto-detected when importing; unrecognized types are labeled "Other" and can be renamed or edited later
- **Flexible Import:** Import entities from files or clipboard with automatic parsing and mapping to fields

## Installation

### Prerequisites

- Python (Built with 3.12.6)

### Getting Started
#### Clone the Repository
```sh
git clone https://github.com/dylan-mp4/soc-case-builder.git
cd soc-case-builder
```
#### Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### Usage
#### Install Dependencies
```sh
pip install -r requirements.txt
```
#### Running the Application
```sh
python src/main.py
```

### Settings
The settings can be configured through the settings dialog in the application. The settings include:

- Sign off (User)
- Sign off (Org)
- AbuseIPDB API Key
- VirusTotal API Key
- URLScan API Key
- URLScan wait time (0-100s)
- Custom entities
- Spell check settings

### Clients
Clients can be added and managed through the settings dialog. The clients are stored in `clients.csv`.

### Custom Entities
Custom entities can be added and managed through the settings dialog. The entities are stored in `entities.json`.

### Spell Check
The spell check feature can be configured through the settings dialog. You can add custom words to the dictionary and select the language region.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
- PyQt6
- PyInstaller
- AbuseIPDB
- VirusTotal
- URLScan
- Networkcalc