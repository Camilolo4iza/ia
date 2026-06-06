import os
from pathlib import Path
from typing import List, Dict, Any
from src.config import RAW_DATA_DIR

class DocumentLoader:
    """
    Carga documentos de texto (.txt, .md) desde el directorio de datos raw.
    """
    def __init__(self, data_dir: Path = RAW_DATA_DIR):
        self.data_dir = data_dir

    def load(self) -> List[Dict[str, Any]]:
        """
        Carga todos los archivos válidos del directorio raw.
        Retorna una lista de diccionarios con la estructura:
        {
            'content': str,
            'metadata': {
                'source_file': str,
                'topic': str,
                'path': str
            }
        }
        """
        documents = []
        if not self.data_dir.exists():
            return documents

        for file_path in self.data_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix in [".txt", ".md"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Extraer el tema a partir del nombre del archivo
                    topic = file_path.stem.replace("_", " ").title()
                    
                    documents.append({
                        "content": content,
                        "metadata": {
                            "source_file": file_path.name,
                            "topic": topic,
                            "path": str(file_path.absolute())
                        }
                    })
                except Exception as e:
                    print(f"Error al cargar {file_path.name}: {str(e)}")
        
        return documents
