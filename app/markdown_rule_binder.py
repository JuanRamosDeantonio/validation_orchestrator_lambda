from typing import List, Dict, Set, Tuple

from app.models import MarkdownDocument, RuleData
import fnmatch
import logging

from app.markdown_provider import MarkdownConsumer

logger = logging.getLogger(__name__)


class LogMessages:
    """Constantes para mensajes de logging consistentes."""
    
    RULE_INVALID = "[⚠️] Regla '{rule_id}' sin referencias válidas. Se omite."
    RULE_NO_SOURCES = "[ℹ️] No se encontraron archivos fuente para la regla '{rule_id}'."
    RULE_NO_VALID_FILES = "[ℹ️] Regla '{rule_id}' sin archivos válidos después de filtrar duplicados. Se omite."
    RULE_DUPLICATED_FILES = "[⚠️] Regla '{rule_id}' ignorará {count} archivo(s) ya usado(s): {files}"
    RULE_PROCESSING_ERROR = "[❌] Error crítico procesando la regla '{rule_id}': {error}"
    MARKDOWN_LOAD_ERROR = "[❌] Error cargando archivo Markdown '{path}': {error}"


def is_rule_valid(rule: RuleData) -> bool:
    """
    Valida que una regla tenga la estructura mínima requerida.
    
    Args:
        rule: Regla a validar
        
    Returns:
        bool: True si la regla tiene al menos una referencia válida
    """
    return (
        rule.references and 
        len(rule.references) > 0 and 
        rule.references[0].strip()
    )


def extract_patterns_from_rule(rule: RuleData) -> Tuple[str, List[str]]:
    """
    Extrae los patrones de búsqueda de una regla.
    
    La primera referencia es el patrón fuente (obligatorio).
    Las referencias adicionales son patrones de destino (opcionales).
    
    Args:
        rule: Regla de la cual extraer patrones
        
    Returns:
        Tuple con (patrón_fuente, lista_patrones_destino)
    """
    source_pattern = rule.parsed_references[0]
    destiny_patterns = [r.strip() for r in rule.parsed_references[1:]] if len(rule.parsed_references) > 1 else []
    return source_pattern, destiny_patterns


def find_matching_paths(paths: List[str], patterns: List[str]) -> List[str]:
    """
    Encuentra todas las rutas que coincidan con cualquiera de los patrones dados.
    
    Args:
        paths: Lista de rutas disponibles
        patterns: Lista de patrones de búsqueda (estilo Unix glob)
        
    Returns:
        Lista de rutas que coinciden con al menos un patrón
    """
    if not patterns:
        return []
    
    matching_paths = []
    for path in paths:
        if any(fnmatch.fnmatch(path, pattern) for pattern in patterns):
            matching_paths.append(path)
    
    return matching_paths


class UsedPathsTracker:
    """
    Rastrea archivos que ya han sido asignados a reglas anteriores.
    
    Esto evita que múltiples reglas procesen el mismo archivo,
    manteniendo una correlación uno-a-uno entre archivos y reglas.
    """
    
    def __init__(self):
        self._used_paths: Set[str] = set()
    
    def mark_as_used(self, paths: List[str]) -> None:
        """
        Marca una lista de rutas como ya utilizadas.
        
        Args:
            paths: Rutas a marcar como utilizadas
        """
        self._used_paths.update(paths)
    
    def filter_unused_paths(self, paths: List[str]) -> Tuple[List[str], Set[str]]:
        """
        Filtra las rutas que no han sido utilizadas previamente.
        
        Args:
            paths: Lista de rutas candidatas
            
        Returns:
            Tuple con (rutas_no_utilizadas, rutas_duplicadas)
        """
        duplicated = self._used_paths.intersection(paths)
        unused_paths = [p for p in paths if p not in duplicated]
        return unused_paths, duplicated


class MarkdownLoader:
    """
    Maneja la carga de documentos Markdown desde el proveedor configurado.
    
    Encapsula la lógica de carga y manejo de errores para archivos Markdown.
    """
    
    def __init__(self, markdown_provider: MarkdownConsumer):
        """
        Inicializa el cargador con un proveedor específico.
        
        Args:
            markdown_provider: Objeto que implementa get_markdown(path)
        """
        self.markdown_provider = markdown_provider
    
    def load_documents(self, paths: List[str], repository_url:str) -> Dict[str, MarkdownDocument]:
        """
        Carga múltiples documentos Markdown en un solo lote.
        
        Args:
            paths: Lista de rutas de archivos a cargar
            
        Returns:
            Diccionario mapeando ruta -> MarkdownDocument
            
        Raises:
            Exception: Si hay error cargando cualquier archivo
        """
        documents = {}
        
        for path in paths:
            try:
                markdown_result = self.markdown_provider.get_file_markdown(path,repository_url)
                documents[path] = MarkdownDocument(
                                                   path=path,
                                                   content=markdown_result.markdown_content
                                  )
            except Exception as e:
                logger.error(LogMessages.MARKDOWN_LOAD_ERROR.format(path=path, error=str(e)))
                raise
        
        return documents


