# py-zotero-manage

A collection of Python utilities for managing, organizing, and automating workflows within Zotero using the Zotero API.

## Current Scripts

### `sync_local_folder_to_zotero.py`

Synchronizes a local PDF library to Zotero while preserving the existing folder structure.

The script automatically creates matching collections in Zotero, links PDFs to their corresponding collections, and can optionally use Zotero's Linked Attachment Base Directory (LABD) feature to make linked papers accessible across multiple computers. This allows users to store PDFs in their own cloud storage (e.g. OneDrive) while using Zotero for organization, notes, and citations without relying on Zotero's limited cloud storage.

### Example

Local folder structure:

```text
papers_for_phd/
├── Brain Connectivity/
│   ├── Paper_A.pdf
│   └── Paper_B.pdf
├── OPM-MEG/
│   ├── Paper_C.pdf
│   └── Paper_D.pdf
└── Methods/
     ├── Paper_E.pdf
     └── Paper_F.pdf
```

Zotero collection structure created automatically:

```text
PhD
├── Brain Connectivity
│   ├── Paper_A.pdf
│   └── Paper_B.pdf
├── OPM-MEG
│   ├── Paper_C.pdf
│   └── Paper_D.pdf
└── Methods
     ├── Paper_E.pdf
     └── Paper_F.pdf
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
- Allows Zotero's LABD setting

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
ROOT_COLLECTION_NAME = "YOUR_ZOTERO_COLLECTION_NAME"
LIBRARY_ID = "YOUR_LIBRARY_ID"
API_KEY = "YOUR_API_KEY"
LIBRARY_TYPE = "user"
USE_LABD = True/False
```

| Variable | Description |
|-----------|-------------|
| `ROOT_FOLDER` | Root folder containing PDFs and subfolders |
| `ROOT_COLLECTION_NAME` | Top-level Zotero collection to mirror into |
| `LIBRARY_ID` | Zotero User or Group Library ID |
| `API_KEY` | Zotero API key with write permissions |
| `LIBRARY_TYPE` | Usually `"user"` |
| `USE_LABD` | Set to `True` to use Linked Attachment Base Directory (LABD) |

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

if you are using a standard virtual environment.

---

## Contributing

Suggestions, issues, and pull requests are welcome.

If you find a bug or have an idea for a Zotero workflow that could be automated, feel free to open an issue.
Happy to collaborate to add new features!
