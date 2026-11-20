"""Disponibiliza o acervo local distribuído em um único arquivo ZIP."""
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
import os
import zipfile


def preparar_dados():
    root = Path(__file__).resolve().parent
    archive = root / 'dados_painel.zip'
    fingerprint = sha256(archive.read_bytes()).hexdigest()
    marker = root / '.dados_instalados'
    if marker.exists() and marker.read_text() == fingerprint:
        return
    with zipfile.ZipFile(archive) as data:
        for entry in data.infolist():
            relative = Path(entry.filename)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Caminho inválido no acervo do painel.')
            if entry.is_dir():
                continue
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
                temporary.write(data.read(entry))
                temporary_path = Path(temporary.name)
            try:
                os.replace(temporary_path, target)
            finally:
                temporary_path.unlink(missing_ok=True)
    with NamedTemporaryFile(mode='w', dir=root, delete=False) as temporary:
        temporary.write(fingerprint)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, marker)