class RuleProcessor:
    """
    Procesa reglas individuales aplicando toda la lógica de correlación.
    
    Coordina la validación, búsqueda de archivos, filtrado de duplicados
    y carga de documentos para una regla específica.
    """
    
    def __init__(self, markdown_loader: MarkdownLoader, used_paths_tracker: UsedPathsTracker):
        """
        Inicializa el procesador con sus dependencias.
        
        Args:
            markdown_loader: Cargador de documentos Markdown
            used_paths_tracker: Rastreador de archivos ya utilizados
        """
        self.markdown_loader = markdown_loader
        self.used_paths_tracker = used_paths_tracker
    
    def process_rule(self, rule: RuleData, available_paths: List[str], repository_url: str) -> bool:
        """
        Ejecuta el procesamiento completo de una regla individual.
        
        Args:
            rule: Regla a procesar
            available_paths: Lista de todas las rutas disponibles en el repositorio
            
        Returns:
            bool: True si la regla se procesó exitosamente, False si se omitió
        """
        # Paso 1: Validar estructura de la regla
        if not is_rule_valid(rule):
            logger.warning(LogMessages.RULE_INVALID.format(rule_id=rule.id))
            return False
        
        # Paso 2: Encontrar archivos que coincidan con los patrones
        target_paths = self._find_target_paths(rule, available_paths)
        if not target_paths:
            logger.info(LogMessages.RULE_NO_SOURCES.format(rule_id=rule.id))
            return False
        
        # Paso 3: Cargar documentos Markdown y asignarlos a la regla
        self._load_rule_documents(rule, target_paths, repository_url)
        return True
    
    def _find_target_paths(self, rule: RuleData, available_paths: List[str]) -> List[str]:
        """
        Identifica todas las rutas objetivo para una regla según sus patrones.
        
        Combina archivos fuente y destino en una sola lista sin duplicados.
        
        Args:
            rule: Regla con patrones de búsqueda
            available_paths: Rutas disponibles para buscar
            
        Returns:
            Lista única de rutas que coinciden con los patrones de la regla
        """
        source_pattern, destiny_patterns = extract_patterns_from_rule(rule)
        
        # Buscar archivos fuente (obligatorios)
        sources = find_matching_paths(available_paths, [source_pattern])
        
        # Buscar archivos destino (opcionales)
        targets = find_matching_paths(available_paths, destiny_patterns)
        
        # Combinar eliminando duplicados
        return list(set(sources + targets))
    
    def _filter_and_track_paths(self, rule: RuleData, paths: List[str]) -> List[str]:
        """
        Filtra archivos ya utilizados y marca los nuevos como en uso.
        
        Args:
            rule: Regla siendo procesada (para logging)
            paths: Rutas candidatas a filtrar
            
        Returns:
            Lista de rutas no utilizadas previamente
        """
        filtered_paths, duplicated = self.used_paths_tracker.filter_unused_paths(paths)
        
        # Reportar archivos duplicados si los hay
        if duplicated:
            logger.warning(LogMessages.RULE_DUPLICATED_FILES.format(
                rule_id=rule.id, 
                count=len(duplicated), 
                files=list(duplicated)
            ))
        
        # Marcar rutas válidas como utilizadas
        if filtered_paths:
            self.used_paths_tracker.mark_as_used(filtered_paths)
        
        return filtered_paths
    
    def _load_rule_documents(self, rule: RuleData, paths: List[str], repository_url: str) -> None:
        """
        Carga los documentos Markdown y los asigna a la regla.
        
        Args:
            rule: Regla a la cual asignar los documentos
            paths: Rutas de archivos a cargar
        """
        rule.markdownfiles = self.markdown_loader.load_documents(paths, repository_url)


class MarkdownRuleBinder:
    """
    Coordinador principal del proceso de correlación entre reglas y documentos Markdown.
    
    Orquesta el procesamiento secuencial de reglas, manteniendo el estado
    de archivos utilizados para evitar duplicaciones entre reglas.
    """
    
    def __init__(self, markdown_provider):
        """
        Inicializa el coordinador con un proveedor de archivos Markdown.
        
        Args:
            markdown_provider: Objeto que implementa get_markdown(path) para 
                             obtener el contenido de archivos Markdown
        """
        self.markdown_loader = MarkdownLoader(markdown_provider)
        self.used_paths_tracker = UsedPathsTracker()
        self.rule_processor = RuleProcessor(self.markdown_loader, self.used_paths_tracker)
    
    def run(self, rules: List[RuleData], paths: List[str], repository_url: str) -> Dict[str, str]:
        """
        Ejecuta el proceso completo de correlación para todas las reglas.
        
        Procesa cada regla secuencialmente, manteniendo un registro global
        de archivos ya asignados para evitar duplicaciones.
        
        Args:
            rules: Lista de reglas a procesar en orden
            paths: Lista de todas las rutas de archivos Markdown disponibles
            
        Returns:
            Dict[str, str]: Diccionario de resultados (actualmente placeholder)
            
        Raises:
            Exception: Si ocurre un error crítico durante el procesamiento
        """
        processed_count = 0
        
        for rule in rules:
            try:
                if self.rule_processor.process_rule(rule, paths, repository_url):
                    processed_count += 1
                    
            except Exception as e:
                logger.exception(LogMessages.RULE_PROCESSING_ERROR.format(
                    rule_id=rule.id, 
                    error=str(e)
                ))
                raise  # Detener ejecución en errores críticos
        
        logger.info(f"[✅] Procesamiento completado: {processed_count}/{len(rules)} reglas exitosas")
        return {}  # Placeholder para compatibilidad