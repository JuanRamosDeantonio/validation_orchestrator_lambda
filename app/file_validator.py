"""
Validador de estructura de archivos que aplica reglas con expresiones regulares.

Este módulo proporciona funcionalidad para validar la estructura de archivos
contra reglas definidas, soportando diferentes tipos de validación.
"""

import logging
import os
import fnmatch
from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Tipos de datos
FileEntry = Tuple[str, bool]  # (ruta_relativa, iswiki)

# Constantes
PATH_EXTRACT_PLACEHOLDER = '{path_extract}'
DEFAULT_PATH_PART = 0
DEFAULT_POSITION = 0
DEFAULT_SEPARATOR = '-'
DEFAULT_DIRECTION = 'left_to_right'
DEFAULT_MISSING_BEHAVIOR = 'error'

# Configurar logging del módulo
logger = logging.getLogger(__name__)


# ================================
# ENUMS Y CONSTANTES
# ================================

class MissingPathBehavior(Enum):
    """Comportamiento cuando no se encuentran archivos en references."""
    ERROR = 'error'      # Genera error si no encuentra archivos
    WARNING = 'warning'  # Solo notifica sin generar error
    IGNORE = 'ignore'    # Omite la regla sin procesamiento


class ExtractionDirection(Enum):
    """Dirección para extracción de información de rutas."""
    LEFT_TO_RIGHT = 'left_to_right'  # Extrae de izquierda a derecha (normal)
    RIGHT_TO_LEFT = 'right_to_left'  # Extrae de derecha a izquierda (reverso)


class ValidationType(Enum):
    """Tipos de validación soportados."""
    EXACT_MATCH = 'exact_match'                        # Búsqueda exacta de archivo específico
    DYNAMIC_PATTERN_FROM_PATH = 'dynamic_pattern_from_path'  # Patrón dinámico basado en extracción de ruta
    CONDITIONAL_MULTIPLE_PATTERNS = 'conditional_multiple_patterns'  # Múltiples patrones condicionales
    AT_LEAST_ONE_PATTERN = 'at_least_one_pattern'      # Al menos un archivo que coincida con patrón wildcard
    CONDITIONAL_EXTENSION_VALIDATION = 'conditional_extension_validation'  # Validación de extensión basada en nombre de archivo


# ================================
# CLASES DE CONFIGURACIÓN
# ================================

@dataclass
class PathExtractionConfig:
    """
    Configuración para extracción de información de rutas de archivos.
    
    Attributes:
        separator: Carácter que separa las partes (ej: '-', '_', '.')
        position: Posición del elemento a extraer (0=primero, -1=último)
        path_part: Índice de la parte de la ruta a analizar (0=primera carpeta)
        direction: Dirección de extracción (left_to_right o right_to_left)
    
    Examples:
        Para "empresa-modulo-PROYECTO-version/src/file.txt":
        
        PathExtractionConfig(separator='-', position=2, path_part=0)
        → Extrae "PROYECTO"
        
        PathExtractionConfig(separator='-', position=1, direction='right_to_left', path_part=0)  
        → Extrae "PROYECTO" (segundo desde la derecha)
    """
    separator: str = DEFAULT_SEPARATOR
    position: int = DEFAULT_POSITION  
    path_part: int = DEFAULT_PATH_PART
    direction: str = DEFAULT_DIRECTION
    
    def __post_init__(self):
        """Validar configuración después de inicialización."""
        if self.direction not in [e.value for e in ExtractionDirection]:
            raise ValueError(f"direction debe ser uno de: {[e.value for e in ExtractionDirection]}")


@dataclass
class NamingRule:
    """
    Regla de nomenclatura para validación condicional de extensiones.
    
    Attributes:
        contains: Término que debe contener el nombre del archivo
        required_extension: Extensión requerida si coincide
        case_sensitive: Si la búsqueda es sensible a mayúsculas
        exclude: Lista de términos que no deben estar presentes
        is_default: Si es la regla por defecto cuando no hay coincidencias
    
    Examples:
        NamingRule(contains="soapui", required_extension=".xml", case_sensitive=False)
        NamingRule(contains="postman", required_extension=".json", exclude=["soapui"])
        NamingRule(is_default=True, required_extension=".txt")
    """
    required_extension: str
    contains: Optional[str] = None
    case_sensitive: bool = False
    exclude: Optional[List[str]] = None
    is_default: bool = False
    
    def __post_init__(self):
        """Validar configuración después de inicialización."""
        if not self.is_default and not self.contains:
            raise ValueError("NamingRule debe tener 'contains' o 'is_default=True'")
        if self.exclude is None:
            self.exclude = []


