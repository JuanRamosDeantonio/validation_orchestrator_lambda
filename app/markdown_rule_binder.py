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
    CACHE_HIT = "[🎯] Cache hit para archivo '{path}'"
    CACHE_MISS = "[📁] Cache miss para archivo '{path}' - cargando desde proveedor"
    PROCESSING_COMPLETE = "[✅] Procesamiento completado: {processed}/{total} reglas exitosas"
    CACHE_STATS = "[📊] Cache stats: {cached_docs} documentos únicos cargados"
    CACHE_CLEARED = "[🧹] Cache limpiado - memoria liberada"
    
    # Mensajes detallados para mejor trazabilidad
    RULE_PROCESSING_START = "[🔄] Iniciando procesamiento de regla '{rule_id}'"
    RULE_FOUND_TARGETS = "[📂] Regla '{rule_id}' encontró {count} archivo(s): {files}"
    RULE_LOADING_DOCUMENTS = "[📥] Regla '{rule_id}' cargando {count} documento(s)..."
    RULE_DOCUMENTS_LOADED = "[✅] Regla '{rule_id}' cargó exitosamente {count} archivo(s): {files}"
    RULE_PROCESSING_SUCCESS = "[🎯] Regla '{rule_id}' procesada exitosamente con {count} archivo(s)"
    RULE_PROCESSING_SKIPPED = "[⏭️] Regla '{rule_id}' omitida - sin archivos válidos"


