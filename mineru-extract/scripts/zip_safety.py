import pathlib
import stat
import zipfile


def extract_zip_safely(archive: zipfile.ZipFile, out_dir: pathlib.Path) -> None:
    root = out_dir.resolve()
    for member in archive.infolist():
        target = (root / member.filename).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"Unsafe archive path: {member.filename}")
        if stat.S_ISLNK(member.external_attr >> 16):
            raise ValueError(f"Archive links are not supported: {member.filename}")
    archive.extractall(root)
