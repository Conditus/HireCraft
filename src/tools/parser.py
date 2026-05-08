# Module for pdf parsing (just as simple as possible)

import os
from typing import Optional, Union
from pathlib import Path
from dataclasses import dataclass
import fitz

@dataclass
class PDFResult:
    text: str
    metadata: dict
    file_path: str

class PDFParser:
    def __init__(self, backend: str = "fitz"):
        """
        Args:
            backend: fitz (PyMuPDF)
        """
        self.backend = backend
        
    def parse(
        self, 
        source: Union[str, Path, bytes],
        pages: Optional[list[int]] = None
    ) -> PDFResult:
        """
        Extracts text from PDF.
        
        Args:
            source: file path or bytes
            pages: pages to parse (None = all)
            
        Returns:
            PDFResult with text and meta
        """
        if self.backend == "fitz":
            return self._parse_with_fitz(source, pages)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _parse_with_fitz(self, source, pages) -> PDFResult:
        try:
            if isinstance(source, (str, Path)):
                doc = fitz.open(str(source))
                file_path = str(source)
            else:
                doc = fitz.open(stream=source, filetype="pdf")
                file_path = "<bytes>"
            
            text_blocks = []
            page_range = pages if pages else range(len(doc))
            
            for page_num in page_range:
                if page_num < len(doc):
                    page = doc[page_num]
                    text_blocks.append(page.get_text())
            
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
            }
            
            doc.close()
            
            return PDFResult(
                text="\n\n".join(text_blocks).strip(),
                metadata=metadata,
                file_path=file_path
            )
            
        except Exception as e:
            raise RuntimeError(f"Parsing error: {e}")