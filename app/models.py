from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LambdaResult:
    """
    Resultado de una invocación de Lambda.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    lambda_name: Optional[str] = None


@dataclass
class MarkdownDocument:
    """
    Representa un archivo Markdown con su ruta y contenido.
    """
    path: str
    content: str
    
    def contains(self, value: str) -> bool:
        return value in self.content


FileEntry = Tuple[str, bool]  # (ruta_relativa, iswiki)

@dataclass(slots=True)
class MarkdownResponse:
    """Respuesta de markdown desde las lambdas."""
    success: bool
    markdown_content: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    source: Optional[str] = None  # 'structure' o 'file'
    files: Optional[List[FileEntry]] = None  # [(path, iswiki)]


@dataclass
class S3Result:
    """Resultado de operación S3."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class RuleData:
    """
    Modelo que representa una regla de validación semántica o estructural.
    """
    id: str  # Identificador único de la regla
    description: str  # Descripción general de la regla
    documentation: Optional[str] = None  # nombre de la regla
    type: Optional[str] = None  # Tipo de regla (estructura, contenido, semántica, etc.)
    criticality: Optional[str] = None  # Criticidad o severidad de la regla
    references: Optional[str] = None  # Cadena de referencias separadas por coma (ej: 'patron1,valor,patron2')
    markdownfiles: List[MarkdownDocument] = field(default_factory=list)  # Archivos Markdown relacionados con la regla
    explanation: Optional[str] = None  # Explicación adicional sobre la lógica de la regla
    projects: Optional[str] = None
    tags: List[str] = field(default_factory=list)  # Etiquetas asociadas para filtrado o agrupación
    
    def __post_init__(self):
        """Validación y conversión de tipos después de la inicialización."""
        # Convierte integers a strings para explanation (equivalente al field_validator)
        if self.explanation is not None and isinstance(self.explanation, int):
            self.explanation = str(self.explanation)
    
    @property
    def parsed_references(self) -> List[str]:
        """
        Devuelve la cadena `references` separada por comas como lista, limpiando espacios.
        Si `references` es None, retorna una lista vacía.
        """
        return [r.strip() for r in self.references.split(",")] if self.references else []