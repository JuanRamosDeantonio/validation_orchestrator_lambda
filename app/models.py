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
    id: str
    description: str
    documentation: Optional[str] = None
    type: Optional[str] = None
    criticality: Optional[str] = None
    references: Optional[str] = None
    markdownfiles: List["MarkdownDocument"] = field(default_factory=list)
    explanation: Optional[str] = None
    projects: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # NUEVO: lista opcional de errores generados a mano
    errors: Optional[List[str]] = field(default=None)

    def __post_init__(self):
        # Convierte integers a strings para explanation
        if self.explanation is not None and isinstance(self.explanation, int):
            self.explanation = str(self.explanation)

    @property
    def parsed_references(self) -> List[str]:
        return [r.strip() for r in self.references.split(",")] if self.references else []

    # Helpers opcionales
    def add_error(self, msg: str) -> None:
        if self.errors is None:
            self.errors = []
        self.errors.append(str(msg))

    def has_errors(self) -> bool:
        return bool(self.errors)

    def clear_errors(self) -> None:
        self.errors = None