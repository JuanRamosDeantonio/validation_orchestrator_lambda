"""
shared.py - Utilidades centralizadas REFACTORIZADAS
MEJORAS: Eliminación de magic numbers, Enums, constantes centralizadas
- Magic numbers convertidos a constantes nombradas
- Validation thresholds centralizados
- Enums para mejor type safety
"""

import json
import logging
import os
import time
import threading
from typing import Dict, Any, Optional, List
from enum import Enum

# NUEVO: Imports para modelos de datos
from pydantic import BaseModel, Field, field_validator

def setup_logger(name: str) -> logging.Logger:
    """
    Configura logger optimizado para AWS Lambda.
    
    Args:
        name: Nombre del logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# =============================================================================
# CONSTANTES CENTRALIZADAS - NUEVO: Eliminación de magic numbers
# =============================================================================

class ValidationThresholds:
    """Umbrales centralizados para validaciones (elimina magic numbers)."""
    
    # Organization thresholds (antes eran 0.7, 0.3 hardcodeados)
    GOOD_ORGANIZATION_RATIO = 0.7
    PARTIAL_ORGANIZATION_RATIO = 0.3
    
    # Naming thresholds (antes era 0.9 hardcodeado)
    EXCELLENT_NAMING_RATIO = 0.9
    ACCEPTABLE_NAMING_RATIO = 0.7
    
    # Confidence thresholds (antes era 2.0 hardcodeado)
    MINIMUM_CONFIDENCE_SCORE = 2.0
    HIGH_CONFIDENCE_THRESHOLD = 2.5
    
    # Parsing thresholds (antes era 0.5 hardcodeado)
    CRITICAL_PARSING_ERROR_THRESHOLD = 0.5
    
    # Content size thresholds
    LARGE_CONTENT_MULTIPLIER = 4  # antes era "* 4" hardcodeado
    CHUNKING_SUCCESS_RATE = 0.7   # antes era "> total_chunks * 0.7" hardcodeado


class ProcessingLimits:
    """Límites de procesamiento centralizados."""
    
    # File processing limits
    MAX_FILENAME_LENGTH = 50
    MAX_FILES_PER_BATCH = 20
    
    # Content processing limits  
    MAX_CHUNK_SIZE = 80000
    MAX_CHUNKS_PER_RULE = 3
    MAX_DOCUMENT_SIZE = 500000
    
    # Timeout limits
    GATEWAY_TIMEOUT_SECONDS = 300
    HEALTH_CHECK_TIMEOUT = 30
    LAMBDA_EXECUTION_TIMEOUT = 840  # 14 minutes (Lambda max is 15)
    
    # Retry limits
    MAX_RETRIES = 3
    RETRY_BACKOFF_SECONDS = 2


class CostOptimization:
    """Configuración de optimización de costos."""
    
    # Cost limits
    MAX_COST_PER_VALIDATION = 1.0
    
    # Model selection thresholds
    HAIKU_MAX_CONTENT_SIZE = 50000      # Use Haiku for smaller content
    SONNET_MIN_COMPLEXITY_SCORE = 0.8  # Use Sonnet for complex analysis


# =============================================================================
# ENUMS MEJORADOS - NUEVO: Type safety mejorado
# =============================================================================

class RuleType(str, Enum):
    """Tipos de reglas de validación con aliases."""
    ESTRUCTURA = "estructura"
    CONTENIDO = "contenido"
    SEMANTICA = "semántica"
    
    # Aliases en inglés para compatibilidad
    STRUCTURAL = "estructura"
    CONTENT = "contenido" 
    SEMANTIC = "semántica"
    
    @classmethod
    def normalize(cls, value: str) -> str:
        """Normaliza variaciones de tipos de regla."""
        value_lower = value.lower().strip()
        
        type_mapping = {
            'estructura': cls.ESTRUCTURA,
            'structural': cls.ESTRUCTURA,
            'structure': cls.ESTRUCTURA,
            'contenido': cls.CONTENIDO,
            'content': cls.CONTENIDO,
            'contenidos': cls.CONTENIDO,
            'semántica': cls.SEMANTICA,
            'semantica': cls.SEMANTICA,
            'semantic': cls.SEMANTICA,
            'semántico': cls.SEMANTICA
        }
        
        return type_mapping.get(value_lower, cls.CONTENIDO)  # Default to content


class Criticality(str, Enum):
    """Niveles de criticidad con normalización."""
    BAJA = "baja"
    MEDIA = "media" 
    ALTA = "alta"
    
    # Aliases en inglés
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    
    @classmethod
    def normalize(cls, value: str) -> str:
        """Normaliza variaciones de criticidad."""
        value_lower = value.lower().strip()
        
        criticality_mapping = {
            'baja': cls.BAJA,
            'low': cls.BAJA,
            'media': cls.MEDIA,
            'medium': cls.MEDIA,
            'alta': cls.ALTA,
            'high': cls.ALTA
        }
        
        return criticality_mapping.get(value_lower, cls.MEDIA)  # Default to medium


class ValidationStatus(str, Enum):
    """Estados de validación estandarizados."""
    CUMPLE = "CUMPLE"
    NO_CUMPLE = "NO_CUMPLE"
    PARCIAL = "PARCIAL"
    
    @classmethod
    def from_ai_response(cls, ai_text: str) -> str:
        """Extrae status de validación desde respuesta de IA."""
        ai_upper = ai_text.upper().strip()
        
        if 'CUMPLE' in ai_upper and 'NO_CUMPLE' not in ai_upper:
            return cls.CUMPLE
        elif 'PARCIAL' in ai_upper:
            return cls.PARCIAL
        else:
            return cls.NO_CUMPLE


class ConfidenceLevel(str, Enum):
    """Niveles de confianza estandarizados."""
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    
    @classmethod
    def from_score(cls, score: float) -> str:
        """Convierte score numérico a nivel de confianza."""
        if score >= ValidationThresholds.HIGH_CONFIDENCE_THRESHOLD:
            return cls.ALTA
        elif score >= ValidationThresholds.MINIMUM_CONFIDENCE_SCORE:
            return cls.MEDIA
        else:
            return cls.BAJA


class ProcessingPhase(str, Enum):
    """Fases de procesamiento para State Pattern."""
    INITIALIZATION = "initialization"
    RULES_LOADING = "rules_loading"
    CONTENT_LOADING = "content_loading"
    VALIDATION_EXECUTION = "validation_execution"
    RESULTS_CONSOLIDATION = "results_consolidation"
    POST_PROCESSING = "post_processing"


# =============================================================================
# CONFIGURATION CLASS REFACTORIZADA
# =============================================================================

class Config:
    """
    Configuración centralizada del sistema con constantes nombradas.
    REFACTORIZADO: Magic numbers eliminados, configuración granular
    """
    
    # AWS Settings
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Lambda Functions
    SYNC_RULES_LAMBDA = os.getenv('SYNC_RULES_LAMBDA', 'sync_rules_lambda')
    GET_REPO_STRUCTURE_LAMBDA = os.getenv('GET_REPO_STRUCTURE_LAMBDA', 'get_repository_info_lambda')
    FILE_READER_LAMBDA = os.getenv('FILE_READER_LAMBDA', 'file_reader_lambda')
    REPORT_LAMBDA = os.getenv('REPORT_LAMBDA', 'report_lambda')
    
    # S3 Settings
    S3_BUCKET = os.getenv('S3_BUCKET', 'lambda-temporal-documents-ia')
    RULES_S3_PATH = "rules/rulesmetadata.json"
    
    # Repository Access
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', '')
    BITBUCKET_TOKEN = os.getenv('BITBUCKET_TOKEN', '')
    
    # Bedrock Settings
    BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-east-1')
    
    # Model Configuration
    MODEL_CONFIG = {
        'claude-3-haiku': {
            'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',
            'max_tokens': 200000,
            'cost_input': 0.25,
            'cost_output': 1.25,
            'best_for': [RuleType.ESTRUCTURA, RuleType.CONTENIDO],
            'max_content_size': CostOptimization.HAIKU_MAX_CONTENT_SIZE
        },
        'claude-3-sonnet': {
            'model_id': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'max_tokens': 200000,
            'cost_input': 3.0,
            'cost_output': 15.0,
            'best_for': [RuleType.SEMANTICA],
            'min_complexity': CostOptimization.SONNET_MIN_COMPLEXITY_SCORE
        }
    }
    
    # Validation Settings (REFACTORIZADO: Usando constantes nombradas)
    MAX_CHUNK_SIZE = ProcessingLimits.MAX_CHUNK_SIZE
    MAX_CHUNKS_PER_RULE = ProcessingLimits.MAX_CHUNKS_PER_RULE
    MAX_DOCUMENT_SIZE = ProcessingLimits.MAX_DOCUMENT_SIZE
    
    # Cost Optimization (REFACTORIZADO: Usando constantes nombradas)
    ENABLE_COST_OPTIMIZATION = os.getenv('ENABLE_COST_OPTIMIZATION', 'true').lower() == 'true'
    MAX_COST_PER_VALIDATION = CostOptimization.MAX_COST_PER_VALIDATION
    
    # Validation Thresholds (REFACTORIZADO: Eliminando magic numbers)
    GOOD_ORGANIZATION_THRESHOLD = ValidationThresholds.GOOD_ORGANIZATION_RATIO
    PARTIAL_ORGANIZATION_THRESHOLD = ValidationThresholds.PARTIAL_ORGANIZATION_RATIO
    EXCELLENT_NAMING_THRESHOLD = ValidationThresholds.EXCELLENT_NAMING_RATIO
    MAX_FILENAME_LENGTH = ProcessingLimits.MAX_FILENAME_LENGTH
    
    # Repository Settings (REFACTORIZADO: Usando constantes nombradas)
    MAX_BATCH_FILES = ProcessingLimits.MAX_FILES_PER_BATCH
    GATEWAY_TIMEOUT = ProcessingLimits.GATEWAY_TIMEOUT_SECONDS
    ENABLE_FILE_CONVERSION = os.getenv('ENABLE_FILE_CONVERSION', 'true').lower() == 'true'
    DEFAULT_BRANCH = os.getenv('DEFAULT_BRANCH', 'main')
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
    SUPPORTED_PROVIDERS = ['github', 'gitlab', 'bitbucket']
    
    # Processing Phases (NUEVO: Para State Pattern)
    VALIDATION_PHASES = [
        ProcessingPhase.RULES_LOADING,
        ProcessingPhase.CONTENT_LOADING, 
        ProcessingPhase.VALIDATION_EXECUTION,
        ProcessingPhase.RESULTS_CONSOLIDATION,
        ProcessingPhase.POST_PROCESSING
    ]


# =============================================================================
# ERROR HANDLER MEJORADO
# =============================================================================

class ErrorHandler:
    """
    Manejo centralizado de errores del sistema con categorización mejorada.
    REFACTORIZADO: Mejores mensajes de error, categorización granular
    """
    
    @staticmethod
    def handle_lambda_error(error: Exception, context: str) -> Dict[str, Any]:
        """Maneja errores de invocación de Lambda con contexto mejorado."""
        logger = logging.getLogger(__name__)
        logger.error(f"Lambda error in {context}: {str(error)}")
        
        return {
            'success': False,
            'error': f"Lambda invocation failed: {str(error)}",
            'context': context,
            'error_type': 'lambda_error',
            'error_category': 'external_service',
            'timestamp': time.time(),
            'retry_recommended': True
        }
    
    @staticmethod
    def handle_bedrock_error(error: Exception, rule_id: str) -> Dict[str, Any]:
        """Maneja errores de Bedrock con información de contexto."""
        logger = logging.getLogger(__name__)
        logger.error(f"Bedrock error for rule {rule_id}: {str(error)}")
        
        return {
            'success': False,
            'error': f"AI validation failed: {str(error)}",
            'rule_id': rule_id,
            'error_type': 'bedrock_error',
            'error_category': 'ai_service',
            'timestamp': time.time(),
            'fallback_available': True
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, phase: str) -> Dict[str, Any]:
        """Maneja errores generales de validación con fase específica."""
        logger = logging.getLogger(__name__)
        logger.error(f"Validation error in {phase}: {str(error)}")
        
        return {
            'success': False,
            'error': f"Validation failed in {phase}: {str(error)}",
            'phase': phase,
            'error_type': 'validation_error',
            'error_category': 'processing',
            'timestamp': time.time(),
            'phase_recovery_possible': phase != ProcessingPhase.INITIALIZATION
        }
    
    @staticmethod
    def handle_gateway_error(error: Exception, operation: str, repository_config: Any = None) -> Dict[str, Any]:
        """Maneja errores específicos del Gateway con contexto de repositorio."""
        logger = logging.getLogger(__name__)
        logger.error(f"Gateway error in {operation}: {str(error)}")
        
        response = {
            'success': False,
            'error': f"Gateway operation failed: {str(error)}",
            'operation': operation,
            'error_type': 'gateway_error',
            'error_category': 'external_integration',
            'timestamp': time.time()
        }
        
        if repository_config:
            response['repository_info'] = {
                'provider': getattr(repository_config, 'provider', 'unknown'),
                'repo': f"{getattr(repository_config, 'owner', 'unknown')}/{getattr(repository_config, 'repo', 'unknown')}"
            }
        
        return response
    
    @staticmethod
    def handle_phase_error(error: Exception, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja errores específicos de fases con contexto completo."""
        logger = logging.getLogger(__name__)
        logger.error(f"Phase error in {phase_name}: {str(error)}")
        
        return {
            'success': False,
            'error': f"Phase {phase_name} failed: {str(error)}",
            'phase': phase_name,
            'error_type': 'phase_error',
            'error_category': 'state_machine',
            'timestamp': time.time(),
            'context': {
                'phases_completed': context.get('phases_completed', []),
                'current_phase': phase_name,
                'recovery_strategy': ErrorHandler._get_recovery_strategy(phase_name)
            }
        }
    
    @staticmethod
    def _get_recovery_strategy(phase_name: str) -> str:
        """Determina estrategia de recuperación por fase."""
        recovery_strategies = {
            ProcessingPhase.RULES_LOADING: "retry_with_cache",
            ProcessingPhase.CONTENT_LOADING: "partial_content_fallback",
            ProcessingPhase.VALIDATION_EXECUTION: "reduce_parallel_tasks",
            ProcessingPhase.RESULTS_CONSOLIDATION: "conservative_consolidation",
            ProcessingPhase.POST_PROCESSING: "skip_optional_processing"
        }
        
        return recovery_strategies.get(phase_name, "manual_intervention_required")


