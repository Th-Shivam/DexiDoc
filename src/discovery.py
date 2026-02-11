from pathlib import Path
from dataclasses import dataclass
from typing import Iterator, List

@dataclass
class FileInfo:
    path: Path
    size: int

class FileScanner:
    def __init__(self, base_path: Path, excludes: List[str] = None, extensions: List[str] = None):
        self.base_path = base_path
        self.excludes = excludes or []
        self.extensions = extensions or ['.pdf', '.txt', '.md', '.doc', '.docx']
    
    def scan(self) -> Iterator[FileInfo]:
        for item in self.base_path.rglob('*'):
            if not item.is_file():
                continue
            
            if any(exclude in str(item) for exclude in self.excludes):
                continue
            
            if self.extensions and item.suffix.lower() not in self.extensions:
                continue
            
            yield FileInfo(path=item, size=item.stat().st_size)
