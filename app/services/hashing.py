import hashlib

def get_file_hash(file_path: str) -> str:
    # Genera un hash SHA-256 leyendo el archivo por pedazos de 4KB.
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()