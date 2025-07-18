"""
config.py - Configuración optimizada para AWS Lambda
"""

import os
import logging
import threading
from typing import Optional, Dict, Any


class Config:
    """
    Configuración optimizada para AWS Lambda con cache y validación.
    
    Características:
    - Cache de variables de entorno para mejor performance
    - Validación de tipos automática
    - Thread-safe para entornos concurrentes
    - Inicialización rápida para cold starts
    """
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def _get_env_cached(self, key: str, default: str = '') -> str:
        """Obtiene variable de entorno con cache thread-safe."""
        if key not in self._cache:
            with self._lock:
                if key not in self._cache:
                    self._cache[key] = os.environ.get(key, default)
        return self._cache[key]
    
    def _get_env_int(self, key: str, default: int = 0) -> int:
        """Obtiene variable de entorno como entero con validación."""
        cache_key = f"{key}_int"
        if cache_key not in self._cache:
            with self._lock:
                if cache_key not in self._cache:
                    try:
                        value = int(os.environ.get(key, str(default)))
                        # Validación básica para valores sensatos
                        if key.endswith('_BYTES') and value < 0:
                            value = default
                        elif key.endswith('_TIMEOUT') and (value < 1 or value > 900):
                            value = default
                        self._cache[cache_key] = value
                    except (ValueError, TypeError):
                        self._cache[cache_key] = default
        return self._cache[cache_key]
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Obtiene variable de entorno como booleano."""
        cache_key = f"{key}_bool"
        if cache_key not in self._cache:
            with self._lock:
                if cache_key not in self._cache:
                    value = os.environ.get(key, 'false' if not default else 'true')
                    self._cache[cache_key] = value.lower() in ('true', '1', 'yes', 'on')
        return self._cache[cache_key]
    
    # =============================================================================
    # AWS CONFIGURATION
    # =============================================================================
    
    @property
    def AWS_REGION(self) -> str:
        """Región de AWS - usa AWS_DEFAULT_REGION como fallback."""
        # Prioridad: AWS_REGION -> AWS_DEFAULT_REGION -> default
        region = self._get_env_cached('AWS_REGION', '')
        if not region:
            region = self._get_env_cached('AWS_DEFAULT_REGION', 'us-east-1')
        return region
    
    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        """Access Key ID de AWS."""
        return self._get_env_cached('AWS_ACCESS_KEY_ID', '')
    
    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        """Secret Access Key de AWS."""
        return self._get_env_cached('AWS_SECRET_ACCESS_KEY', '')
    
    # =============================================================================
    # S3 SETTINGS
    # =============================================================================
    
    @property
    def S3_BUCKET(self) -> str:
        """Bucket S3 para almacenar archivos temporales."""
        return self._get_env_cached('S3_BUCKET', 'lambda-temporal-documents-ia')
    
    @property
    def RULES_S3_PATH(self) -> str:
        """Ruta en S3 donde están las reglas de validación."""
        return "rules/rules_metadata.json"
    
    @property
    def TEMPLATE_PROMPT_S3_PATH(self) -> str:
        """Ruta en S3 donde esta el prompt que se usa con la IA."""
        return "template_prompt_files.md"
    
    @property
    def TEMPLATE_PROMPT_S3_PATH_STRUCTURE(self) -> str:
        """Ruta en S3 donde esta el prompt que se usa con la IA."""
        return "template_prompt_structure.md"
    
    # =============================================================================
    # LAMBDA FUNCTIONS
    # =============================================================================
    
    @property
    def GET_REPO_STRUCTURE_LAMBDA(self) -> str:
        """Lambda para obtener estructura de repositorio."""
        return self._get_env_cached('GET_REPO_STRUCTURE_LAMBDA', 'get_repository_info_lambda')
    
    @property
    def FILE_READER_LAMBDA(self) -> str:
        """Lambda para leer archivos."""
        return self._get_env_cached('FILE_READER_LAMBDA', 'file_reader_lambda')
    
    @property
    def REPORT_LAMBDA(self) -> str:
        """Lambda para generar reportes."""
        return self._get_env_cached('REPORT_LAMBDA', 'report_lambda')
    
    # =============================================================================
    # REPOSITORY ACCESS
    # =============================================================================
    
    @property
    def GITHUB_TOKEN(self) -> str:
        """Token de GitHub."""
        return self._get_env_cached('GITHUB_TOKEN', '')
    
    @property
    def GITHUB_BRANCH(self) -> str:
        """Rama por defecto."""
        return self._get_env_cached('GITHUB_BRANCH', 'main')
    
    @property
    def GITHUB_API_URL(self) -> str:
        """URL base de la API de GitHub."""
        return self._get_env_cached('GITHUB_API_URL', 'https://api.github.com')
    
    # =============================================================================
    # PROCESSING LIMITS
    # =============================================================================
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Tamaño máximo de archivo en bytes."""
        return self._get_env_int('MAX_FILE_SIZE_BYTES', 1048576)  # 1MB
    
    @property
    def MAX_FILES_PER_BATCH(self) -> int:
        """Máximo archivos por batch."""
        return self._get_env_int('MAX_FILES_PER_BATCH', 20)
    
    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Máximo contenido a procesar en caracteres."""
        return self._get_env_int('MAX_CONTENT_LENGTH', 100000)
    
    # =============================================================================
    # TIMEOUTS
    # =============================================================================
    
    @property
    def LAMBDA_TIMEOUT_SECONDS(self) -> int:
        """Timeout para invocaciones Lambda."""
        return self._get_env_int('LAMBDA_TIMEOUT_SECONDS', 60)
    
    @property
    def HTTP_TIMEOUT_SECONDS(self) -> int:
        """Timeout para requests HTTP."""
        return self._get_env_int('HTTP_TIMEOUT_SECONDS', 30)
    
    @property
    def GITHUB_API_TIMEOUT(self) -> int:
        """Timeout específico para GitHub API."""
        return self._get_env_int('GITHUB_API_TIMEOUT', 15)
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    
    @property
    def ENABLE_CACHING(self) -> bool:
        """Habilitar cache de respuestas."""
        return self._get_env_bool('ENABLE_CACHING', True)
    
    @property
    def ENABLE_RETRY(self) -> bool:
        """Habilitar reintentos automáticos."""
        return self._get_env_bool('ENABLE_RETRY', True)
    
    @property
    def ENABLE_LOGGING(self) -> bool:
        """Habilitar logging detallado."""
        return self._get_env_bool('ENABLE_LOGGING', True)
    
    @property
    def DEBUG_MODE(self) -> bool:
        """Modo debug."""
        return self._get_env_bool('DEBUG_MODE', False)
    
    # =============================================================================
    # RETRY CONFIGURATION
    # =============================================================================
    
    @property
    def MAX_RETRIES(self) -> int:
        """Número máximo de reintentos."""
        return self._get_env_int('MAX_RETRIES', 3)
    
    @property
    def RETRY_DELAY_SECONDS(self) -> int:
        """Delay base entre reintentos."""
        return self._get_env_int('RETRY_DELAY_SECONDS', 1)
    
    # =============================================================================
    # VALIDATION & UTILITIES
    # =============================================================================
    
    def is_configured(self) -> bool:
        """Verifica si la configuración básica está presente."""
        required_vars = [
            self.GET_REPO_STRUCTURE_LAMBDA,
            self.FILE_READER_LAMBDA,
            self.AWS_REGION
        ]
        return all(var.strip() for var in required_vars)
    
    def has_github_access(self) -> bool:
        """Verifica si hay acceso configurado a GitHub."""
        return bool(self.GITHUB_TOKEN.strip())
    
    def get_lambda_config(self) -> Dict[str, str]:
        """Obtiene configuración de lambdas como diccionario."""
        return {
            'get_repo_structure': self.GET_REPO_STRUCTURE_LAMBDA,
            'file_reader': self.FILE_READER_LAMBDA,
            'report': self.REPORT_LAMBDA
        }
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Obtiene configuración de timeouts."""
        return {
            'lambda': self.LAMBDA_TIMEOUT_SECONDS,
            'http': self.HTTP_TIMEOUT_SECONDS,
            'github_api': self.GITHUB_API_TIMEOUT
        }
    
    def clear_cache(self):
        """Limpia el cache de configuración (útil para testing)."""
        with self._lock:
            self._cache.clear()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de configuración para debugging."""
        return {
            'aws_region': self.AWS_REGION,
            'github_configured': self.has_github_access(),
            'lambdas_configured': self.is_configured(),
            'caching_enabled': self.ENABLE_CACHING,
            'retry_enabled': self.ENABLE_RETRY,
            'debug_mode': self.DEBUG_MODE,
            'max_file_size_mb': round(self.MAX_FILE_SIZE_BYTES / 1024 / 1024, 2),
            'timeouts': self.get_timeout_config()
        }


class OptimizedLogger:
    """Logger optimizado para AWS Lambda."""
    
    _loggers = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_logger(cls, name: str, debug: bool = None) -> logging.Logger:
        """Obtiene logger con cache para evitar recreaciones."""
        if name not in cls._loggers:
            with cls._lock:
                if name not in cls._loggers:
                    logger = logging.getLogger(name)
                    
                    # Determinar nivel
                    if debug is None:
                        debug = Config.DEBUG_MODE
                    level = logging.DEBUG if debug else logging.INFO
                    logger.setLevel(level)
                    
                    # Configurar handler solo si no existe
                    if not logger.handlers:
                        handler = logging.StreamHandler()
                        
                        # Formato optimizado para Lambda
                        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
                            # Formato para CloudWatch
                            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
                        else:
                            # Formato completo para desarrollo
                            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                        
                        handler.setFormatter(formatter)
                        logger.addHandler(handler)
                    
                    cls._loggers[name] = logger
        
        return cls._loggers[name]


def setup_logger(name: str, debug: bool = None) -> logging.Logger:
    """
    Configura logger optimizado.
    
    Args:
        name: Nombre del logger
        debug: Modo debug (usa Config.DEBUG_MODE si es None)
    
    Returns:
        Logger configurado
    """
    return OptimizedLogger.get_logger(name, debug)


# Instancia singleton de configuración
Config = Config()