class DocumentCache:
    """
    Cache de documentos Markdown para evitar cargas duplicadas.
    
    Mantiene los documentos ya cargados en memoria para reutilización
    entre múltiples reglas que requieren los mismos archivos.
    """
    
    def __init__(self, markdown_provider: MarkdownConsumer):
        """
        Inicializa el cache con el proveedor de documentos.
        
        Args:
            markdown_provider: Objeto que implementa get_file_markdown(path, repo_url)
        """
        self.markdown_provider = markdown_provider
        self._cache: Dict[str, MarkdownDocument] = {}
    
    def _generate_cache_key(self, path: str, repository_url: str) -> str:
        """
        Genera una clave única para el cache basada en la ruta y repositorio.
        
        Args:
            path: Ruta del archivo
            repository_url: URL del repositorio
            
        Returns:
            Clave única para el cache
        """
        return f"{repository_url}:{path}"
    
    def get_document(self, path: str, repository_url: str) -> MarkdownDocument:
        """
        Obtiene un documento del cache o lo carga si no existe.
        
        Args:
            path: Ruta del archivo Markdown
            repository_url: URL del repositorio
            
        Returns:
            MarkdownDocument cargado
            
        Raises:
            Exception: Si hay error cargando el archivo
        """
        cache_key = self._generate_cache_key(path, repository_url)
        
        if cache_key in self._cache:
            logger.debug(LogMessages.CACHE_HIT.format(path=path))
            return self._cache[cache_key]
        
        logger.debug(LogMessages.CACHE_MISS.format(path=path))
        
        try:
            markdown_result = self.markdown_provider.get_file_markdown(path, repository_url)
            document = MarkdownDocument(
                path=path,
                content=markdown_result.markdown_content
            )
            
            # Guardar en cache para futuras consultas
            self._cache[cache_key] = document
            return document
            
        except Exception as e:
            logger.error(LogMessages.MARKDOWN_LOAD_ERROR.format(path=path, error=str(e)))
            raise
    
    def get_documents(self, paths: List[str], repository_url: str) -> Dict[str, MarkdownDocument]:
        """
        Obtiene múltiples documentos usando el cache.
        
        Args:
            paths: Lista de rutas de archivos
            repository_url: URL del repositorio
            
        Returns:
            Diccionario mapeando ruta -> MarkdownDocument
            
        Raises:
            Exception: Si hay error cargando cualquier archivo
        """
        return {path: self.get_document(path, repository_url) for path in paths}
    
    def clear_cache(self) -> None:
        """Limpia el cache liberando memoria. Útil para optimización en Lambda."""
        self._cache.clear()
        logger.info(LogMessages.CACHE_CLEARED)
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retorna estadísticas del cache para debugging/monitoring.
        
        Returns:
            Dict con estadísticas del cache
        """
        return {
            'cached_documents': len(self._cache),
            'total_memory_items': len(self._cache)
        }


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


class MarkdownLoader:
    """
    Maneja la carga de documentos Markdown usando cache para optimizar rendimiento.
    
    Utiliza DocumentCache para evitar cargas duplicadas del mismo archivo
    cuando múltiples reglas lo requieren.
    """
    
    def __init__(self, document_cache: DocumentCache):
        """
        Inicializa el cargador con un cache de documentos.
        
        Args:
            document_cache: Cache que maneja la carga optimizada de documentos
        """
        self.document_cache = document_cache
    
    def load_documents(self, paths: List[str], repository_url: str) -> Dict[str, MarkdownDocument]:
        """
        Carga múltiples documentos Markdown usando cache.
        
        Args:
            paths: Lista de rutas de archivos a cargar
            repository_url: URL del repositorio
            
        Returns:
            Diccionario mapeando ruta -> MarkdownDocument
            
        Raises:
            Exception: Si hay error cargando cualquier archivo
        """
        return self.document_cache.get_documents(paths, repository_url)


class RuleProcessor:
    """
    Procesa reglas individuales aplicando toda la lógica de correlación.
    
    Coordina la validación, búsqueda de archivos y carga optimizada
    de documentos para una regla específica.
    """
    
    def __init__(self, markdown_loader: MarkdownLoader):
        """
        Inicializa el procesador con sus dependencias.
        
        Args:
            markdown_loader: Cargador optimizado de documentos Markdown
        """
        self.markdown_loader = markdown_loader
    
    def process_rule(self, rule: RuleData, available_paths: List[str], repository_url: str) -> bool:
        """
        Ejecuta el procesamiento completo de una regla individual.
        
        Args:
            rule: Regla a procesar
            available_paths: Lista de todas las rutas disponibles en el repositorio
            repository_url: URL del repositorio
            
        Returns:
            bool: True si la regla se procesó exitosamente, False si se omitió
        """
        logger.info(LogMessages.RULE_PROCESSING_START.format(rule_id=rule.id))
        
        # Paso 1: Validar estructura de la regla
        if not is_rule_valid(rule):
            logger.warning(LogMessages.RULE_INVALID.format(rule_id=rule.id))
            return False
        
        # Paso 2: Encontrar archivos que coincidan con los patrones
        target_paths = self._find_target_paths(rule, available_paths)
        if not target_paths:
            logger.info(LogMessages.RULE_NO_SOURCES.format(rule_id=rule.id))
            logger.info(LogMessages.RULE_PROCESSING_SKIPPED.format(rule_id=rule.id))
            return False
        
        # Log de archivos encontrados
        logger.info(LogMessages.RULE_FOUND_TARGETS.format(
            rule_id=rule.id, 
            count=len(target_paths), 
            files=target_paths
        ))
             
        # Paso 3: Cargar documentos usando cache y asignarlos a la regla
        logger.info(LogMessages.RULE_LOADING_DOCUMENTS.format(
            rule_id=rule.id, 
            count=len(target_paths)
        ))
        
        self._load_rule_documents(rule, target_paths, repository_url)
        
        # Log de documentos cargados exitosamente
        loaded_paths = self._get_loaded_paths(rule)
        logger.info(LogMessages.RULE_DOCUMENTS_LOADED.format(
            rule_id=rule.id, 
            count=len(loaded_paths), 
            files=loaded_paths
        ))
        
        logger.info(LogMessages.RULE_PROCESSING_SUCCESS.format(
            rule_id=rule.id, 
            count=len(loaded_paths)
        ))
        
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
    
    def _load_rule_documents(self, rule: RuleData, paths: List[str], repository_url: str) -> None:
        """
        Carga los documentos Markdown usando cache y los asigna a la regla.
        
        Args:
            rule: Regla a la cual asignar los documentos
            paths: Rutas de archivos a cargar
            repository_url: URL del repositorio
        """
        rule.markdownfiles = self.markdown_loader.load_documents(paths, repository_url)
    
    def _get_loaded_paths(self, rule: RuleData) -> List[str]:
        """
        Extrae los paths de los documentos cargados en una regla.
        
        Args:
            rule: Regla procesada
            
        Returns:
            Lista de paths de documentos cargados
        """
        if not hasattr(rule, 'markdownfiles') or not rule.markdownfiles:
            return []
        
        if isinstance(rule.markdownfiles, dict):
            return list(rule.markdownfiles.keys())
        elif isinstance(rule.markdownfiles, list):
            return [doc.path for doc in rule.markdownfiles]
        else:
            return []


class MarkdownRuleBinder:
    """
    Coordinador principal del proceso de correlación entre reglas y documentos Markdown.
    
    Orquesta el procesamiento secuencial de reglas con cache optimizado.
    Versión simplificada basada en tu código, eliminando el tracking innecesario
    de archivos duplicados ya que el cache maneja las cargas duplicadas.
    """
    
    def __init__(self, markdown_provider: MarkdownConsumer):
        """
        Inicializa el coordinador con un proveedor de archivos Markdown.
        
        Args:
            markdown_provider: Objeto que implementa get_file_markdown(path, repo_url)
        """
        self.document_cache = DocumentCache(markdown_provider)
        self.markdown_loader = MarkdownLoader(self.document_cache)
        self.rule_processor = RuleProcessor(self.markdown_loader)
    
    def run(self, rules: List[RuleData], paths: List[str], repository_url: str) -> Dict[str, any]:
        """
        Ejecuta el proceso completo de correlación para todas las reglas.
        
        Procesa cada regla secuencialmente con cache optimizado.
        
        Args:
            rules: Lista de reglas a procesar en orden
            paths: Lista de todas las rutas de archivos Markdown disponibles
            repository_url: URL del repositorio
            
        Returns:
            Dict con estadísticas del procesamiento y cache
            
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
        
        # Obtener estadísticas para logging/monitoring
        cache_stats = self.document_cache.get_cache_stats()
        
        logger.info(LogMessages.PROCESSING_COMPLETE.format(
            processed=processed_count, 
            total=len(rules)
        ))
        logger.info(LogMessages.CACHE_STATS.format(
            cached_docs=cache_stats['cached_documents']
        ))
        
        # Resumen detallado de reglas con archivos
        self._log_processing_summary(rules)
        
        return {
            'processed_rules': processed_count,
            'total_rules': len(rules),
            'success_rate': processed_count / len(rules) if rules else 0,
            'cache_stats': cache_stats
        }
    
    def _log_processing_summary(self, rules: List[RuleData]) -> None:
        """
        Registra un resumen detallado de todas las reglas procesadas.
        
        Args:
            rules: Lista de reglas procesadas
        """
        logger.info("="*60)
        logger.info("[📋] RESUMEN DE PROCESAMIENTO DE REGLAS")
        logger.info("="*60)
        
        rules_with_files = []
        rules_without_files = []
        
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    file_count = len(rule.markdownfiles)
                    file_paths = list(rule.markdownfiles.keys())
                elif isinstance(rule.markdownfiles, list):
                    file_count = len(rule.markdownfiles)
                    file_paths = [doc.path for doc in rule.markdownfiles]
                else:
                    file_count = 0
                    file_paths = []
                
                if file_count > 0:
                    rules_with_files.append((rule.id, file_count, file_paths))
                else:
                    rules_without_files.append(rule.id)
            else:
                rules_without_files.append(rule.id)
        
        # Logging de reglas con archivos
        if rules_with_files:
            logger.info(f"[✅] Reglas con archivos Markdown ({len(rules_with_files)}):")
            for rule_id, file_count, file_paths in rules_with_files:
                logger.info(f"  📁 Regla '{rule_id}': {file_count} archivo(s)")
                for path in file_paths:
                    logger.info(f"    └─ {path}")
        
        # Logging de reglas sin archivos
        if rules_without_files:
            logger.info(f"[❌] Reglas sin archivos Markdown ({len(rules_without_files)}):")
            for rule_id in rules_without_files:
                logger.info(f"  📂 Regla '{rule_id}': 0 archivos")
        
        # Estadísticas finales
        total_files = sum(count for _, count, _ in rules_with_files)
        logger.info("="*60)
        logger.info(f"[📊] ESTADÍSTICAS FINALES:")
        logger.info(f"  • Total reglas procesadas: {len(rules)}")
        logger.info(f"  • Reglas con archivos: {len(rules_with_files)}")
        logger.info(f"  • Reglas sin archivos: {len(rules_without_files)}")
        logger.info(f"  • Total archivos cargados: {total_files}")
        logger.info("="*60)
    
    def clear_cache(self) -> None:
        """
        Limpia el cache de documentos para liberar memoria.
        
        Útil en entornos Lambda para optimizar uso de memoria
        entre invocaciones o al final del procesamiento.
        """
        self.document_cache.clear_cache()
    
    def get_processing_stats(self) -> Dict[str, any]:
        """
        Retorna estadísticas actuales del procesamiento y cache.
        
        Returns:
            Dict con métricas de rendimiento y uso de memoria
        """
        return {
            'cache_stats': self.document_cache.get_cache_stats()
        }
    
    def get_all_markdown_paths(self, rules: List[RuleData]) -> List[str]:
        """
        Extrae todos los paths de los archivos Markdown procesados.
        
        Args:
            rules: Lista de reglas procesadas
            
        Returns:
            Lista de todos los paths de archivos Markdown
        """
        paths = []
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    # Si es diccionario (como en el código original)
                    paths.extend(rule.markdownfiles.keys())
                elif isinstance(rule.markdownfiles, list):
                    # Si es lista (como en el modelo)
                    paths.extend(doc.path for doc in rule.markdownfiles)
        return paths
    
    def get_paths_by_rule(self, rules: List[RuleData]) -> Dict[str, List[str]]:
        """
        Obtiene los paths de archivos Markdown agrupados por regla.
        
        Args:
            rules: Lista de reglas procesadas
            
        Returns:
            Dict mapeando rule_id -> lista de paths
        """
        result = {}
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    # Si es diccionario (como en el código original)
                    result[rule.id] = list(rule.markdownfiles.keys())
                elif isinstance(rule.markdownfiles, list):
                    # Si es lista (como en el modelo)
                    result[rule.id] = [doc.path for doc in rule.markdownfiles]
        return result
    
    def get_unique_markdown_paths(self, rules: List[RuleData]) -> Set[str]:
        """
        Obtiene el conjunto único de paths de archivos Markdown.
        
        Args:
            rules: Lista de reglas procesadas
            
        Returns:
            Set de paths únicos
        """
        paths = set()
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    # Si es diccionario (como en el código original)
                    paths.update(rule.markdownfiles.keys())
                elif isinstance(rule.markdownfiles, list):
                    # Si es lista (como en el modelo)
                    paths.update(doc.path for doc in rule.markdownfiles)
        return paths
    
    def count_total_markdown_files(self, rules: List[RuleData]) -> int:
        """
        Cuenta el total de archivos Markdown procesados.
        
        Args:
            rules: Lista de reglas procesadas
            
        Returns:
            Número total de archivos Markdown
        """
        total = 0
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    # Si es diccionario (como en el código original)
                    total += len(rule.markdownfiles)
                elif isinstance(rule.markdownfiles, list):
                    # Si es lista (como en el modelo)
                    total += len(rule.markdownfiles)
        return total
    
    def log_rules_with_files(self, rules: List[RuleData]) -> None:
        """
        Registra en el log un detalle de qué reglas tienen archivos y cuáles.
        
        Args:
            rules: Lista de reglas a analizar
        """
        self._log_processing_summary(rules)
    
    def get_rules_files_summary(self, rules: List[RuleData]) -> Dict[str, any]:
        """
        Obtiene un resumen estructurado de las reglas y sus archivos.
        
        Args:
            rules: Lista de reglas procesadas
            
        Returns:
            Dict con resumen detallado de reglas y archivos
        """
        rules_with_files = {}
        rules_without_files = []
        
        for rule in rules:
            if hasattr(rule, 'markdownfiles') and rule.markdownfiles:
                if isinstance(rule.markdownfiles, dict):
                    file_paths = list(rule.markdownfiles.keys())
                elif isinstance(rule.markdownfiles, list):
                    file_paths = [doc.path for doc in rule.markdownfiles]
                else:
                    file_paths = []
                
                if file_paths:
                    rules_with_files[rule.id] = {
                        'file_count': len(file_paths),
                        'file_paths': file_paths
                    }
                else:
                    rules_without_files.append(rule.id)
            else:
                rules_without_files.append(rule.id)
        
        total_files = sum(info['file_count'] for info in rules_with_files.values())
        
        return {
            'rules_with_files': rules_with_files,
            'rules_without_files': rules_without_files,
            'summary': {
                'total_rules': len(rules),
                'rules_with_files_count': len(rules_with_files),
                'rules_without_files_count': len(rules_without_files),
                'total_files_loaded': total_files
            }
        }