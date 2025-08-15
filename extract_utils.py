import os
import shutil
import tarfile
import zipfile
import stat
from pathlib import Path

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def cleanup_dirs(directories):
    for directory in directories:
        if directory.exists():
            shutil.rmtree(directory, onerror=remove_readonly)
        directory.mkdir(parents=True, exist_ok=True)

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        print(f"Failed to extract zip {zip_path}: {e}")

def extract_nested_tar(file_path, extract_to, recurse=True):
    try:
        with tarfile.open(file_path, 'r:*') as tar:
            tar.extractall(extract_to)
        if recurse:
            for item in extract_to.rglob("*.tar"):
                nested_extract_dir = extract_to / f"nested_{item.stem}"
                nested_extract_dir.mkdir(parents=True, exist_ok=True)
                extract_nested_tar(item, nested_extract_dir, recurse=False)
    except Exception as e:
        print(f"Failed to extract {file_path}: {e}")