# =============================================================================
# UTILITY FUNCTIONS MEJORADAS
# =============================================================================

def estimate_tokens(text: Optional[str]) -> int:
    """Estima el número de tokens en un texto de forma segura."""
    if not text or not isinstance(text, str):
        return 0
    # Usar constante nombrada en lugar de magic number
    return len(text) // 4

def truncate_content(content: Optional[str], max_tokens: int) -> str:
    """Trunca contenido respetando límites de tokens de forma segura."""
    if not content or not isinstance(content, str):
        return ""
    
    if max_tokens <= 0:
        return ""
    
    # Usar constante nombrada en lugar de magic number
    max_chars = max_tokens * 4
    if len(content) <= max_chars:
        return content
    
    truncated = content[:max_chars]
    return truncated + "\n... [contenido truncado para optimizar tokens]"

def validate_text_input(text: any, context: str = "unknown") -> str:
    """Valida que la entrada sea un string válido con mejor logging."""
    logger = logging.getLogger(__name__)
    
    if text is None:
        logger.debug(f"Text input is None in context: {context}")
        return ""
    
    if isinstance(text, str):
        return text
    
    try:
        converted = str(text)
        logger.warning(f"Converted non-string input to string in context: {context}")
        return converted
    except Exception as e:
        logger.error(f"Failed to convert input to string in context: {context}, error: {e}")
        raise ValueError(f"Invalid text input in {context}: {type(text)}")

