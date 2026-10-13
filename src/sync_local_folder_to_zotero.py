"""
Synchronize a local PDF library to Zotero while preserving the existing folder hierarchy.

Purpose
-------
This script is intended for researchers who maintain a literature collection as a
structured folder tree (e.g. in OneDrive, Dropbox, or a local drive) and wish to
use Zotero for reference management, annotation, note-taking, and citation
generation without reorganizing their files.

Use Case
--------
Given a folder structure such as:

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

the script automatically creates a corresponding collection hierarchy in Zotero:

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

and links each PDF to its matching Zotero collection.

User Configuration
------------------
Before running the script, the user must configure:

    ROOT_FOLDER
        Path to the root directory containing the PDF library.

    ROOT_COLLECTION_NAME
        Name of the top-level Zotero collection under which the folder
        hierarchy will be mirrored.

    LIBRARY_ID
        Zotero User or Group Library ID.

    API_KEY
        Zotero API key with write permissions.

    LIBRARY_TYPE
        Typically "user" for a personal library or "group" for a group library.

How It Works
------------
1. Connects to the user's Zotero library through the Zotero Web API.
2. Loads existing Zotero collections and linked PDF attachments.
3. Recursively scans the specified ROOT_FOLDER for PDF files.
4. Creates any missing collections in Zotero to mirror the local folder structure.
5. Prevents duplicate imports by checking existing linked attachment paths.
6. Attempts to extract a DOI from each PDF.
7. If a DOI is found:
       - Retrieves publication metadata from Crossref.
       - Creates a Zotero Journal Article item with available metadata
         (authors, title, journal, year, DOI, etc.).
8. If a DOI cannot be identified:
       - Creates a generic Zotero Document item using the PDF filename.
9. Creates a linked PDF attachment pointing to the original file location.
10. Leaves all PDFs in their original location; no files are copied,
    moved, renamed, or uploaded.

Notes
-----
- The local folder structure remains the authoritative source of organization.
- Zotero collections act as a mirrored view of that structure.
- PDFs remain linked to their original filesystem locations.
- Journal articles with identifiable DOIs are imported with rich bibliographic
  metadata whenever possible.
- PDFs without identifiable metadata are still added to Zotero to maintain a
  complete mirror of the source.
"""

import re
from pathlib import Path

import pymupdf
import requests
from pyzotero import zotero

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT_FOLDER = Path(
    "temp"
)  # User provided path to the folder that needs to be synced with Zotero

ROOT_COLLECTION_NAME = "temp"  # User provided name for the root collection in Zotero

LIBRARY_ID = "11111111"  # Ask user to provide their Zotero library ID (CAUTION: Do not push this ID to public repositories)
API_KEY = "YOUR_API_KEY"  # Ask user to provide their Zotero API key (CAUTION: Do not push this key to public repositories)
LIBRARY_TYPE = (
    "user"  # Assumes a user library; change to "group" if using a group library
)

PDF_EXTENSIONS = {".pdf"}

USE_LABD = False  # Set to True if using Linked Attachment Base Directory (LABD) in Zotero; 
# this will store paths relative to ROOT_FOLDER. Set to False to store absolute paths.
# Caution : set LABD setting in Zotero before running this script for correct file linking.

# =====================================================
# COLLECTION HELPERS
# =====================================================


def get_or_create_collection(name, parent_key=None):

    lookup_key = (parent_key, name)

    if lookup_key in collection_lookup:
        return collection_lookup[lookup_key]

    print(f"Creating collection: {name}")

    payload = {"name": name}

    if parent_key:
        payload["parentCollection"] = parent_key

    result = zot.create_collections([payload])

    success = result["successful"]["0"]

    if isinstance(success, dict):
        new_key = success["key"]
    else:
        new_key = success

    collection_lookup[lookup_key] = new_key

    return new_key


def ensure_collection_path(folder_path):

    rel_parts = folder_path.relative_to(ROOT_FOLDER).parts

    parent = ROOT_COLLECTION_KEY

    for part in rel_parts:
        parent = get_or_create_collection(name=part, parent_key=parent)

    return parent


# =====================================================
# DOI EXTRACTION
# =====================================================

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


def extract_doi_from_pdf(pdf_path):

    try:
        doc = pymupdf.open(pdf_path)

        text = ""

        pages_to_scan = min(5, len(doc))

        for i in range(pages_to_scan):
            text += doc[i].get_text()

        doc.close()

        match = DOI_PATTERN.search(text)

        if match:
            return match.group(0)

    except Exception:
        pass

    return None


# =====================================================
# CROSSREF LOOKUP
# =====================================================


def get_crossref_metadata(doi):

    url = f"https://api.crossref.org/works/{doi}"

    try:
        response = requests.get(
            url, timeout=20, headers={"User-Agent": "zotero-folder-sync/1.0"}
        )

        response.raise_for_status()

        return response.json()["message"]

    except Exception as ex:
        print(f"Crossref lookup failed for DOI: {doi}")

        print(ex)

        return None


# =====================================================
# PDF LINKING
# =====================================================


def pdf_already_linked(path):

    if USE_LABD:

        relative_path = (
            path
            .relative_to(ROOT_FOLDER)
            .as_posix()
        )

        zotero_path = f"attachments:{relative_path}"

    else:

        zotero_path = str(path)

    return zotero_path in existing_paths


