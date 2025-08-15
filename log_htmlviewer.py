from pathlib import Path
from collections import defaultdict
import webbrowser
import os
import zipfile
import tempfile

from extract_utils import extract_zip, extract_nested_tar, cleanup_dirs
from html_writer import write_log_page, generate_index_html, generate_keyword_pages, label_to_filepath
from helpers import sanitize_filename
from search_utils import prompt_keywords
from html_writer import keyword_pages

OUTPUT_DIR = Path("log_pages")
TEMP_DIR = Path("temp_logs")
EXTRACTED_ROOT = Path("./unzipped_logs")
cleanup_dirs([OUTPUT_DIR, TEMP_DIR, EXTRACTED_ROOT])

zip_files = list(Path('.').glob('*.zip'))
print('Path(''):', Path('.'))
if not zip_files:
    print("No zip files found.")
    exit(1)

if len(zip_files) == 1:
    ZIP_INPUT = zip_files[0]
    print(f"Using zip file: {ZIP_INPUT.name}")
else:
    print("\nAvailable ZIP files:")
    for idx, zf in enumerate(zip_files, 1):
        print(f"[{idx}] {zf.name}")
    
    while True:
        try:
            choice = int(input("\nChoose a ZIP file by number: "))
            if 1 <= choice <= len(zip_files):
                ZIP_INPUT = zip_files[choice - 1]
                print(f"\nSelected: {ZIP_INPUT.name}")
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def collect_and_generate_pages(root_path, keywords):
    grouped_entries = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in {"pstore", "logd"}]
        for filename in filenames:
            file_path = Path(dirpath) / filename
            rel_path = file_path.relative_to(root_path)
            label = str(rel_path)
            top_folder = Path(label).parts[0] if len(Path(label).parts) > 1 else "root"

            if filename.endswith(".tar") or filename.endswith(".tar.gz"):
                extract_target = TEMP_DIR / sanitize_filename(rel_path)
                extract_target.mkdir(parents=True, exist_ok=True)
                extract_nested_tar(file_path, extract_target)
                for nested_file in extract_target.rglob("*"):
                    if nested_file.is_file():
                        nested_label = f"{label}/{nested_file.relative_to(extract_target)}"
                        link = write_log_page(nested_file, nested_label, keywords, OUTPUT_DIR)
                        if link:
                            grouped_entries[top_folder].append((nested_label, link))
                            
            elif filename.endswith(".zip"):
                zip_entries = extract_and_collect_zip(file_path, label)
                for zip_file, zip_label in zip_entries:
                    link = write_log_page(zip_file, zip_label, keywords, OUTPUT_DIR)
                    if link:
                        grouped_entries[top_folder].append((zip_label, link))
            
            else:
                link = write_log_page(file_path, label, keywords, OUTPUT_DIR)
                if link:
                    grouped_entries[top_folder].append((label, link))
    return grouped_entries


def extract_and_collect_zip(zip_path: Path, parent_label: str):
    temp_dir = tempfile.mkdtemp()
    extracted_files = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f"Extracting ZIP: {zip_path}")
            zip_ref.extractall(temp_dir)

        temp_dir_path = Path(temp_dir)
        found = list(temp_dir_path.rglob("*"))
        print(f"  -> Found {len(found)} files inside ZIP: {zip_path.name}")

        for file in found:
            if file.is_file():
                print(f"  - Checking file: {file}")
                if file.suffix.lower() in [".txt", ".log", ".cfg", ".ini", ".csv"]:
                    nested_label = f"{parent_label}/{file.relative_to(temp_dir_path)}"
                    extracted_files.append((file, str(nested_label)))
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
    finally:
        # Optionally clean up
        pass
        # shutil.rmtree(temp_dir)

    print(f"  -> Returning {len(extracted_files)} valid text files.")
    return extracted_files


if __name__ == "__main__":
    extract_zip(ZIP_INPUT, EXTRACTED_ROOT)
    grouped_entries = collect_and_generate_pages(EXTRACTED_ROOT, [])
    generate_index_html(grouped_entries)
    webbrowser.open("index.html")

    while True:
        keywords = prompt_keywords()
        if not keywords:
            break
        for group in grouped_entries.values():
            for label, _ in group:
                log_path = label_to_filepath.get(label)
                if log_path and log_path.exists():
                    write_log_page(log_path, label, keywords, OUTPUT_DIR)
        generate_keyword_pages(OUTPUT_DIR)
        for page in keyword_pages:
            webbrowser.open(page)
        if input("Search more keywords? (y/n): ").strip().lower() != 'y':
            break
