# SOC Case Builder

**SOC Case Builder** is a Python-based application designed to help Security Operations Centers (SOCs) efficiently build, manage, and document cases. It features a user-friendly interface built with PyQt6 and includes robust tools for managing entities, clients, spell check, and API configurations.

---

## Features

### 🗂️ Case Management
- Create, rename, and delete case tabs
- Save case information to text files

### 👥 Client & Entity Management
- Add and manage clients (stored in `clients.csv`)
- Define and manage custom entities (stored in `entities.json`)

### 📥 Bulk Entity Import
- Import multiple entities from:
  - CSV
  - JSON
  - Raw text (comma, space, or newline separated)
- Import via file upload or clipboard

### 🧠 Smart Entity Detection
- Automatically detects types such as IP, Domain, URL, Hash, Email
- Unrecognized entities are labeled "Other" and can be edited later

### 📝 Spell Check
- Integrated spell check powered by `enchant`
- Add custom dictionary entries
- Set language and region

### ⚙️ Configurable Settings
- API key configuration:
  - AbuseIPDB
  - VirusTotal
  - URLScan (with optional wait time)
- User and organization sign-off details
- Manage spell check and custom entity preferences

---

## Installation

### ✅ Prerequisites

- Python 3.12.6 or later

### 📦 Clone the Repository

### Getting Started
#### Clone the Repository
```sh
git clone https://github.com/dylan-mp4/soc-case-builder.git
cd soc-case-builder
```

### 🏗️ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 📥 Install Dependencies

```bash
pip install -r requirements.txt
```

### ▶️ Run the Application

```bash
python src/main.py
```

---

## Settings Overview

All settings are available via the **Settings Dialog** within the application.

### API Keys
- AbuseIPDB
- VirusTotal
- URLScan
- URLScan wait time (0–100 seconds)

### Sign-Off Info
- Analyst name
- Organization name

### Spell Check
- Enable or disable spell check
- Set language region
- Add custom dictionary entries

---

## Clients

Clients can be added and managed through the Settings Dialog.  
Stored persistently in `clients.csv`.

---

## Custom Entities

Define and manage your own entity types via the Settings Dialog.  
Stored in `entities.json`.

---

## Spell Check

Spell checking is provided by the `enchant` library.  
You can configure:
- Default language/region
- Custom word lists
- Enable/disable per session

---

## Contributing

Contributions are welcome! To contribute:
- Open an issue for bugs or feature requests
- Fork the repo and submit a Pull Request

Please follow standard Python formatting and documentation practices.

---

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [PyQt6](https://riverbankcomputing.com/software/pyqt/intro)
- [PyInstaller](https://pyinstaller.org/)
- [AbuseIPDB](https://www.abuseipdb.com/)
- [VirusTotal](https://www.virustotal.com/)
- [URLScan.io](https://urlscan.io/)
- [NetworkCalc](https://networkcalc.com/)
