# SOC Case Builder

**SOC Case Builder** is a Python-based application designed to help Security Operations Centers (SOCs) efficiently build, manage, and document cases. It features a modern, responsive user interface built with **Flet** and includes robust tools for managing entities, clients, and API configurations.

---

## Features

### 🗂️ Case Management
- Create, rename, and delete case tabs using native tab control
- Save case information as JSON files with timestamps
- Dynamic field addition/removal for flexibility

### 👥 Client & Entity Management
- Add and manage clients (stored in centralized settings)
- Define and manage custom entity types (IP, Domain, Hash, URL, etc.)
- Entity auto-detection for standardized field types

### 🔍 Entity Enrichment
- Query entities against external APIs
- Search saved cases by entity value
- Integrated entity cache with TTL-based expiration
- Status indicators for enrichment state (enriched/pending/error)

### 📋 Case Workflow
- Route cases to close or escalation
- Add detailed notes for each route
- Compile cases to formatted output
- Full case history and persistence

### ⚙️ Configurable Settings
- API key configuration:
  - AbuseIPDB
  - VirusTotal
  - URLScan (with optional wait time)
- User and organization sign-off details
- Custom entity type management
- Set language and region

---

## Installation

### ✅ Prerequisites

- Python 3.12.6 or later
- Windows 10+ (currently targeting Windows desktop)

### 📦 Clone the Repository

```sh
git clone https://github.com/dylan-mp4/soc-case-builder.git
cd soc-case-builder
```

### 🏗️ Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
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

## Architecture

The application is built with a **clear separation of concerns**:

- **UI Layer** (`src/ui_flet/`): Flet-based user interface with reactive components
- **Business Logic** (`src/utils/`): Entity enrichment, API integration, file operations
- **State Management** (`src/ui_flet/state.py`): Centralized AppState for all app-level data
- **Configuration** (`src/ui_flet/config/`): Settings persistence with flat JSON schema

Key features:
- ✅ Decoupled UI from business logic
- ✅ Centralized application state
- ✅ Settings auto-migration from legacy formats
- ✅ Reactive UI updates
- ✅ Dark mode theme throughout

See [MIGRATION_NOTES.md](MIGRATION_NOTES.md) for detailed architecture documentation.

---

## Settings

All settings are now stored in a single flat JSON file: `src/ui_flet/config/settings.json`

Settings include:
- User and organization details
- API keys (AbuseIPDB, VirusTotal, URLScan)
- Client list
- Custom entity types
- Entity cache TTLs
- Application state (first_time flag)

Settings are automatically migrated from the legacy PyQt6 format on first run.

---

## Building for Distribution

### Build Windows Executable

```bash
# Install dev requirements
pip install -r dev_requirements.txt

# Build with PyInstaller
pyinstaller soc_case_builder.spec

# Output: dist/soc_case_builder/soc_case_builder.exe
```

---

## Development

### Project Structure

```
src/
├── main.py                    # Application entry point
├── ui_flet/                   # Flet UI implementation
│   ├── app.py                # Main Flet app
│   ├── state.py              # Centralized app state
│   ├── theme.py              # Dark mode colors
│   ├── config/               # Settings and configuration
│   ├── components/           # Reusable UI components
│   └── pages/                # Page implementations
├── utils/                     # Business logic
│   ├── api_requests.py       # External API integration
│   ├── entity_store.py       # Entity cache management
│   ├── file_operations.py    # File I/O and persistence
│   └── check_updates.py      # Update checking
└── resources/                 # Application resources
```

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