@dataclass
class MarkdownDocument:
    """Documento markdown asociado a una regla."""
    path: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RuleData:
    """
    Modelo que representa una regla de validación semántica o estructural.
    
    Soporta diferentes tipos de validación:
    - exact_match: Búsqueda exacta de archivo específico
    - dynamic_pattern_from_path: Patrón dinámico basado en extracción de ruta
    - conditional_multiple_patterns: Múltiples patrones condicionales
    - at_least_one_pattern: Al menos un archivo que coincida con patrón wildcard
    - conditional_extension_validation: Validación de extensión basada en nombre de archivo
    """
    
    # CAMPOS ORIGINALES
    id: str
    description: str
    documentation: Optional[str] = None
    type: Optional[str] = None  # Para validación estructural debe ser "estructura"
    criticality: Optional[str] = None
    references: Optional[str] = None  # Patrones glob para filtrar archivos
    markdownfiles: List[MarkdownDocument] = field(default_factory=list)
    explanation: Optional[str] = None
    projects: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    errors: Optional[List[str]] = field(default=None)
    
    # CAMPOS PARA VALIDACIÓN ESTRUCTURAL
    validation_type: Optional[str] = None  # Tipo de validación (usar ValidationType enum values)
    pattern: Optional[str] = None  # Patrón único como "Guion.md" o "*.project"
    patterns: Optional[List[str]] = None  # Múltiples patrones para validación condicional
    path_extraction: Optional[Union[PathExtractionConfig, List[PathExtractionConfig]]] = None
    missing_path_behavior: Optional[str] = None  # 'error', 'warning', 'ignore'
    expected_file_count: Optional[int] = None  # Número exacto de archivos esperados
    naming_rules: Optional[List[NamingRule]] = None  # Reglas de nomenclatura condicional
    isvalidated: bool = False  # Estado de validación
    
    def __post_init__(self):
        """Convierte integers a strings para explanation si es necesario."""
        if self.explanation is not None and isinstance(self.explanation, int):
            self.explanation = str(self.explanation)

    @property
    def parsed_references(self) -> List[str]:
        """Convierte references string a lista separada por comas."""
        return [r.strip() for r in self.references.split(",")] if self.references else []

    # MÉTODOS DE UTILIDAD EXISTENTES
    def add_error(self, msg: str) -> None:
        """Agrega un mensaje de error a la lista de errores."""
        if self.errors is None:
            self.errors = []
        self.errors.append(str(msg))

    def has_errors(self) -> bool:
        """Retorna True si la regla tiene errores."""
        return bool(self.errors)

    def clear_errors(self) -> None:
        """Limpia todos los errores de la regla."""
        self.errors = None
    
    # MÉTODOS DE UTILIDAD NUEVOS
    def is_structure_rule(self) -> bool:
        """Retorna True si es una regla de validación estructural."""
        return self.type and self.type.lower() == 'estructura'
    
    def has_validation_config(self) -> bool:
        """Retorna True si tiene configuración de validación (pattern o patterns)."""
        return bool(self.pattern or self.patterns)
    
    def get_validation_summary(self) -> str:
        """Retorna un resumen del estado de validación."""
        if not self.isvalidated:
            return "No validada"
        elif self.has_errors():
            return f"Validada con {len(self.errors)} errores"
        else:
            return "Validada exitosamente"


# ================================
# FUNCIÓN DESERIALIZADORA
# ================================

def deserialize_rule_data(json_data: Dict[str, Any]) -> RuleData:
    """
    Convierte un diccionario JSON a objeto RuleData con objetos tipados.
    
    Maneja la conversión automática de:
    - naming_rules: dict → NamingRule objects
    - path_extraction: dict/list → PathExtractionConfig objects
    
    Args:
        json_data: Diccionario con datos de la regla
        
    Returns:
        Objeto RuleData completamente tipado
        
    Example:
        json_rule = {
            "id": "1.12",
            "validation_type": "conditional_extension_validation",
            "naming_rules": [
                {"contains": "soapui", "required_extension": ".xml"}
            ]
        }
        rule = deserialize_rule_data(json_rule)
    """
    # Crear copia para no modificar el original
    data = json_data.copy()
    
    # Convertir naming_rules de dict a NamingRule objects
    if 'naming_rules' in data and data['naming_rules']:
        naming_rules = []
        for rule_dict in data['naming_rules']:
            if isinstance(rule_dict, dict):
                naming_rules.append(NamingRule(
                    contains=rule_dict.get('contains'),
                    required_extension=rule_dict.get('required_extension', ''),
                    case_sensitive=rule_dict.get('case_sensitive', False),
                    exclude=rule_dict.get('exclude', []),
                    is_default=rule_dict.get('is_default', False)
                ))
            else:
                # Ya es un objeto NamingRule
                naming_rules.append(rule_dict)
        data['naming_rules'] = naming_rules
    
    # Convertir path_extraction de dict a PathExtractionConfig objects
    if 'path_extraction' in data and data['path_extraction']:
        path_ext = data['path_extraction']
        
        if isinstance(path_ext, dict):
            # Configuración única
            data['path_extraction'] = PathExtractionConfig(
                separator=path_ext.get('separator', DEFAULT_SEPARATOR),
                position=path_ext.get('position', DEFAULT_POSITION),
                path_part=path_ext.get('path_part', DEFAULT_PATH_PART),
                direction=path_ext.get('direction', DEFAULT_DIRECTION)
            )
        elif isinstance(path_ext, list):
            # Lista de configuraciones
            configs = []
            for pe_dict in path_ext:
                if isinstance(pe_dict, dict):
                    configs.append(PathExtractionConfig(
                        separator=pe_dict.get('separator', DEFAULT_SEPARATOR),
                        position=pe_dict.get('position', DEFAULT_POSITION),
                        path_part=pe_dict.get('path_part', DEFAULT_PATH_PART),
                        direction=pe_dict.get('direction', DEFAULT_DIRECTION)
                    ))
                else:
                    # Ya es un objeto PathExtractionConfig
                    configs.append(pe_dict)
            data['path_extraction'] = configs
    
    # Crear y retornar objeto RuleData
    return RuleData(**data)


# ================================
# CLASE PRINCIPAL VALIDADOR
# ================================

