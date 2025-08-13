import hashlib
import os
from typing import Tuple


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def compute_checksum_and_save(fileobj, dest_dir: str, filename: str) -> Tuple[str, str, int]:
    """
    Save the uploaded file to ATTACHMENTS_DIR using a checksum-based path.
    Returns (storage_key, checksum, bytes_written)
    """
    ensure_dir(dest_dir)

    hasher = hashlib.sha256()
    tmp_path = os.path.join(dest_dir, f".{filename}.part")
    size = 0
    with open(tmp_path, "wb") as out:
        for chunk in iter(lambda: fileobj.read(1024 * 1024), b""):
            hasher.update(chunk)
            size += len(chunk)
            out.write(chunk)
    checksum = hasher.hexdigest()
    subdir = os.path.join(dest_dir, checksum[:2], checksum[2:4])
    ensure_dir(subdir)
    storage_key = os.path.join(checksum[:2], checksum[2:4], checksum + "_" + filename)
    final_path = os.path.join(dest_dir, storage_key)
    os.replace(tmp_path, final_path)
    return storage_key, checksum, size


def resolve_path(dest_dir: str, storage_key: str) -> str:
    return os.path.join(dest_dir, storage_key)

