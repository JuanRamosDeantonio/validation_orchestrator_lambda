from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class LambdaResult(BaseModel):
    """
    Resultado de una invocación de Lambda.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    lambda_name: Optional[str] = None


class MarkdownDocument(BaseModel):
    """
    Representa un archivo Markdown con su ruta y contenido.
    """
    path: str
    content: str

    def contains(self, value: str) -> bool:
        return value in self.content



@dataclass
class MarkdownResponse:
    """Respuesta de markdown desde las lambdas."""
    success: bool
    markdown_content: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    source: Optional[str] = None  # 'structure' o 'file'
    files: Optional[list[str]] = None


@dataclass
class S3Result:
    """Resultado de operación S3."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class RuleData(BaseModel):
    """
    Modelo que representa una regla de validación semántica o estructural.
    """

    id: str = Field(..., description="Identificador único de la regla.")
    documentation: Optional[str] = Field(default=None, description="nombre de la regla.")
    type: Optional[str] = Field(default=None, description="Tipo de regla (estructura, contenido, semántica, etc.).")  # ✅ CAMBIO: Permite None
    description: str = Field(..., description="Descripción general de la regla.")
    criticality: Optional[str] = Field(default=None, description="Criticidad o severidad de la regla.")  # ✅ CAMBIO: Permite None
    references: Optional[str] = Field(default=None, description="Cadena de referencias separadas por coma (ej: 'patron1,valor,patron2').")
    markdownfiles: List["MarkdownDocument"] = Field(default_factory=list, description="Archivos Markdown relacionados con la regla.")
    explanation: Optional[str] = Field(default=None, description="Explicación adicional sobre la lógica de la regla.")
    tags: List[str] = Field(default_factory=list, description="Etiquetas asociadas para filtrado o agrupación.")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('explanation', mode='before')  # ✅ NUEVO: Convierte integers a strings
    @classmethod
    def convert_explanation_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return str(v)
        return v

    @property
    def parsed_references(self) -> List[str]:
        """
        Devuelve la cadena `references` separada por comas como lista, limpiando espacios.
        Si `references` es None, retorna una lista vacía.
        """
        return [r.strip() for r in self.references.split(",")] if self.references else []