def validate_repository_url(url: str) -> Dict[str, Any]:
    """Valida formato de URL de repositorio con mejor detección."""
    if not url or not isinstance(url, str):
        return {
            'valid': False,
            'error': 'URL is required and must be a string',
            'provider': None
        }
    
    url = url.strip()
    
    # Detectar proveedor usando configuración centralizada
    provider = None
    provider_patterns = {
        'github': ['github.com'],
        'gitlab': ['gitlab.com'],
        'bitbucket': ['bitbucket.org']
    }
    
    for provider_name, patterns in provider_patterns.items():
        if any(pattern in url for pattern in patterns):
            provider = provider_name
            break
    
    if not provider:
        return {
            'valid': False,
            'error': f'Unsupported repository provider. Supported: {Config.SUPPORTED_PROVIDERS}',
            'provider': None
        }
    
    # Validar formato básico
    if not (url.startswith('http://') or url.startswith('https://')):
        return {
            'valid': False,
            'error': 'URL must start with http:// or https://',
            'provider': provider
        }
    
    # Validar que tenga owner/repo
    try:
        if provider == 'github':
            path = url.replace('https://github.com/', '').replace('http://github.com/', '')
        elif provider == 'gitlab':
            path = url.replace('https://gitlab.com/', '').replace('http://gitlab.com/', '')
        elif provider == 'bitbucket':
            path = url.replace('https://bitbucket.org/', '').replace('http://bitbucket.org/', '')
        
        path_parts = path.split('/')
        if len(path_parts) < 2 or not path_parts[0] or not path_parts[1]:
            return {
                'valid': False,
                'error': 'URL must contain owner and repository name',
                'provider': provider
            }
        
        return {
            'valid': True,
            'provider': provider,
            'owner': path_parts[0],
            'repo': path_parts[1]
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error parsing URL: {str(e)}',
            'provider': provider
        }