def create_generic_document(pdf_path, collection_key):

    document = {
        "itemType": "document",
        "title": pdf_path.stem,
        "collections": [collection_key],
    }

    response = zot.create_items([document])

    success = response["successful"]["0"]

    if isinstance(success, dict):
        return success["key"]

    return success


def add_pdf(pdf_path, collection_key):

    print(f"Processing: {pdf_path.name}")

    doi = extract_doi_from_pdf(pdf_path)

    # =================================================
    # CASE 1: DOI FOUND
    # =================================================

    if doi:
        print(f"  DOI found: {doi}")

        metadata = get_crossref_metadata(doi)

        if metadata:
            title = pdf_path.stem

            if metadata.get("title"):
                title = metadata["title"][0]

            journal = ""

            if metadata.get("container-title"):
                journal = metadata["container-title"][0]

            article = {
                "itemType": "journalArticle",
                "title": title,
                "publicationTitle": journal,
                "DOI": doi,
                "collections": [collection_key],
            }

            # publication year

            if "published-print" in metadata:
                article["date"] = str(metadata["published-print"]["date-parts"][0][0])

            elif "published-online" in metadata:
                article["date"] = str(metadata["published-online"]["date-parts"][0][0])

            # authors

            creators = []

            for author in metadata.get("author", []):
                creators.append(
                    {
                        "creatorType": "author",
                        "firstName": author.get("given", ""),
                        "lastName": author.get("family", ""),
                    }
                )

            article["creators"] = creators

            response = zot.create_items([article])

            success = response["successful"]["0"]

            if isinstance(success, dict):
                parent_key = success["key"]
            else:
                parent_key = success

            print("  Created Journal Article")

        else:
            print("  DOI found but metadata lookup failed")

            parent_key = create_generic_document(pdf_path, collection_key)

    # =================================================
    # CASE 2: DOI NOT FOUND
    # =================================================

    else:
        print("  DOI not found, creating generic document")

        parent_key = create_generic_document(pdf_path, collection_key)

    # =================================================
    # ATTACH PDF
    # =================================================

    if USE_LABD:
        # Store path relative to ROOT_FOLDER.
        # This allows Zotero's Linked Attachment Base Directory
        # to resolve the file correctly on different operating systems.

        relative_path = pdf_path.relative_to(ROOT_FOLDER).as_posix()

        zotero_path = f"attachments:{relative_path}"

    else:
        # Store absolute path (original behaviour)

        zotero_path = str(pdf_path)

    attachment = {
        "itemType": "attachment",
        "parentItem": parent_key,
        "linkMode": "linked_file",
        "title": pdf_path.name,
        "path": zotero_path,
        "contentType": "application/pdf",
    }

    zot.create_items([attachment])

    existing_paths.add(zotero_path)

    print("  PDF linked")


# =====================================================
# MAIN LOOP
# =====================================================


def check_required_user_config():

    if not ROOT_FOLDER.exists():
        raise ValueError(f"Root folder does not exist: {ROOT_FOLDER}")

    if not ROOT_COLLECTION_NAME:
        raise ValueError("Please provide a valid Zotero root collection name")

    if not LIBRARY_ID or LIBRARY_ID == "11111111":
        raise ValueError("Please provide a valid Zotero library ID")

    if not API_KEY or API_KEY == "YOUR_API_KEY":
        raise ValueError("Please provide a valid Zotero API key")


if __name__ == "__main__":
    # Check user configuration
    check_required_user_config()

    # Initialize Zotero API client
    zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)

    print("Loading existing collections...")

    all_collections = zot.all_collections()

    # cache:
    # (parent_key, collection_name) -> collection_key

    collection_lookup = {}

    for c in all_collections:
        key = c["key"]

        data = c["data"]

        parent = data.get("parentCollection")

        if parent is False:
            parent = None

        name = data["name"]

        collection_lookup[(parent, name)] = key

    print(f"Loaded {len(collection_lookup)} collections")

    # Ensure root collection exists
    ROOT_COLLECTION_KEY = get_or_create_collection(
        ROOT_COLLECTION_NAME, parent_key=None
    )

    print(f"Using root Zotero collection: {ROOT_COLLECTION_NAME}")

    # =====================================================
    # LOAD ALL EXISTING ATTACHMENTS
    # =====================================================

    print("Loading existing attachment paths...")

    existing_paths = set()

    items = zot.everything(zot.top())

    for item in items:
        data = item.get("data", {})

        if data.get("itemType") == "attachment":
            path = data.get("path")

            if path:
                existing_paths.add(path)

    print(f"Loaded {len(existing_paths)} existing attachments")

    pdfs = list(ROOT_FOLDER.rglob("*.pdf"))

    print(f"\nFound {len(pdfs)} PDFs")

    for pdf in pdfs:
        if pdf_already_linked(pdf):
            print(f"Skipping existing: {pdf.name}")
            continue

        collection_key = ensure_collection_path(pdf.parent)

        try:
            add_pdf(pdf_path=pdf, collection_key=collection_key)

        except Exception as ex:
            print()
            print("ERROR")
            print(pdf)
            print(ex)
            print()

    print("\nFinished.")
