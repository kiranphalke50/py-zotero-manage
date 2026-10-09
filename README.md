# py-zotero-manage

A collection of Python utilities for managing, organizing, and automating workflows within Zotero using the Zotero API.

The goal of this repository is to provide practical scripts that reduce repetitive tasks when working with large research literature collections. While the current focus is on synchronizing local PDF libraries with Zotero, additional tools may be added in the future for metadata management, library maintenance, reporting, tagging, note extraction, and other research workflows.

## Current Scripts

### `sync_local_folder_to_zotero.py`

Synchronizes a local folder hierarchy containing PDF papers to a Zotero library while preserving the existing folder structure.

### Example

Local folder structure:

```text
papers_for_phd/
├── Brain Connectivity/
│   ├── Paper_A.pdf
│   └── Paper_B.pdf
├── OPM-MEG/
└── Methods/
```

Zotero collection structure created automatically:

```text
PhD
├── Brain Connectivity
├── OPM-MEG
└── Methods
```

### Features

- Mirrors local folder hierarchies into Zotero collections
- Creates missing collections automatically
- Links PDFs without moving or copying files
- Detects duplicate linked PDFs
- Extracts DOI information from PDFs where available
- Retrieves publication metadata from Crossref
- Creates Zotero Journal Article entries when metadata can be identified
- Falls back to generic Zotero Document entries when metadata cannot be identified
- Preserves the local folder structure as the source of truth
- Allows a configurable root collection name in Zotero (e.g. `PhD`)

### Typical Workflow

```text
Local PDF
     ↓
Extract DOI
     ↓
Crossref Lookup
     ↓
Create Journal Article in Zotero
     ↓
Create Linked PDF Attachment
```

If a DOI cannot be located:

```text
Local PDF
     ↓
DOI Not Found
     ↓
Create Generic Document in Zotero
     ↓
Create Linked PDF Attachment
```

This ensures that every PDF in the source folder is represented in Zotero, even if metadata cannot be determined automatically.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/py-zotero-manage.git
cd py-zotero-manage
```

Install dependencies:

```bash
uv sync
```

---

## Configuration

Open the script and configure the following variables:

```python
ROOT_FOLDER = Path(
    r"C:\path\to\papers_for_phd"
)

ROOT_COLLECTION_NAME = "PhD"

LIBRARY_ID = "YOUR_LIBRARY_ID"
API_KEY = "YOUR_API_KEY"
LIBRARY_TYPE = "user"
```

### Required Settings

| Variable | Description |
|-----------|-------------|
| `ROOT_FOLDER` | Root folder containing PDFs and subfolders |
| `ROOT_COLLECTION_NAME` | Top-level Zotero collection to mirror into |
| `LIBRARY_ID` | Zotero User or Group Library ID |
| `API_KEY` | Zotero API key with write permissions |
| `LIBRARY_TYPE` | Usually `"user"` |

### Obtaining Zotero Credentials

Library ID:

- Zotero Web Library → Settings

API Key:

- https://www.zotero.org/settings/keys

Recommended permissions:

- Read Library
- Write Library

---

## Running

Run the synchronization script:

```bash
uv run python src/local/sync_local_folder_to_zotero.py
```

or:

```bash
python src/local/sync_local_folder_to_zotero.py
```

if you are using a standard virtual environment.

---

## Contributing

Suggestions, issues, and pull requests are welcome.

If you find a bug or have an idea for a Zotero workflow that could be automated, feel free to open an issue.
Happy to collaborate to add new features!