class FileStructureValidator:
    """
    Validador de estructura de archivos que aplica reglas con expresiones regulares.
    
    Esta clase se encarga de:
    1. Recibir una lista de archivos (FileEntry) que representan la estructura actual
    2. Aplicar reglas de validación de tipo 'estructura' sobre estos archivos
    3. Usar el campo 'references' para filtrado dinámico y 'pattern' para validación
    4. Modificar las reglas in-place agregando errores cuando no cumplan
    5. Marcar las reglas como validadas con el flag isvalidated
    
    Tipos de validación soportados:
    - exact_match: Búsqueda exacta de archivo específico
    - dynamic_pattern_from_path: Patrón dinámico basado en extracción de ruta
    - conditional_multiple_patterns: Múltiples patrones condicionales
    - at_least_one_pattern: Al menos un archivo que coincida con patrón wildcard
    - conditional_extension_validation: Validación de extensión basada en nombre de archivo
    """
    
    def __init__(self) -> None:
        """Inicializa el validador con logger configurado."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._logger.debug("FileStructureValidator inicializado")
    
    def validate_file_structure(
        self, 
        files: List[FileEntry], 
        rules: List[RuleData]
    ) -> None:
        """
        Método principal para validar estructura de archivos contra reglas.
        
        Soporta diferentes tipos de validación:
        - exact_match: Búsqueda exacta de archivo
        - dynamic_pattern_from_path: Patrón dinámico basado en extracción de ruta
        - conditional_multiple_patterns: Múltiples patrones condicionales
        - at_least_one_pattern: Al menos un archivo que coincida con patrón
        - conditional_extension_validation: Validación de extensión basada en nombre
        
        Args:
            files: Lista de tuplas (ruta_relativa, iswiki) representando los archivos
            rules: Lista de objetos RuleData que serán modificados in-place
            
        Raises:
            ValueError: Si files o rules están vacíos o son None
        """
        if not files:
            raise ValueError("La lista de archivos no puede estar vacía")
        if not rules:
            raise ValueError("La lista de reglas no puede estar vacía")
            
        self._logger.info(
            "Iniciando validación de estructura: %d archivos, %d reglas", 
            len(files), len(rules)
        )
        
        try:
            structure_rules = self._filter_structure_rules_with_pattern(rules)
            processed_count = 0
            
            for rule in structure_rules:
                self._process_single_rule(files, rule)
                processed_count += 1
            
            self._logger.info(
                "Validación completada exitosamente: %d reglas procesadas", 
                processed_count
            )
            
        except Exception as exc:
            self._logger.error(
                "Error durante la validación de estructura: %s", 
                exc, exc_info=True
            )
            raise
    
    def _process_single_rule(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Procesa una regla individual según su tipo de validación.
        
        Args:
            files: Lista de archivos disponibles
            rule: Regla a procesar
        """
        validation_type = getattr(rule, 'validation_type', 'exact_match')
        rule_id = getattr(rule, 'id', 'unknown')
        
        self._logger.debug("Procesando regla %s con tipo: %s", rule_id, validation_type)
        
        try:
            if validation_type == 'exact_match':
                self._validate_exact_pattern(files, rule)
            elif validation_type == 'dynamic_pattern_from_path':
                self._validate_dynamic_pattern(files, rule)
            elif validation_type == 'conditional_multiple_patterns':
                self._validate_conditional_multiple_patterns(files, rule)
            elif validation_type == 'at_least_one_pattern':
                self._validate_at_least_one_pattern(files, rule)
            elif validation_type == 'conditional_extension_validation':
                self._validate_conditional_extension(files, rule)
            else:
                self._handle_unknown_validation_type(rule, validation_type)
                
        except Exception as exc:
            self._logger.error(
                "Error procesando regla %s: %s", 
                rule_id, exc, exc_info=True
            )
            rule.isvalidated = False
            rule.add_error(f"Error interno al procesar regla: {exc}")
    
    def _handle_unknown_validation_type(self, rule: RuleData, validation_type: str) -> None:
        """Maneja tipos de validación desconocidos."""
        rule.isvalidated = False
        rule.add_error(f"Tipo de validación desconocido: {validation_type}")
        self._logger.warning(
            "Tipo de validación '%s' no reconocido para regla %s", 
            validation_type, getattr(rule, 'id', 'unknown')
        )
    
    def _filter_structure_rules_with_pattern(self, rules: List[RuleData]) -> List[RuleData]:
        """
        Filtra reglas que son de tipo 'estructura' y tienen un pattern o patterns definido.
        
        Args:
            rules: Lista completa de reglas
            
        Returns:
            Lista de reglas aplicables para validación de patrones
        """
        applicable_rules = []
        
        for rule in rules:
            rule_id = getattr(rule, 'id', 'unknown')
            is_structure = rule.type and rule.type.lower() == 'estructura'
            has_pattern = hasattr(rule, 'pattern') and rule.pattern
            has_patterns = hasattr(rule, 'patterns') and rule.patterns
            
            if is_structure and (has_pattern or has_patterns):
                applicable_rules.append(rule)
                pattern_info = getattr(rule, 'pattern', '') or f"{len(getattr(rule, 'patterns', []))} patrones"
                self._logger.debug(
                    "Regla %s incluida: %s", 
                    rule_id, pattern_info
                )
            else:
                self._logger.debug(
                    "Regla %s omitida: estructura=%s, tiene_pattern=%s, tiene_patterns=%s", 
                    rule_id, is_structure, has_pattern, has_patterns
                )
        
        self._logger.info(
            "Filtradas %d reglas aplicables de %d totales", 
            len(applicable_rules), len(rules)
        )
        return applicable_rules
    
    def _validate_exact_pattern(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Validación de patrón exacto (funcionalidad original).
        Busca literalmente el archivo especificado en rule.pattern
        
        Args:
            files: Lista de archivos disponibles
            rule: Regla con patrón exacto a validar
        """
        # Filtrar archivos usando references si existe
        filtered_files = self._filter_files_by_references(files, rule.references)
        
        # Usar la lógica existente
        self._validate_file_exists_with_pattern(filtered_files, rule)
    
    def _validate_dynamic_pattern(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Validación de patrón dinámico basado en extracción de información de rutas.
        
        Args:
            files: Lista completa de archivos
            rule: Regla con configuración de patrón dinámico
        """
        rule_id = getattr(rule, 'id', 'unknown')
        
        try:
            # 1. Filtrar archivos usando references
            source_files = self._filter_files_by_references(files, rule.references)
            if not source_files:
                return self._handle_no_source_files(rule, rule_id)
            
            self._logger.debug("Regla %s: encontrados %d archivos fuente", rule_id, len(source_files))
            
            # 2. Extraer información de las rutas
            extracted_values = self._extract_values_from_paths(source_files, rule)
            if not extracted_values:
                return self._handle_no_extracted_values(rule, rule_id)
            
            self._logger.debug("Regla %s: extraídos valores %s", rule_id, extracted_values)
            
            # 3. Generar y validar patrones dinámicos
            self._validate_generated_patterns(files, extracted_values, rule)
            
        except Exception as exc:
            self._handle_validation_error(rule, rule_id, exc)
    
    def _validate_conditional_multiple_patterns(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Validación condicional de múltiples patrones obligatorios.
        
        Si no encuentra archivos en references:
        - missing_path_behavior="warning" → Solo notifica
        - missing_path_behavior="error" → Genera error
        - missing_path_behavior="ignore" → Omite regla
        
        Si encuentra archivos, valida que existan TODOS los patrones especificados.
        
        Args:
            files: Lista completa de archivos
            rule: Regla con configuración de patrones múltiples
        """
        rule_id = getattr(rule, 'id', 'unknown')
        
        try:
            # 1. Filtrar archivos usando references
            source_files = self._filter_files_by_references(files, rule.references)
            
            if not source_files:
                return self._handle_missing_conditional_path(rule, rule_id)
            
            self._logger.debug("Regla %s: encontrados %d archivos en ruta condicional", rule_id, len(source_files))
            
            # 2. Extraer información de las rutas
            extracted_values = self._extract_values_from_paths(source_files, rule)
            if not extracted_values:
                return self._handle_no_extracted_values(rule, rule_id)
            
            # 3. Validar todos los patrones múltiples
            self._validate_all_required_patterns(files, extracted_values, rule)
            
        except Exception as exc:
            self._handle_validation_error(rule, rule_id, exc)
    
    def _validate_at_least_one_pattern(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Valida que exista al menos un archivo que coincida con el patrón wildcard.
        
        Usado para casos como "debe haber un archivo .project" donde pattern="*.project"
        
        Args:
            files: Lista completa de archivos
            rule: Regla con patrón wildcard
        """
        rule_id = getattr(rule, 'id', 'unknown')
        pattern = getattr(rule, 'pattern', '')
        
        if not pattern:
            rule.isvalidated = False
            rule.add_error("No se especificó patrón para validar")
            return
        
        try:
            # Filtrar archivos usando references si existe
            filtered_files = self._filter_files_by_references(files, rule.references)
            
            # Buscar archivos que coincidan con el patrón wildcard
            matching_files = self._find_wildcard_matches(filtered_files, pattern)
            
            rule.isvalidated = True
            
            if matching_files:
                self._logger.debug(
                    "Regla %s: encontrados %d archivos que coinciden con '%s': %s",
                    rule_id, len(matching_files), pattern, matching_files
                )
            else:
                error_msg = f"No se encontró ningún archivo que coincida con el patrón '{pattern}'"
                rule.add_error(error_msg)
                self._logger.debug("Regla %s: %s", rule_id, error_msg)
                
        except Exception as exc:
            rule.isvalidated = False
            error_msg = f"Error validando patrón wildcard '{pattern}': {exc}"
            rule.add_error(error_msg)
            self._logger.error("Regla %s: %s", rule_id, error_msg, exc_info=True)
    
    def _validate_conditional_extension(self, files: List[FileEntry], rule: RuleData) -> None:
        """
        Valida extensiones de archivos basado en reglas de nomenclatura condicionales.
        
        Proceso:
        1. Filtra archivos usando references
        2. Para cada archivo, determina qué regla de nomenclatura aplica
        3. Valida que la extensión sea correcta según la regla
        
        Args:
            files: Lista completa de archivos
            rule: Regla con configuración de nomenclatura en 'naming_rules'
        """
        rule_id = getattr(rule, 'id', 'unknown')
        
        try:
            # 1. Filtrar archivos usando references
            filtered_files = self._filter_files_by_references(files, rule.references)
            
            if not filtered_files:
                return self._handle_missing_conditional_path(rule, rule_id)
            
            self._logger.debug("Regla %s: encontrados %d archivos para validación condicional", rule_id, len(filtered_files))
            
            # 2. Obtener reglas de nomenclatura
            naming_rules = self._get_naming_rules(rule)
            if not naming_rules:
                rule.isvalidated = False
                rule.add_error("No se especificaron reglas de nomenclatura")
                return
            
            # 3. Validar cada archivo
            rule.isvalidated = True
            all_valid = True
            
            for file_path, is_wiki in filtered_files:
                file_name = os.path.basename(file_path)
                is_valid = self._validate_single_file_extension(file_name, naming_rules, rule)
                if not is_valid:
                    all_valid = False
            
            if all_valid:
                self._logger.info("Regla %s: todos los archivos tienen extensiones válidas", rule_id)
                
        except Exception as exc:
            self._handle_validation_error(rule, rule_id, exc)
    
    def _handle_no_source_files(self, rule: RuleData, rule_id: str) -> None:
        """Maneja el caso cuando no se encuentran archivos fuente."""
        rule.isvalidated = True
        error_msg = f"No se encontraron archivos que coincidan con references: '{rule.references}'"
        rule.add_error(error_msg)
        self._logger.warning("Regla %s: %s", rule_id, error_msg)
    
    def _handle_no_extracted_values(self, rule: RuleData, rule_id: str) -> None:
        """Maneja el caso cuando no se pueden extraer valores de las rutas."""
        rule.isvalidated = True
        error_msg = "No se pudo extraer información de las rutas de archivos"
        rule.add_error(error_msg)
        self._logger.warning("Regla %s: %s", rule_id, error_msg)
    
    def _handle_validation_error(self, rule: RuleData, rule_id: str, exc: Exception) -> None:
        """Maneja errores durante la validación."""
        rule.isvalidated = False
        error_msg = f"Error en validación dinámica: {exc}"
        rule.add_error(error_msg)
        self._logger.error("Regla %s: %s", rule_id, error_msg, exc_info=True)
    
    def _handle_missing_conditional_path(self, rule: RuleData, rule_id: str) -> None:
        """Maneja el caso cuando no se encuentra la ruta condicional."""
        missing_behavior = getattr(rule, 'missing_path_behavior', DEFAULT_MISSING_BEHAVIOR)
        
        if missing_behavior == MissingPathBehavior.WARNING.value:
            rule.isvalidated = True
            # No agregar error, solo log informativo
            self._logger.info(
                "Regla %s: Ruta condicional '%s' no encontrada (comportamiento: warning)", 
                rule_id, rule.references
            )
        elif missing_behavior == MissingPathBehavior.IGNORE.value:
            rule.isvalidated = False
            self._logger.debug(
                "Regla %s: Ruta condicional omitida (comportamiento: ignore)", 
                rule_id
            )
        else:  # 'error' o comportamiento por defecto
            rule.isvalidated = True
            error_msg = f"Ruta requerida '{rule.references}' no encontrada"
            rule.add_error(error_msg)
            self._logger.warning("Regla %s: %s", rule_id, error_msg)
    
    def _extract_values_from_paths(self, files: List[FileEntry], rule: RuleData) -> List[str]:
        """
        Extrae valores de las rutas de archivos usando configuración de extracción.
        Soporta múltiples configuraciones para buscar en diferentes partes de la ruta.
        
        Args:
            files: Archivos fuente de donde extraer información
            rule: Regla que contiene la configuración de extracción
            
        Returns:
            Lista de valores extraídos únicos
        """
        if not hasattr(rule, 'path_extraction') or not rule.path_extraction:
            self._logger.debug("No hay configuración de extracción de ruta")
            return []
        
        extracted_values = set()  # Usar set para evitar duplicados
        
        for file_path, is_wiki in files:
            extracted = self._extract_from_path_multiple_configs(file_path, rule.path_extraction)
            if extracted:
                extracted_values.add(extracted)
        
        result = list(extracted_values)
        self._logger.debug("Valores extraídos de rutas: %s", result)
        return result
    
    def _extract_from_path_multiple_configs(
        self, 
        file_path: str, 
        extraction_configs: Union[PathExtractionConfig, List[PathExtractionConfig]]
    ) -> Optional[str]:
        """
        Extrae un valor de una ruta usando múltiples configuraciones.
        Intenta cada configuración hasta encontrar un resultado válido.
        
        Args:
            extraction_configs: Configuración única o lista de configuraciones (ya tipadas)
        """
        configs = self._normalize_extraction_configs(extraction_configs)
        
        for config in configs:
            extracted = self._try_extract_from_config(file_path, config)
            if extracted:
                return extracted
        
        self._logger.debug("No se pudo extraer valor de: %s", file_path)
        return None
    
    def _normalize_extraction_configs(
        self, 
        extraction_configs: Union[PathExtractionConfig, List[PathExtractionConfig]]
    ) -> List[PathExtractionConfig]:
        """Convierte configuración única a lista si es necesario."""
        if isinstance(extraction_configs, PathExtractionConfig):
            return [extraction_configs]
        return extraction_configs
    
    def _try_extract_from_config(
        self, 
        file_path: str, 
        config: PathExtractionConfig
    ) -> Optional[str]:
        """Intenta extraer valor usando una configuración específica."""
        extracted = self._extract_from_path_by_position_and_part(file_path, config)
        if extracted:
            self._logger.debug(
                "Extraído '%s' de '%s' usando config %s", 
                extracted, file_path, config
            )
        return extracted
    
    def _extract_from_path_by_position_and_part(
        self, 
        file_path: str, 
        extraction_config: PathExtractionConfig
    ) -> Optional[str]:
        """
        Extrae un valor de una ruta usando configuración de extracción tipada.
        
        Args:
            file_path: Ruta del archivo
            extraction_config: Objeto PathExtractionConfig tipado
            
        Returns:
            Valor extraído o None si no se puede extraer
        """
        path_parts = file_path.split('/')
        if not self._is_valid_path_part(path_parts, extraction_config.path_part):
            return None
        
        target_part = path_parts[extraction_config.path_part]
        parts = target_part.split(extraction_config.separator)
        
        # Aplicar dirección si es necesario
        if extraction_config.direction == ExtractionDirection.RIGHT_TO_LEFT.value:
            parts = parts[::-1]  # Invertir lista
        
        # Normalizar posición negativa a positiva
        position = extraction_config.position
        if position < 0:
            position = len(parts) + position
        
        if self._is_valid_position(parts, position):
            return parts[position].strip()
        
        return None
    
    def _is_valid_path_part(self, path_parts: List[str], path_part: int) -> bool:
        """Verifica si el índice de parte de ruta es válido."""
        return len(path_parts) > path_part
    
    def _is_valid_position(self, parts: List[str], position: int) -> bool:
        """Verifica si el índice de posición es válido."""
        return len(parts) > position
    
    def _validate_generated_patterns(
        self, 
        all_files: List[FileEntry], 
        extracted_values: List[str], 
        rule: RuleData
    ) -> None:
        """
        Valida patrones generados dinámicamente para cada valor extraído.
        """
        rule.isvalidated = True
        rule_id = getattr(rule, 'id', 'unknown')
        
        validation_results = self._check_all_generated_patterns(all_files, extracted_values, rule)
        found_any = any(validation_results)
        
        if found_any:
            self._logger.info("Regla %s: validación dinámica exitosa", rule_id)
    
    def _check_all_generated_patterns(
        self, 
        all_files: List[FileEntry], 
        extracted_values: List[str], 
        rule: RuleData
    ) -> List[bool]:
        """
        Verifica cada patrón generado y retorna lista de resultados.
        
        Returns:
            Lista de booleanos indicando si cada patrón fue encontrado
        """
        results = []
        
        for extracted_value in extracted_values:
            found = self._validate_single_generated_pattern(all_files, extracted_value, rule)
            results.append(found)
        
        return results
    
    def _validate_single_generated_pattern(
        self, 
        all_files: List[FileEntry], 
        extracted_value: str, 
        rule: RuleData
    ) -> bool:
        """
        Valida un patrón generado individual.
        
        Returns:
            True si el archivo fue encontrado, False si no
        """
        rule_id = getattr(rule, 'id', 'unknown')
        generated_pattern = rule.pattern.replace(PATH_EXTRACT_PLACEHOLDER, extracted_value)
        found_file = self._search_exact_file(all_files, generated_pattern)
        
        if found_file:
            self._log_pattern_found(rule_id, found_file, generated_pattern)
            return True
        else:
            self._log_pattern_not_found(rule, rule_id, generated_pattern)
            return False
    
    def _log_pattern_found(self, rule_id: str, found_file: str, pattern: str) -> None:
        """Registra cuando se encuentra un patrón."""
        self._logger.debug(
            "Regla %s: encontrado archivo '%s' para patrón '%s'", 
            rule_id, found_file, pattern
        )
    
    def _log_pattern_not_found(self, rule: RuleData, rule_id: str, pattern: str) -> None:
        """Registra y agrega error cuando no se encuentra un patrón."""
        error_msg = f"Archivo requerido '{pattern}' no encontrado"
        rule.add_error(error_msg)
        self._logger.debug("Regla %s: %s", rule_id, error_msg)
    
    def _validate_all_required_patterns(
        self, 
        all_files: List[FileEntry], 
        extracted_values: List[str], 
        rule: RuleData
    ) -> None:
        """
        Valida que existan TODOS los patrones requeridos para cada valor extraído.
        Incluye validación opcional de conteo exacto de archivos.
        
        Args:
            all_files: Lista completa de archivos donde buscar
            extracted_values: Valores extraídos de las rutas
            rule: Regla con lista de patrones en campo 'patterns'
        """
        rule.isvalidated = True
        rule_id = getattr(rule, 'id', 'unknown')
        patterns = getattr(rule, 'patterns', [])
        
        if not patterns:
            # Fallback al patrón único si no hay lista de patrones
            patterns = [rule.pattern] if hasattr(rule, 'pattern') and rule.pattern else []
        
        if not patterns:
            rule.add_error("No se especificaron patrones para validar")
            return
        
        # Validar conteo exacto si está especificado
        expected_count = getattr(rule, 'expected_file_count', None)
        if expected_count is not None:
            self._validate_exact_file_count(all_files, patterns, extracted_values, expected_count, rule)
        
        # Validar existencia de patrones
        total_missing = 0
        total_found = 0
        
        for extracted_value in extracted_values:
            for pattern_template in patterns:
                found = self._validate_single_pattern_from_template(
                    all_files, extracted_value, pattern_template, rule
                )
                if found:
                    total_found += 1
                else:
                    total_missing += 1
        
        if total_found > 0:
            self._logger.info(
                "Regla %s: validación múltiple completada (%d encontrados, %d faltantes)", 
                rule_id, total_found, total_missing
            )
    
    def _validate_exact_file_count(
        self, 
        all_files: List[FileEntry], 
        patterns: List[str], 
        extracted_values: List[str], 
        expected_count: int, 
        rule: RuleData
    ) -> None:
        """
        Valida que el número total de archivos encontrados sea exactamente el esperado.
        
        Args:
            all_files: Lista completa de archivos
            patterns: Lista de patrones a verificar
            extracted_values: Valores extraídos para generar patrones
            expected_count: Número exacto de archivos esperados
            rule: Regla a actualizar con errores
        """
        # Generar todos los patrones posibles
        generated_patterns = set()
        for extracted_value in extracted_values:
            for pattern_template in patterns:
                generated_pattern = pattern_template.replace(PATH_EXTRACT_PLACEHOLDER, extracted_value)
                generated_patterns.add(generated_pattern)
        
        # Contar archivos que coinciden con algún patrón generado
        matching_files = []
        for file_path, is_wiki in all_files:
            file_name = os.path.basename(file_path)
            if file_name in generated_patterns:
                matching_files.append(file_path)
        
        actual_count = len(matching_files)
        rule_id = getattr(rule, 'id', 'unknown')
        
        if actual_count != expected_count:
            error_msg = f"Se esperaban exactamente {expected_count} archivos, se encontraron {actual_count}"
            rule.add_error(error_msg)
            self._logger.warning("Regla %s: %s", rule_id, error_msg)
        else:
            self._logger.debug(
                "Regla %s: conteo correcto (%d archivos encontrados)", 
                rule_id, actual_count
            )
    
    def _validate_single_pattern_from_template(
        self, 
        all_files: List[FileEntry], 
        extracted_value: str, 
        pattern_template: str, 
        rule: RuleData
    ) -> bool:
        """
        Valida un patrón individual generado desde template.
        
        Returns:
            True si el archivo fue encontrado, False si no
        """
        rule_id = getattr(rule, 'id', 'unknown')
        generated_pattern = pattern_template.replace(PATH_EXTRACT_PLACEHOLDER, extracted_value)
        found_file = self._search_exact_file(all_files, generated_pattern)
        
        if found_file:
            self._logger.debug(
                "Regla %s: encontrado '%s' para patrón '%s'", 
                rule_id, found_file, generated_pattern
            )
            return True
        else:
            error_msg = f"Archivo requerido '{generated_pattern}' no encontrado"
            rule.add_error(error_msg)
            self._logger.debug("Regla %s: %s", rule_id, error_msg)
            return False
    
    def _search_exact_file(self, files: List[FileEntry], pattern: str) -> Optional[str]:
        """
        Busca un archivo que coincida exactamente con el patrón.
        
        Args:
            files: Lista de archivos donde buscar
            pattern: Patrón exacto a buscar
            
        Returns:
            Ruta del archivo encontrado o None
        """
        for file_path, is_wiki in files:
            file_name = os.path.basename(file_path)
            if file_name == pattern:
                return file_path
        
        return None
    
    def _find_wildcard_matches(self, files: List[FileEntry], pattern: str) -> List[str]:
        """
        Busca archivos que coincidan con un patrón wildcard.
        
        Args:
            files: Lista de archivos donde buscar
            pattern: Patrón con wildcards como "*.project" o "config.*"
            
        Returns:
            Lista de rutas de archivos que coinciden
        """
        matching_files = []
        
        # Manejar múltiples patrones separados por coma
        patterns = [p.strip() for p in pattern.split(',')]
        
        for file_path, is_wiki in files:
            file_name = os.path.basename(file_path)
            for single_pattern in patterns:
                if fnmatch.fnmatch(file_name, single_pattern):
                    matching_files.append(file_path)
                    break  # Evitar duplicados si coincide con múltiples patrones
        
        return matching_files
    
    def _validate_file_exists_with_pattern(
        self, 
        files: List[FileEntry], 
        rule: RuleData
    ) -> None:
        """
        Método para validación exacta de archivos.
        Valida que exista exactamente el archivo especificado en rule.pattern
        
        Args:
            files: Lista de archivos donde buscar
            rule: Regla con patrón a validar
        """
        pattern = rule.pattern
        rule_id = getattr(rule, 'id', 'unknown')
        
        try:
            self._logger.debug("Regla %s: validando patrón exacto '%s'", rule_id, pattern)
            
            # 1. Analizar el patrón esperado
            expected_name, expected_extension = self._parse_file_pattern(pattern)
            
            # 2. Buscar archivos en la lista
            exact_matches, similar_files = self._find_matching_files(files, pattern, expected_name)
            
            # 3. Marcar como validada y evaluar resultados
            rule.isvalidated = True
            self._evaluate_and_report_matches(exact_matches, similar_files, pattern, expected_extension, rule)
                
        except Exception as exc:
            self._handle_pattern_validation_error(rule, rule_id, pattern, exc)
    
    def _handle_pattern_validation_error(
        self, 
        rule: RuleData, 
        rule_id: str, 
        pattern: str, 
        exc: Exception
    ) -> None:
        """Maneja errores en validación de patrones."""
        rule.isvalidated = False
        error_msg = f"Error procesando patrón '{pattern}': {exc}"
        rule.add_error(error_msg)
        self._logger.error("Regla %s: %s", rule_id, error_msg, exc_info=True)
    
    def _evaluate_and_report_matches(
        self, 
        exact_matches: List[str], 
        similar_files: List[Tuple[str, str]], 
        pattern: str, 
        expected_extension: str, 
        rule: RuleData
    ) -> None:
        """
        Evalúa los resultados de búsqueda y genera reportes apropiados.
        
        Args:
            exact_matches: Lista de archivos que coinciden exactamente
            similar_files: Lista de archivos similares pero incorrectos
            pattern: Patrón original buscado
            expected_extension: Extensión esperada
            rule: Regla a actualizar con errores
        """
        if not exact_matches:
            self._handle_no_exact_matches(similar_files, pattern, expected_extension, rule)
        elif len(exact_matches) > 1:
            self._handle_multiple_matches(exact_matches, pattern)
    
    def _handle_no_exact_matches(
        self, 
        similar_files: List[Tuple[str, str]], 
        pattern: str, 
        expected_extension: str, 
        rule: RuleData
    ) -> None:
        """Maneja el caso cuando no hay coincidencias exactas."""
        if similar_files:
            self._add_errors_for_similar_files(similar_files, expected_extension, pattern, rule)
        else:
            error_msg = f"Archivo requerido '{pattern}' no encontrado"
            rule.add_error(error_msg)
            self._logger.debug("No se encontró archivo: %s", pattern)
    
    def _handle_multiple_matches(self, exact_matches: List[str], pattern: str) -> None:
        """Maneja el caso cuando hay múltiples coincidencias exactas."""
        self._logger.info(
            "Múltiples archivos encontrados para '%s': %s", 
            pattern, exact_matches
        )
    
    def _evaluate_matches(
        self, 
        exact_matches: List[str], 
        similar_files: List[Tuple[str, str]], 
        pattern: str, 
        expected_extension: str, 
        rule: RuleData
    ) -> None:
        """
        DEPRECATED: Usar _evaluate_and_report_matches en su lugar.
        Mantener por compatibilidad temporal.
        """
        self._evaluate_and_report_matches(exact_matches, similar_files, pattern, expected_extension, rule)
    
    def _filter_files_by_references(
        self, 
        files: List[FileEntry], 
        references: Optional[str]
    ) -> List[FileEntry]:
        """
        Filtra archivos usando patrones glob del campo references.
        
        Args:
            files: Lista completa de archivos
            references: Patrones separados por coma como "**/Resource/Contract/*.wsdl,**/Resource/Contract/*.yaml"
            
        Returns:
            Lista filtrada de archivos que coinciden con los patrones, o lista completa si no hay references
        """
        if not references or not references.strip():
            # Sin filtro, devolver todos los archivos
            return files
        
        # Dividir patrones por coma
        patterns = [pattern.strip() for pattern in references.split(',')]
        filtered_files = []
        
        for file_path, is_wiki in files:
            # Verificar si el archivo coincide con algún patrón
            if self._file_matches_any_pattern(file_path, patterns):
                filtered_files.append((file_path, is_wiki))
        
        self._logger.debug(
            "Filtro por references: %d de %d archivos coinciden con '%s'",
            len(filtered_files), len(files), references
        )
        return filtered_files
    
    def _file_matches_any_pattern(self, file_path: str, patterns: List[str]) -> bool:
        """
        Verifica si un archivo coincide con alguno de los patrones glob.
        
        Args:
            file_path: Ruta del archivo a verificar
            patterns: Lista de patrones glob
            
        Returns:
            True si el archivo coincide con al menos un patrón
        """
        for pattern in patterns:
            if self._matches_glob_pattern(file_path, pattern):
                return True
        return False
    
    def _matches_glob_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Verifica si un archivo coincide con un patrón glob específico.
        
        Args:
            file_path: Ruta del archivo
            pattern: Patrón glob
            
        Returns:
            True si el archivo coincide con el patrón
        """
        normalized_path = self._normalize_path(file_path)
        normalized_pattern = self._normalize_path(pattern)
        
        if '**' in normalized_pattern:
            return self._match_recursive_pattern(normalized_path, normalized_pattern)
        
        return fnmatch.fnmatch(normalized_path, normalized_pattern)
    
    def _normalize_path(self, path: str) -> str:
        """Normaliza separadores de ruta para compatibilidad multiplataforma."""
        return path.replace('\\', '/')
    
    def _match_recursive_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Maneja patrones con ** para coincidencia recursiva de directorios.
        
        Args:
            file_path: Ruta normalizada del archivo
            pattern: Patrón normalizado con **
            
        Returns:
            True si coincide con el patrón recursivo
        """
        parts = pattern.split('**/')
        if len(parts) != 2:
            return False
            
        prefix, suffix = parts
        
        if not self._matches_suffix(file_path, suffix):
            return False
        
        return self._matches_prefix(file_path, prefix)
    
    def _matches_suffix(self, file_path: str, suffix: str) -> bool:
        """Verifica si el archivo coincide con el sufijo del patrón."""
        return fnmatch.fnmatch(file_path, f"*{suffix}")
    
    def _matches_prefix(self, file_path: str, prefix: str) -> bool:
        """Verifica si el archivo coincide con el prefijo del patrón."""
        if not prefix or not prefix.rstrip('/'):
            return True
        return prefix.rstrip('/') in file_path
    
    def _parse_file_pattern(self, pattern: str) -> Tuple[str, str]:
        """
        Extrae el nombre base y extensión de un patrón de archivo.
        
        Args:
            pattern: Patrón como "Guion.md"
            
        Returns:
            Tupla (nombre_base, extensión) como ("Guion", ".md")
        """
        if '.' in pattern:
            base_name = pattern.rsplit('.', 1)[0]
            extension = '.' + pattern.rsplit('.', 1)[1]
        else:
            base_name = pattern
            extension = ""
        
        return base_name, extension
    
    def _find_matching_files(
        self, 
        files: List[FileEntry], 
        pattern: str, 
        expected_name: str
    ) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Busca archivos que coincidan exactamente y archivos similares.
        
        Args:
            files: Lista de archivos donde buscar
            pattern: Patrón exacto a buscar
            expected_name: Nombre base esperado
            
        Returns:
            Tupla (archivos_exactos, archivos_similares)
        """
        exact_matches = []
        similar_files = []
        
        for file_path, is_wiki in files:
            file_name = os.path.basename(file_path)
            
            if file_name == pattern:
                exact_matches.append(file_path)
            elif file_name.startswith(expected_name):
                similar_files.append((file_path, file_name))
        
        return exact_matches, similar_files
    
    def _add_errors_for_similar_files(
        self, 
        similar_files: List[Tuple[str, str]], 
        expected_extension: str, 
        pattern: str, 
        rule: RuleData
    ) -> None:
        """
        Agrega errores específicos para archivos similares pero incorrectos.
        
        Args:
            similar_files: Lista de tuplas (ruta_archivo, nombre_archivo)
            expected_extension: Extensión esperada
            pattern: Patrón original
            rule: Regla a actualizar
        """
        for file_path, file_name in similar_files:
            if '.' in file_name:
                actual_extension = '.' + file_name.rsplit('.', 1)[1]
                if actual_extension != expected_extension:
                    error_msg = (
                        f"Archivo '{file_path}': extensión debe ser '{expected_extension}', "
                        f"no '{actual_extension}'"
                    )
                else:
                    error_msg = f"Archivo '{file_path}': nombre debe ser exactamente '{pattern}'"
            else:
                error_msg = f"Archivo '{file_path}': debe tener extensión '{expected_extension}'"
            
            rule.add_error(error_msg)
            self._logger.debug("Error agregado: %s", error_msg)
    
    def _get_naming_rules(self, rule: RuleData) -> List[NamingRule]:
        """
        Obtiene las reglas de nomenclatura de la regla.
        
        Returns:
            Lista de reglas de nomenclatura como objetos NamingRule
        """
        naming_rules = getattr(rule, 'naming_rules', [])
        return naming_rules or []
    
    def _validate_single_file_extension(
        self, 
        file_name: str, 
        naming_rules: List[NamingRule], 
        rule: RuleData
    ) -> bool:
        """
        Valida la extensión de un archivo individual basado en reglas de nomenclatura.
        
        Args:
            file_name: Nombre del archivo a validar
            naming_rules: Lista de reglas de nomenclatura
            rule: Regla principal para agregar errores
            
        Returns:
            True si la extensión es válida, False si no
        """
        rule_id = getattr(rule, 'id', 'unknown')
        
        # Encontrar la regla aplicable
        applicable_rule = self._find_applicable_naming_rule(file_name, naming_rules)
        
        if not applicable_rule:
            error_msg = f"No se encontró regla aplicable para archivo '{file_name}'"
            rule.add_error(error_msg)
            self._logger.debug("Regla %s: %s", rule_id, error_msg)
            return False
        
        # Validar extensión
        expected_extension = applicable_rule.required_extension
        actual_extension = self._get_file_extension(file_name)
        
        if actual_extension.lower() != expected_extension.lower():
            error_msg = (
                f"Archivo '{file_name}': extensión debe ser '{expected_extension}', "
                f"no '{actual_extension}'"
            )
            rule.add_error(error_msg)
            self._logger.debug("Regla %s: %s", rule_id, error_msg)
            return False
        
        self._logger.debug(
            "Regla %s: archivo '%s' tiene extensión correcta '%s'", 
            rule_id, file_name, actual_extension
        )
        return True
    
    def _find_applicable_naming_rule(
        self, 
        file_name: str, 
        naming_rules: List[NamingRule]
    ) -> Optional[NamingRule]:
        """
        Encuentra la regla de nomenclatura aplicable para un archivo.
        
        Orden de prioridad:
        1. Reglas específicas (con 'contains')
        2. Regla por defecto (is_default=True)
        
        Returns:
            Regla aplicable o None si no se encuentra
        """
        default_rule = None
        
        for naming_rule in naming_rules:
            # Manejar regla por defecto
            if naming_rule.is_default:
                default_rule = naming_rule
                continue
            
            # Verificar reglas específicas
            if not naming_rule.contains:
                continue
            
            # Verificar si el archivo contiene el término
            file_check = file_name if naming_rule.case_sensitive else file_name.lower()
            term_check = naming_rule.contains if naming_rule.case_sensitive else naming_rule.contains.lower()
            
            if term_check in file_check:
                # Verificar exclusiones
                excluded = False
                
                for exclude_term in naming_rule.exclude:
                    exclude_check = exclude_term if naming_rule.case_sensitive else exclude_term.lower()
                    if exclude_check in file_check:
                        excluded = True
                        break
                
                if not excluded:
                    return naming_rule
        
        # Si no se encontró regla específica, usar la por defecto
        return default_rule
    
    def _get_file_extension(self, file_name: str) -> str:
        """
        Obtiene la extensión de un archivo incluyendo el punto.
        
        Returns:
            Extensión como ".txt", ".xml", etc. o "" si no tiene extensión
        """
        if '.' not in file_name:
            return ""
        
        return '.' + file_name.rsplit('.', 1)[1]


# ================================
# EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    # Configurar logging para ejemplo
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ejemplo de archivos
    example_files = [
        ("docs/Guion.md", False),
        ("Resource/Contract/servicio.wsdl", False),
        ("Resource/Test/test_soapui.xml", False),
        ("Resource/Test/postman_collection.json", False),
        ("src/main.py", False)
    ]
    
    # Ejemplo de regla
    example_rule_json = {
        "id": "1.4",
        "description": "Debe haber un documento de Guion...",
        "type": "estructura",
        "validation_type": "exact_match",
        "pattern": "Guion.md",
        "references": None
    }
    
    # Deserializar y validar
    rule = deserialize_rule_data(example_rule_json)
    validator = FileStructureValidator()
    validator.validate_file_structure(example_files, [rule])
    
    # Mostrar resultados
    print(f"Regla validada: {rule.isvalidated}")
    print(f"Errores: {rule.errors}")
    print(f"Resumen: {rule.get_validation_summary()}")