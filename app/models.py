"""
models.py - Modelos de datos para el validation orchestrator
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RuleData(BaseModel):
    """
    Representa una regla de validación cargada desde sync.
    """
    id: str = Field(..., description="Identificador único de la regla.")
    description: str = Field(..., description="Descripción de la validación a realizar.")
    type: str = Field(..., description="Tipo de regla (estructura, contenido, semántica).")
    references: List[str] = Field(..., description="Lista de artefactos involucrados.")
    criticality: str = Field("media", description="Nivel de criticidad (baja, media, alta).")
    explanation: Optional[str] = Field(None, description="Detalle adicional o ejemplo de la regla.")

    def summary(self) -> str:
        """Devuelve un resumen breve de la regla."""
        return f"[{self.id}] {self.description} ({self.type}, {self.criticality})"

class ValidationResult(BaseModel):
    """
    Resultado de validación de una regla individual.
    """
    rule_id: str
    rule_type: str
    rule_criticality: str
    resultado: str  # CUMPLE/NO_CUMPLE/PARCIAL
    confianza: str  # Alta/Media/Baja
    explicacion: str
    chunks_processed: int = 1
    content_size_analyzed: int = 0
    model_used: Optional[str] = None

class ConsolidatedResult(BaseModel):
    """
    Resultado consolidado de todas las validaciones.
    CORREGIDO: Agregar campos que se estaban asignando dinámicamente.
    """
    passed: bool
    message: str
    total_rules_processed: int
    critical_failures: int
    medium_failures: int
    low_failures: int
    system_errors: int
    execution_time_ms: Optional[float] = None
    
    # NUEVOS CAMPOS - Corrigen Bug #2
    detailed_metrics: Optional[Dict[str, Any]] = None
    decision_factors: Optional[List[Dict[str, Any]]] = None
    confidence_level: Optional[str] = None

class ChunkData(BaseModel):
    """
    Representa un chunk de contenido procesado.
    """
    content: str
    chunk_type: str
    size_tokens: int
    rule_focus: bool = False

class RepositoryContent(BaseModel):
    """
    Contenido del repositorio obtenido de las lambdas.
    """
    structure: Dict[str, Any]
    files: Dict[str, str]  # file_path: content
    repository_url: str

# NUEVOS ENUMS para mejor type safety y legibilidad
class ValidationResultStatus(Enum):
    """Estados posibles de validación."""
    COMPLIES = "CUMPLE"
    DOES_NOT_COMPLY = "NO_CUMPLE"
    PARTIAL = "PARCIAL"

class ConfidenceLevel(Enum):
    """Niveles de confianza."""
    HIGH = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"

class RuleType(Enum):
    """Tipos de reglas de validación."""
    STRUCTURAL = "estructura"
    CONTENT = "contenido"
    SEMANTIC = "semántica"

class Criticality(Enum):
    """Niveles de criticidad."""
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baja"