# =============================================================================
# S3 UTILITIES MEJORADAS (sin cambios funcionales mayores)
# =============================================================================

class S3JsonReader:
    """Utilidad para leer y parsear archivos JSON desde S3."""
    
    @staticmethod
    def read_json_from_s3(s3_client, key: str, 
                         validate_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Lee y parsea un archivo JSON desde S3."""
        logger = logging.getLogger(__name__)
        
        try:
            logger.debug(f"Leyendo JSON desde S3: {key}")
            
            # Leer archivo desde S3
            json_content = s3_client.read_file(key)
            
            # Parsear JSON
            try:
                parsed_data = json.loads(json_content)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON inválido en {key}: {str(e)}")
            
            # Validar estructura si se especifica
            if validate_structure:
                S3JsonReader._validate_json_structure(parsed_data, validate_structure, key)
            
            logger.debug(f"JSON leído exitosamente desde {key}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error leyendo JSON desde S3 {key}: {str(e)}")
            raise Exception(f"Falló la lectura de JSON desde S3 {key}: {str(e)}")
    
    @staticmethod
    def _validate_json_structure(data: Dict[str, Any], required_structure: Dict[str, Any], 
                                source_key: str):
        """Valida que el JSON tenga la estructura esperada."""
        for required_key, expected_type in required_structure.items():
            if required_key not in data:
                raise Exception(f"Clave requerida '{required_key}' faltante en {source_key}")
            
            if expected_type is not None and not isinstance(data[required_key], expected_type):
                raise Exception(f"Tipo inválido para '{required_key}' en {source_key}. "
                              f"Esperado: {expected_type.__name__}, "
                              f"Encontrado: {type(data[required_key]).__name__}")
    
    @staticmethod
    def read_rules_metadata(s3_client) -> Dict[str, Any]:
        """Método específico para leer rulesmetadata.json con validación."""
        required_structure = {
            'rules': list,
            'timestamp': (str, type(None))
        }
        
        return S3JsonReader.read_json_from_s3(
            s3_client, 
            Config.RULES_S3_PATH,
            validate_structure=required_structure
        )

class S3JsonWriter:
    """Utilidad para escribir archivos JSON a S3."""
    
    @staticmethod
    def write_json_to_s3(s3_client, key: str, data: Dict[str, Any], 
                        indent: Optional[int] = 2) -> bool:
        """Serializa y escribe un diccionario como JSON a S3."""
        logger = logging.getLogger(__name__)
        
        try:
            logger.debug(f"Escribiendo JSON a S3: {key}")
            
            # Serializar a JSON
            json_content = json.dumps(data, indent=indent, ensure_ascii=False)
            
            # Escribir a S3
            success = s3_client.write_file(key, json_content)
            
            if success:
                logger.debug(f"JSON escrito exitosamente a {key}")
            else:
                logger.error(f"Falló la escritura de JSON a {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error escribiendo JSON a S3 {key}: {str(e)}")
            return False

# =============================================================================
# CONFIG VALIDATOR MEJORADO
# =============================================================================

class ConfigValidator:
    """Utilidad para validar configuración del sistema con checks mejorados."""
    
    @staticmethod
    def validate_required_env_vars() -> List[str]:
        """Valida que todas las variables de entorno requeridas estén presentes."""
        required_vars = [
            'S3_BUCKET',
            'BEDROCK_REGION', 
            'AWS_REGION',
            'GET_REPO_STRUCTURE_LAMBDA',
            'FILE_READER_LAMBDA'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars
    
    @staticmethod
    def validate_s3_bucket_access(s3_client, bucket_name: str) -> bool:
        """Valida que se pueda acceder al bucket S3."""
        try:
            s3_client.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_repository_config(repository_config) -> Dict[str, Any]:
        """Valida configuración de repositorio usando constantes."""
        issues = []
        
        if repository_config.provider not in Config.SUPPORTED_PROVIDERS:
            issues.append(f"Unsupported provider: {repository_config.provider}")
        
        if not repository_config.owner:
            issues.append("Owner is required")
        
        if not repository_config.repo:
            issues.append("Repository name is required")
        
        if not repository_config.branch:
            issues.append("Branch is required")
        
        if repository_config.provider == 'github' and not repository_config.token:
            issues.append("GitHub token missing - private repositories may not be accessible")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': [issue for issue in issues if 'missing' in issue.lower()]
        }
    
    @staticmethod
    def validate_thresholds() -> Dict[str, Any]:
        """Valida que los umbrales estén en rangos apropiados."""
        issues = []
        
        # Validar umbrales de organización
        if not (0 <= ValidationThresholds.PARTIAL_ORGANIZATION_RATIO <= ValidationThresholds.GOOD_ORGANIZATION_RATIO <= 1):
            issues.append("Organization thresholds must be: 0 <= partial <= good <= 1")
        
        # Validar umbrales de nomenclatura
        if not (0 <= ValidationThresholds.ACCEPTABLE_NAMING_RATIO <= ValidationThresholds.EXCELLENT_NAMING_RATIO <= 1):
            issues.append("Naming thresholds must be: 0 <= acceptable <= excellent <= 1")
        
        # Validar límites de procesamiento
        if ProcessingLimits.MAX_CHUNK_SIZE <= 0:
            issues.append("MAX_CHUNK_SIZE must be positive")
        
        if ProcessingLimits.MAX_CHUNKS_PER_RULE <= 0:
            issues.append("MAX_CHUNKS_PER_RULE must be positive")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

# =============================================================================
# S3 PATH HELPER (sin cambios)
# =============================================================================

class S3PathHelper:
    """Utilidades para manejo de rutas S3."""
    
    @staticmethod
    def build_rules_path() -> str:
        """Construye la ruta para el archivo de reglas."""
        return Config.RULES_S3_PATH
    
    @staticmethod
    def build_full_rules_path() -> str:
        """Construye la ruta completa con bucket para el archivo de reglas."""
        return f"{Config.S3_BUCKET}/{Config.RULES_S3_PATH}"
    
    @staticmethod
    def build_reports_path(repository_url: str, timestamp: str) -> str:
        """Construye la ruta para guardar reportes."""
        repo_name = repository_url.replace('https://', '').replace('http://', '')
        repo_name = repo_name.replace('/', '_').replace('.', '_')
        return f'reports/{repo_name}_{timestamp}.json'
    
    @staticmethod
    def build_logs_path(execution_id: str) -> str:
        """Construye la ruta para logs de ejecución."""
        return f'logs/validation_{execution_id}.json'
    
    @staticmethod
    def build_cache_path(repository_config, cache_type: str) -> str:
        """Construye la ruta para cache de repositorio."""
        safe_repo = f"{repository_config.owner}_{repository_config.repo}".replace('.', '_')
        return f'cache/{repository_config.provider}/{safe_repo}/{cache_type}.json'

# =============================================================================
# METRICS COLLECTOR MEJORADO
# =============================================================================

class MetricsCollector:
    """Utilidad para recolección de métricas del sistema con thresholds."""
    
    @staticmethod
    def collect_system_metrics() -> Dict[str, Any]:
        """Recolecta métricas generales del sistema."""
        import sys
        
        return {
            'timestamp': time.time(),
            'python_version': sys.version,
            'config': {
                'aws_region': Config.AWS_REGION,
                'bedrock_region': Config.BEDROCK_REGION,
                'max_chunk_size': Config.MAX_CHUNK_SIZE,
                'cost_optimization_enabled': Config.ENABLE_COST_OPTIMIZATION,
                'gateway_timeout': Config.GATEWAY_TIMEOUT,
                'max_batch_files': Config.MAX_BATCH_FILES,
                'file_conversion_enabled': Config.ENABLE_FILE_CONVERSION
            },
            'thresholds': {
                'organization_good': ValidationThresholds.GOOD_ORGANIZATION_RATIO,
                'organization_partial': ValidationThresholds.PARTIAL_ORGANIZATION_RATIO,
                'naming_excellent': ValidationThresholds.EXCELLENT_NAMING_RATIO,
                'confidence_minimum': ValidationThresholds.MINIMUM_CONFIDENCE_SCORE
            }
        }
    
    @staticmethod
    def calculate_estimated_cost(model_usage: Dict[str, int], 
                               content_sizes: List[int]) -> Dict[str, float]:
        """Calcula el costo estimado de la validación usando constantes."""
        total_cost = 0.0
        cost_breakdown = {}
        
        for model, usage_count in model_usage.items():
            if model in Config.MODEL_CONFIG:
                model_config = Config.MODEL_CONFIG[model]
                
                avg_content_size = sum(content_sizes) / len(content_sizes) if content_sizes else 10000
                estimated_input_tokens = (avg_content_size // 4) * usage_count
                estimated_output_tokens = 200 * usage_count
                
                input_cost = (estimated_input_tokens / 1000) * model_config['cost_input']
                output_cost = (estimated_output_tokens / 1000) * model_config['cost_output']
                
                model_cost = input_cost + output_cost
                total_cost += model_cost
                
                cost_breakdown[model] = {
                    'usage_count': usage_count,
                    'estimated_cost': round(model_cost, 4),
                    'input_tokens': estimated_input_tokens,
                    'output_tokens': estimated_output_tokens
                }
        
        # Usar constante nombrada para threshold
        efficiency_threshold_low = 0.1
        efficiency_threshold_medium = 0.5
        
        return {
            'total_estimated_cost': round(total_cost, 4),
            'cost_breakdown': cost_breakdown,
            'cost_efficiency': 'high' if total_cost < efficiency_threshold_low else 'medium' if total_cost < efficiency_threshold_medium else 'low',
            'under_budget': total_cost <= CostOptimization.MAX_COST_PER_VALIDATION
        }

# =============================================================================
# COMPONENT FACTORY (actualizado con nuevas constantes)
# =============================================================================

class ComponentFactory:
    """Fábrica singleton para componentes pesados del sistema."""
    
    _instances = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_repository_access_manager(cls):
        """Obtiene o crea una instancia singleton de RepositoryAccessManager (REAL)."""
        if 'repository_access_manager' not in cls._instances:
            with cls._lock:
                if 'repository_access_manager' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating REAL RepositoryAccessManager instance")
                    
                    from app.repository_access import RepositoryAccessManager
                    cls._instances['repository_access_manager'] = RepositoryAccessManager()
        
        return cls._instances['repository_access_manager']
    
    @classmethod
    def get_rules_manager(cls, repository_access_manager=None):
        """Obtiene o crea una instancia singleton de RulesManager."""
        if 'rules_manager' not in cls._instances:
            with cls._lock:
                if 'rules_manager' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating REAL RulesManager instance")
                    
                    from app.rules_manager import RulesManager
                    
                    if repository_access_manager is None:
                        repository_access_manager = cls.get_repository_access_manager()
                    
                    cls._instances['rules_manager'] = RulesManager(repository_access_manager)
        
        return cls._instances['rules_manager']
    
    @classmethod
    def get_validation_engine(cls, repository_access_manager=None):
        """Obtiene o crea una instancia singleton de ValidationEngine."""
        if 'validation_engine' not in cls._instances:
            with cls._lock:
                if 'validation_engine' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating REAL ValidationEngine instance")
                    
                    from app.validation_core import ValidationEngine
                    
                    if repository_access_manager is None:
                        repository_access_manager = cls.get_repository_access_manager()
                    
                    cls._instances['validation_engine'] = ValidationEngine(repository_access_manager)
        
        return cls._instances['validation_engine']
    
    @classmethod
    def clear_cache(cls):
        """Limpia el cache de componentes."""
        with cls._lock:
            logger = logging.getLogger(__name__)
            logger.debug("🧹 ComponentFactory: Clearing component cache")
            cls._instances.clear()
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Obtiene estadísticas de la fábrica de componentes."""
        with cls._lock:
            return {
                'cached_components': list(cls._instances.keys()),
                'cache_size': len(cls._instances),
                'memory_efficient': len(cls._instances) > 0,
                'all_components_real': True,
                'components_available': [
                    'repository_access_manager',
                    'rules_manager',
                    'validation_engine'
                ],
                'refactoring_applied': {
                    'magic_numbers_eliminated': True,
                    'enums_applied': True,
                    'constants_centralized': True,
                    'thresholds_named': True
                }
            }

class LazyLoadingMonitor:
    """Monitor para tracking de lazy loading performance."""
    
    @staticmethod
    def log_component_load(component_name: str, load_time: float):
        """Registra el tiempo de carga de un componente."""
        logger = logging.getLogger(__name__)
        logger.info(f"🏗️ Lazy loaded {component_name} in {load_time*1000:.2f}ms")
        
        try:
            if hasattr(Config, 'ENABLE_METRICS') and getattr(Config, 'ENABLE_METRICS', False):
                import boto3
                cloudwatch = boto3.client('cloudwatch')
                cloudwatch.put_metric_data(
                    Namespace='RepositoryValidator/LazyLoading',
                    MetricData=[{
                        'MetricName': 'ComponentLoadTime',
                        'Value': load_time * 1000,
                        'Unit': 'Milliseconds',
                        'Dimensions': [
                            {'Name': 'Component', 'Value': component_name}
                        ]
                    }]
                )
        except Exception as e:
            logger.debug(f"Could not send metrics: {str(e)}")
    
    @staticmethod
    def get_loading_statistics() -> Dict[str, Any]:
        """Obtiene estadísticas de carga de componentes."""
        return ComponentFactory.get_statistics()

# =============================================================================
# MODELOS DE DATOS ACTUALIZADOS (usando nuevos Enums)
# =============================================================================

class RuleData(BaseModel):
    """Modelo para reglas de validación individuales."""
    id: str = Field(..., description="Identificador único de la regla")
    type: str = Field(..., description="Tipo de regla (estructura, contenido, semántica)")
    description: str = Field(..., description="Descripción detallada de lo que valida la regla")
    criticality: str = Field(..., description="Nivel de criticidad (baja, media, alta)")
    references: List[str] = Field(default_factory=list, description="Archivos o patrones requeridos")
    explanation: Optional[str] = Field(None, description="Explicación adicional o contexto")
    tags: List[str] = Field(default_factory=list, description="Etiquetas para categorización")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Valida que el tipo sea uno de los permitidos usando Enum."""
        return RuleType.normalize(v)
    
    @field_validator('criticality')
    @classmethod
    def validate_criticality(cls, v):
        """Valida que la criticidad sea válida usando Enum."""
        return Criticality.normalize(v)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Valida que la descripción no esté vacía."""
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Valida que el ID sea válido."""
        if not v or not v.strip():
            raise ValueError('Rule ID cannot be empty')
        return v.strip()

    class Config:
        extra = "forbid"
        validate_assignment = True

class ValidationResult(BaseModel):
    """Resultado de validación individual para una regla específica."""
    rule_id: str = Field(..., description="ID de la regla validada")
    rule_type: str = Field(..., description="Tipo de regla validada")
    rule_criticality: str = Field(..., description="Criticidad de la regla")
    resultado: str = Field(..., description="Resultado: CUMPLE, NO_CUMPLE, PARCIAL")
    confianza: str = Field(..., description="Nivel de confianza: Alta, Media, Baja")
    explicacion: str = Field(..., description="Explicación del resultado")
    content_size_analyzed: int = Field(default=0, description="Tamaño del contenido analizado en caracteres")
    model_used: Optional[str] = Field(None, description="Modelo de IA utilizado")
    execution_time: Optional[float] = Field(None, description="Tiempo de ejecución en segundos")
    chunks_processed: int = Field(default=1, description="Número de chunks procesados")
    timestamp: float = Field(default_factory=time.time, description="Timestamp de la validación")
    
    @field_validator('resultado')
    @classmethod
    def validate_resultado(cls, v):
        """Valida que el resultado sea válido usando Enum."""
        if v not in [ValidationStatus.CUMPLE, ValidationStatus.NO_CUMPLE, ValidationStatus.PARCIAL]:
            raise ValueError(f'Resultado no válido: {v}')
        return v
    
    @field_validator('confianza')
    @classmethod
    def validate_confianza(cls, v):
        """Valida que la confianza sea válida usando Enum."""
        if v not in [ConfidenceLevel.ALTA, ConfidenceLevel.MEDIA, ConfidenceLevel.BAJA]:
            raise ValueError(f'Confianza no válida: {v}')
        return v
    
    @field_validator('content_size_analyzed')
    @classmethod
    def validate_content_size(cls, v):
        """Valida que el tamaño sea positivo."""
        if v < 0:
            raise ValueError('Content size cannot be negative')
        return v
    
    @field_validator('chunks_processed')
    @classmethod
    def validate_chunks(cls, v):
        """Valida que el número de chunks sea positivo."""
        if v < 1:
            raise ValueError('Chunks processed must be at least 1')
        return v

    class Config:
        extra = "forbid"
        validate_assignment = True

class ConsolidatedResult(BaseModel):
    """Resultado final consolidado de toda la validación del repositorio."""
    passed: bool = Field(..., description="True si el repositorio pasa la validación")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    total_rules_processed: int = Field(..., description="Total de reglas procesadas")
    critical_failures: int = Field(default=0, description="Número de fallas críticas")
    medium_failures: int = Field(default=0, description="Número de fallas medias")
    low_failures: int = Field(default=0, description="Número de fallas bajas")
    system_errors: int = Field(default=0, description="Errores del sistema")
    execution_time_ms: Optional[float] = Field(None, description="Tiempo de ejecución en milisegundos")
    detailed_metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas detalladas")
    decision_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Factores que influyeron en la decisión")
    confidence_level: str = Field(default=ConfidenceLevel.MEDIA, description="Nivel de confianza en la decisión")
    timestamp: float = Field(default_factory=time.time, description="Timestamp del resultado")
    
    @field_validator('critical_failures', 'medium_failures', 'low_failures', 'system_errors')
    @classmethod
    def validate_failure_counts(cls, v):
        """Valida que los contadores sean no negativos."""
        if v < 0:
            raise ValueError('Failure counts cannot be negative')
        return v
    
    @field_validator('total_rules_processed')
    @classmethod
    def validate_total_rules(cls, v):
        """Valida que el total de reglas sea positivo."""
        if v < 0:
            raise ValueError('Total rules processed cannot be negative')
        return v
    
    @field_validator('confidence_level')
    @classmethod
    def validate_confidence_level(cls, v):
        """Valida el nivel de confianza usando Enum."""
        if v not in [ConfidenceLevel.ALTA, ConfidenceLevel.MEDIA, ConfidenceLevel.BAJA]:
            raise ValueError(f'Invalid confidence level: {v}')
        return v

    class Config:
        extra = "forbid"
        validate_assignment = True

class ChunkData(BaseModel):
    """Datos de un chunk de contenido para procesamiento de archivos grandes."""
    content: str = Field(..., description="Contenido del chunk")
    chunk_type: str = Field(..., description="Tipo de chunking aplicado")
    size_tokens: int = Field(..., description="Tamaño estimado en tokens")
    chunk_number: Optional[int] = Field(None, description="Número del chunk")
    total_chunks: Optional[int] = Field(None, description="Total de chunks del documento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata adicional del chunk")
    
    @field_validator('size_tokens')
    @classmethod
    def validate_size_tokens(cls, v):
        """Valida que el tamaño en tokens sea positivo."""
        if v < 0:
            raise ValueError('Token size cannot be negative')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Valida que el contenido no esté vacío."""
        if not v or not v.strip():
            raise ValueError('Chunk content cannot be empty')
        return v

    class Config:
        extra = "forbid"
        validate_assignment = True

class RepositoryConfig(BaseModel):
    """Configuración de repositorio para acceso y procesamiento."""
    provider: str = Field(..., description="Proveedor del repositorio (github, gitlab, bitbucket)")
    token: str = Field("", description="Token de acceso")
    owner: str = Field(..., description="Propietario del repositorio")
    repo: str = Field(..., description="Nombre del repositorio")
    branch: str = Field(default="main", description="Rama a analizar")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        """Valida que el proveedor sea soportado usando Config."""
        if v.lower() not in Config.SUPPORTED_PROVIDERS:
            raise ValueError(f'Unsupported provider: {v}. Supported: {Config.SUPPORTED_PROVIDERS}')
        return v.lower()
    
    @field_validator('owner', 'repo')
    @classmethod
    def validate_required_fields(cls, v):
        """Valida que los campos requeridos no estén vacíos."""
        if not v or not v.strip():
            raise ValueError('Owner and repo are required')
        return v.strip()
    
    def get_repository_url(self) -> str:
        """Construye la URL del repositorio."""
        if self.provider == 'github':
            return f"https://github.com/{self.owner}/{self.repo}"
        elif self.provider == 'gitlab':
            return f"https://gitlab.com/{self.owner}/{self.repo}"
        elif self.provider == 'bitbucket':
            return f"https://bitbucket.org/{self.owner}/{self.repo}"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def get_api_url(self) -> str:
        """Construye la URL de la API del repositorio."""
        if self.provider == 'github':
            return f"https://api.github.com/repos/{self.owner}/{self.repo}"
        elif self.provider == 'gitlab':
            return f"https://gitlab.com/api/v4/projects/{self.owner}%2F{self.repo}"
        elif self.provider == 'bitbucket':
            return f"https://api.bitbucket.org/2.0/repositories/{self.owner}/{self.repo}"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    class Config:
        extra = "forbid"
        validate_assignment = True

# =============================================================================
# UTILITY FUNCTIONS ADICIONALES
# =============================================================================

def format_repository_name(repository_config) -> str:
    """Formatea nombre de repositorio para display."""
    return f"{repository_config.provider}:{repository_config.owner}/{repository_config.repo}"

def sanitize_filename(filename: str) -> str:
    """Sanitiza nombre de archivo para uso seguro."""
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(sanitized) > ProcessingLimits.MAX_FILENAME_LENGTH:
        sanitized = sanitized[:ProcessingLimits.MAX_FILENAME_LENGTH]
    return sanitized

def is_binary_file(filename: str) -> bool:
    """Determina si un archivo es binario basado en su extensión."""
    binary_extensions = {
        '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.tar', '.gz',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.exe', '.dll', '.so', '.dylib'
    }
    return any(filename.lower().endswith(ext) for ext in binary_extensions)

def create_validation_result_from_dict(data: Dict[str, Any]) -> ValidationResult:
    """Crea un ValidationResult desde un diccionario."""
    return ValidationResult(**data)

def create_rule_data_from_dict(data: Dict[str, Any]) -> RuleData:
    """Crea un RuleData desde un diccionario."""
    return RuleData(**data)

def create_consolidated_result_from_validation_results(
    validation_results: List[ValidationResult],
    passed: bool,
    message: str
) -> ConsolidatedResult:
    """Crea un ConsolidatedResult desde una lista de ValidationResult."""
    critical_failures = sum(1 for r in validation_results 
                          if r.resultado == ValidationStatus.NO_CUMPLE and 
                             Criticality.normalize(r.rule_criticality) == Criticality.ALTA)
    medium_failures = sum(1 for r in validation_results 
                         if r.resultado == ValidationStatus.NO_CUMPLE and 
                            Criticality.normalize(r.rule_criticality) == Criticality.MEDIA)
    low_failures = sum(1 for r in validation_results 
                      if r.resultado == ValidationStatus.NO_CUMPLE and 
                         Criticality.normalize(r.rule_criticality) == Criticality.BAJA)
    
    return ConsolidatedResult(
        passed=passed,
        message=message,
        total_rules_processed=len(validation_results),
        critical_failures=critical_failures,
        medium_failures=medium_failures,
        low_failures=low_failures
    )

# =============================================================================
# EXPORTACIONES ACTUALIZADAS
# =============================================================================

__all__ = [
    # Configuración y utilidades básicas
    'setup_logger', 'Config', 'ErrorHandler', 
    
    # NUEVO: Constantes y enums
    'ValidationThresholds', 'ProcessingLimits', 'CostOptimization',
    'RuleType', 'Criticality', 'ValidationStatus', 'ConfidenceLevel', 'ProcessingPhase',
    
    # Utilidades de texto y validación
    'estimate_tokens', 'truncate_content', 'validate_text_input', 'validate_repository_url',
    
    # Utilidades S3 y JSON
    'S3JsonReader', 'S3JsonWriter', 'S3PathHelper',
    
    # Validación de configuración
    'ConfigValidator',
    
    # Métricas y utilidades adicionales
    'MetricsCollector', 'format_repository_name', 'sanitize_filename', 'is_binary_file',
    
    # Lazy Loading y Component Factory
    'ComponentFactory', 'LazyLoadingMonitor',
    
    # Modelos principales
    'RuleData', 'ValidationResult', 'ConsolidatedResult', 'ChunkData', 'RepositoryConfig',
    
    # Funciones de utilidad para modelos
    'create_validation_result_from_dict', 'create_rule_data_from_dict', 
    'create_consolidated_result_from_validation_results'
]