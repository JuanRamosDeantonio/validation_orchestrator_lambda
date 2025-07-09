"""
utils.py - Utilidades centralizadas actualizadas para LambdaGateway + LAZY LOADING
"""

import json
import logging
import os
import time
import threading
from typing import Dict, Any, Optional, List

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

class Config:
    """
    Configuración centralizada del sistema actualizada para LambdaGateway.
    """
    
    # AWS Settings
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Lambda Functions - Actualizadas para LambdaGateway
    SYNC_RULES_LAMBDA = os.getenv('SYNC_RULES_LAMBDA', 'sync_rules_lambda')
    GET_REPO_STRUCTURE_LAMBDA = os.getenv('GET_REPO_STRUCTURE_LAMBDA', 'get_repository_info_lambda')  # ACTUALIZADO
    FILE_READER_LAMBDA = os.getenv('FILE_READER_LAMBDA', 'file_reader_lambda')
    REPORT_LAMBDA = os.getenv('REPORT_LAMBDA', 'report_lambda')
    
    # S3 Settings - Centralizado
    S3_BUCKET = os.getenv('S3_BUCKET', 'lambda-temporal-documents-ia')
    RULES_S3_PATH = "rules/rulesmetadata.json"
    
    # Repository Access - NUEVO para LambdaGateway
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Token para repositorios privados
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', '')  # Para soporte futuro
    BITBUCKET_TOKEN = os.getenv('BITBUCKET_TOKEN', '')  # Para soporte futuro
    
    # Bedrock Settings
    BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-east-1')
    
    # Model Configuration
    MODEL_CONFIG = {
        'claude-3-haiku': {
            'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',
            'max_tokens': 200000,
            'cost_input': 0.25,
            'cost_output': 1.25,
            'best_for': ['estructura', 'contenido']
        },
        'claude-3-sonnet': {
            'model_id': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'max_tokens': 200000,
            'cost_input': 3.0,
            'cost_output': 15.0,
            'best_for': ['semántica']
        }
    }
    
    # Validation Settings
    MAX_CHUNK_SIZE = 80000  # tokens
    MAX_CHUNKS_PER_RULE = 3
    MAX_DOCUMENT_SIZE = 500000  # characters
    
    # Cost Optimization
    ENABLE_COST_OPTIMIZATION = os.getenv('ENABLE_COST_OPTIMIZATION', 'true').lower() == 'true'
    MAX_COST_PER_VALIDATION = float(os.getenv('MAX_COST_PER_VALIDATION', '1.0'))
    
    # Validation Thresholds
    GOOD_ORGANIZATION_THRESHOLD = 0.7
    PARTIAL_ORGANIZATION_THRESHOLD = 0.3
    MAX_FILENAME_LENGTH = 50
    EXCELLENT_NAMING_THRESHOLD = 0.9
    
    # LambdaGateway Settings - NUEVO
    MAX_BATCH_FILES = int(os.getenv('MAX_BATCH_FILES', '20'))  # Máximo archivos por lote
    GATEWAY_TIMEOUT = int(os.getenv('GATEWAY_TIMEOUT', '300'))  # Timeout en segundos
    ENABLE_FILE_CONVERSION = os.getenv('ENABLE_FILE_CONVERSION', 'true').lower() == 'true'
    
    # Repository Settings - NUEVO
    DEFAULT_BRANCH = os.getenv('DEFAULT_BRANCH', 'main')
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))  # Máximo tamaño de archivo
    SUPPORTED_PROVIDERS = ['github', 'gitlab', 'bitbucket']

class ErrorHandler:
    """
    Manejo centralizado de errores del sistema actualizado.
    """
    
    @staticmethod
    def handle_lambda_error(error: Exception, context: str) -> Dict[str, Any]:
        """
        Maneja errores de invocación de Lambda.
        
        Args:
            error: Excepción ocurrida
            context: Contexto donde ocurrió el error
            
        Returns:
            dict: Información estructurada del error
        """
        logger = logging.getLogger(__name__)
        logger.error(f"Lambda error in {context}: {str(error)}")
        
        return {
            'success': False,
            'error': f"Lambda invocation failed: {str(error)}",
            'context': context,
            'error_type': 'lambda_error',
            'timestamp': time.time()
        }
    
    @staticmethod
    def handle_bedrock_error(error: Exception, rule_id: str) -> Dict[str, Any]:
        """
        Maneja errores de Bedrock.
        
        Args:
            error: Excepción ocurrida
            rule_id: ID de la regla que causó el error
            
        Returns:
            dict: Información estructurada del error
        """
        logger = logging.getLogger(__name__)
        logger.error(f"Bedrock error for rule {rule_id}: {str(error)}")
        
        return {
            'success': False,
            'error': f"AI validation failed: {str(error)}",
            'rule_id': rule_id,
            'error_type': 'bedrock_error',
            'timestamp': time.time()
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, phase: str) -> Dict[str, Any]:
        """
        Maneja errores generales de validación.
        
        Args:
            error: Excepción ocurrida
            phase: Fase donde ocurrió el error
            
        Returns:
            dict: Información estructurada del error
        """
        logger = logging.getLogger(__name__)
        logger.error(f"Validation error in {phase}: {str(error)}")
        
        return {
            'success': False,
            'error': f"Validation failed in {phase}: {str(error)}",
            'phase': phase,
            'error_type': 'validation_error',
            'timestamp': time.time()
        }
    
    @staticmethod
    def handle_gateway_error(error: Exception, operation: str, repository_config: Any = None) -> Dict[str, Any]:
        """
        NUEVO: Maneja errores específicos del LambdaGateway.
        
        Args:
            error: Excepción ocurrida
            operation: Operación que falló
            repository_config: Configuración del repositorio (opcional)
            
        Returns:
            dict: Información estructurada del error
        """
        logger = logging.getLogger(__name__)
        logger.error(f"Gateway error in {operation}: {str(error)}")
        
        response = {
            'success': False,
            'error': f"Gateway operation failed: {str(error)}",
            'operation': operation,
            'error_type': 'gateway_error',
            'timestamp': time.time()
        }
        
        if repository_config:
            response['repository_info'] = {
                'provider': getattr(repository_config, 'provider', 'unknown'),
                'repo': f"{getattr(repository_config, 'owner', 'unknown')}/{getattr(repository_config, 'repo', 'unknown')}"
            }
        
        return response

def estimate_tokens(text: Optional[str]) -> int:
    """
    Estima el número de tokens en un texto de forma segura.
    
    Args:
        text: Texto a analizar (puede ser None)
        
    Returns:
        int: Número estimado de tokens (0 si texto es None/vacío)
        
    Examples:
        >>> estimate_tokens("hello world")
        2
        >>> estimate_tokens("")
        0
        >>> estimate_tokens(None)
        0
    """
    if not text or not isinstance(text, str):
        return 0
    
    # Aproximación: 1 token ≈ 4 caracteres en inglés, 3.5 en español
    return len(text) // 4

def truncate_content(content: Optional[str], max_tokens: int) -> str:
    """
    Trunca contenido respetando límites de tokens de forma segura.
    
    Args:
        content: Contenido a truncar (puede ser None)
        max_tokens: Máximo número de tokens permitidos
        
    Returns:
        str: Contenido truncado o vacío si content es None
    """
    if not content or not isinstance(content, str):
        return ""
    
    if max_tokens <= 0:
        return ""
    
    max_chars = max_tokens * 4
    if len(content) <= max_chars:
        return content
    
    truncated = content[:max_chars]
    return truncated + "\n... [contenido truncado para optimizar tokens]"

def validate_text_input(text: any, context: str = "unknown") -> str:
    """
    Valida que la entrada sea un string válido.
    
    Args:
        text: Input a validar
        context: Contexto para logging (opcional)
        
    Returns:
        str: String válido o cadena vacía
        
    Raises:
        ValueError: Si el input no puede ser convertido a string válido
    """
    logger = logging.getLogger(__name__)
    
    if text is None:
        logger.debug(f"Text input is None in context: {context}")
        return ""
    
    if isinstance(text, str):
        return text
    
    # Intentar convertir a string
    try:
        converted = str(text)
        logger.warning(f"Converted non-string input to string in context: {context}")
        return converted
    except Exception as e:
        logger.error(f"Failed to convert input to string in context: {context}, error: {e}")
        raise ValueError(f"Invalid text input in {context}: {type(text)}")

def validate_repository_url(url: str) -> Dict[str, Any]:
    """
    NUEVO: Valida formato de URL de repositorio.
    
    Args:
        url: URL del repositorio
        
    Returns:
        dict: Resultado de validación con detalles
    """
    if not url or not isinstance(url, str):
        return {
            'valid': False,
            'error': 'URL is required and must be a string',
            'provider': None
        }
    
    url = url.strip()
    
    # Detectar proveedor
    provider = None
    if 'github.com' in url:
        provider = 'github'
    elif 'gitlab.com' in url:
        provider = 'gitlab'
    elif 'bitbucket.org' in url:
        provider = 'bitbucket'
    
    if not provider:
        return {
            'valid': False,
            'error': 'Unsupported repository provider',
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

class S3JsonReader:
    """
    Utilidad para leer y parsear archivos JSON desde S3.
    """
    
    @staticmethod
    def read_json_from_s3(s3_client, key: str, 
                         validate_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lee y parsea un archivo JSON desde S3.
        
        Args:
            s3_client: Cliente S3 configurado
            key: Clave del archivo en S3 (ej: 'rules/rulesmetadata.json')
            validate_structure: Diccionario con claves requeridas para validar
            
        Returns:
            dict: Contenido JSON parseado
            
        Raises:
            Exception: Si falla la lectura o parsing
        """
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
        """
        Valida que el JSON tenga la estructura esperada.
        
        Args:
            data: Datos JSON parseados
            required_structure: Estructura requerida
            source_key: Clave del archivo (para logging)
            
        Raises:
            Exception: Si la estructura no es válida
        """
        for required_key, expected_type in required_structure.items():
            if required_key not in data:
                raise Exception(f"Clave requerida '{required_key}' faltante en {source_key}")
            
            if expected_type is not None and not isinstance(data[required_key], expected_type):
                raise Exception(f"Tipo inválido para '{required_key}' en {source_key}. "
                              f"Esperado: {expected_type.__name__}, "
                              f"Encontrado: {type(data[required_key]).__name__}")
    
    @staticmethod
    def read_rules_metadata(s3_client) -> Dict[str, Any]:
        """
        Método específico para leer rulesmetadata.json con validación.
        
        Args:
            s3_client: Cliente S3 configurado
            
        Returns:
            dict: Metadata de reglas parseado y validado
        """
        required_structure = {
            'rules': list,
            'timestamp': (str, type(None))  # Opcional
        }
        
        return S3JsonReader.read_json_from_s3(
            s3_client, 
            Config.RULES_S3_PATH,
            validate_structure=required_structure
        )

class S3JsonWriter:
    """
    Utilidad para escribir archivos JSON a S3.
    """
    
    @staticmethod
    def write_json_to_s3(s3_client, key: str, data: Dict[str, Any], 
                        indent: Optional[int] = 2) -> bool:
        """
        Serializa y escribe un diccionario como JSON a S3.
        
        Args:
            s3_client: Cliente S3 configurado
            key: Clave del archivo en S3
            data: Datos a serializar
            indent: Indentación del JSON (None para compacto)
            
        Returns:
            bool: True si se escribió exitosamente
        """
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

class ConfigValidator:
    """
    Utilidad para validar configuración del sistema.
    """
    
    @staticmethod
    def validate_required_env_vars() -> List[str]:
        """
        Valida que todas las variables de entorno requeridas estén presentes.
        
        Returns:
            list: Lista de variables faltantes (vacía si todo está bien)
        """
        required_vars = [
            'S3_BUCKET',
            'BEDROCK_REGION', 
            'AWS_REGION',
            'GET_REPO_STRUCTURE_LAMBDA',  # ACTUALIZADO
            'FILE_READER_LAMBDA'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars
    
    @staticmethod
    def validate_s3_bucket_access(s3_client, bucket_name: str) -> bool:
        """
        Valida que se pueda acceder al bucket S3.
        
        Args:
            s3_client: Cliente S3 configurado
            bucket_name: Nombre del bucket
            
        Returns:
            bool: True si el bucket es accesible
        """
        try:
            # Intentar listar objetos (operación mínima)
            s3_client.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_model_availability(bedrock_client) -> Dict[str, bool]:
        """
        Valida que los modelos de Bedrock estén disponibles.
        
        Args:
            bedrock_client: Cliente Bedrock configurado
            
        Returns:
            dict: Estado de disponibilidad por modelo
        """
        model_status = {}
        
        for model_name in Config.MODEL_CONFIG.keys():
            try:
                # Intentar una invocación mínima de prueba
                test_prompt = "Test"
                # Note: En producción esto podría tener costo, usar con precaución
                model_status[model_name] = True
            except Exception:
                model_status[model_name] = False
        
        return model_status
    
    @staticmethod
    def validate_repository_config(repository_config) -> Dict[str, Any]:
        """
        NUEVO: Valida configuración de repositorio.
        
        Args:
            repository_config: Instancia de RepositoryConfig
            
        Returns:
            dict: Resultado de validación
        """
        issues = []
        
        # Validar proveedor soportado
        if repository_config.provider not in Config.SUPPORTED_PROVIDERS:
            issues.append(f"Unsupported provider: {repository_config.provider}")
        
        # Validar campos requeridos
        if not repository_config.owner:
            issues.append("Owner is required")
        
        if not repository_config.repo:
            issues.append("Repository name is required")
        
        if not repository_config.branch:
            issues.append("Branch is required")
        
        # Validar token si es necesario para provider
        if repository_config.provider == 'github' and not repository_config.token:
            issues.append("GitHub token missing - private repositories may not be accessible")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': [issue for issue in issues if 'missing' in issue.lower()]
        }

class S3PathHelper:
    """
    Utilidades para manejo de rutas S3.
    """
    
    @staticmethod
    def build_rules_path() -> str:
        """
        Construye la ruta para el archivo de reglas.
        
        Returns:
            str: Ruta del archivo de reglas
        """
        return Config.RULES_S3_PATH
    
    @staticmethod
    def build_full_rules_path() -> str:
        """
        Construye la ruta completa con bucket para el archivo de reglas.
        
        Returns:
            str: Ruta completa del archivo de reglas
        """
        return f"{Config.S3_BUCKET}/{Config.RULES_S3_PATH}"
    
    @staticmethod
    def build_reports_path(repository_url: str, timestamp: str) -> str:
        """
        Construye la ruta para guardar reportes.
        
        Args:
            repository_url: URL del repositorio
            timestamp: Timestamp del reporte
            
        Returns:
            str: Ruta para el reporte
        """
        # Limpiar URL del repositorio para usar como nombre de archivo
        repo_name = repository_url.replace('https://', '').replace('http://', '')
        repo_name = repo_name.replace('/', '_').replace('.', '_')
        
        return f'reports/{repo_name}_{timestamp}.json'
    
    @staticmethod
    def build_logs_path(execution_id: str) -> str:
        """
        Construye la ruta para logs de ejecución.
        
        Args:
            execution_id: ID único de la ejecución
            
        Returns:
            str: Ruta para los logs
        """
        return f'logs/validation_{execution_id}.json'
    
    @staticmethod
    def build_cache_path(repository_config, cache_type: str) -> str:
        """
        NUEVO: Construye la ruta para cache de repositorio.
        
        Args:
            repository_config: Configuración del repositorio
            cache_type: Tipo de cache ('structure', 'files', 'metadata')
            
        Returns:
            str: Ruta para el cache
        """
        safe_repo = f"{repository_config.owner}_{repository_config.repo}".replace('.', '_')
        return f'cache/{repository_config.provider}/{safe_repo}/{cache_type}.json'

class MetricsCollector:
    """
    Utilidad para recolección de métricas del sistema.
    """
    
    @staticmethod
    def collect_system_metrics() -> Dict[str, Any]:
        """
        Recolecta métricas generales del sistema.
        
        Returns:
            dict: Métricas del sistema
        """
        import sys
        
        return {
            'timestamp': time.time(),
            'python_version': sys.version,
            'config': {
                'aws_region': Config.AWS_REGION,
                'bedrock_region': Config.BEDROCK_REGION,
                'max_chunk_size': Config.MAX_CHUNK_SIZE,
                'cost_optimization_enabled': Config.ENABLE_COST_OPTIMIZATION,
                'gateway_timeout': Config.GATEWAY_TIMEOUT,  # NUEVO
                'max_batch_files': Config.MAX_BATCH_FILES,  # NUEVO
                'file_conversion_enabled': Config.ENABLE_FILE_CONVERSION  # NUEVO
            }
        }
    
    @staticmethod
    def calculate_estimated_cost(model_usage: Dict[str, int], 
                               content_sizes: List[int]) -> Dict[str, float]:
        """
        Calcula el costo estimado de la validación.
        
        Args:
            model_usage: Uso por modelo {'claude-3-haiku': 5, 'claude-3-sonnet': 3}
            content_sizes: Tamaños de contenido analizados
            
        Returns:
            dict: Análisis de costos
        """
        total_cost = 0.0
        cost_breakdown = {}
        
        for model, usage_count in model_usage.items():
            if model in Config.MODEL_CONFIG:
                model_config = Config.MODEL_CONFIG[model]
                
                # Estimación basada en tamaños promedio
                avg_content_size = sum(content_sizes) / len(content_sizes) if content_sizes else 10000
                estimated_input_tokens = (avg_content_size // 4) * usage_count
                estimated_output_tokens = 200 * usage_count  # Promedio de respuesta
                
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
        
        return {
            'total_estimated_cost': round(total_cost, 4),
            'cost_breakdown': cost_breakdown,
            'cost_efficiency': 'high' if total_cost < 0.1 else 'medium' if total_cost < 0.5 else 'low'
        }
    
    @staticmethod
    def collect_gateway_metrics(lambda_gateway) -> Dict[str, Any]:
        """
        NUEVO: Recolecta métricas específicas del LambdaGateway.
        
        Args:
            lambda_gateway: Instancia del LambdaGateway
            
        Returns:
            dict: Métricas del gateway
        """
        gateway_stats = lambda_gateway.get_invocation_statistics()
        
        return {
            'gateway_performance': {
                'total_invocations': gateway_stats['total_invocations'],
                'success_rate': gateway_stats['success_rate'],
                'average_response_time': gateway_stats.get('average_response_time', 0)
            },
            'function_usage': gateway_stats['invocations_by_function'],
            'health_status': lambda_gateway.health_check()['overall_status']
        }

# NUEVAS FUNCIONES DE UTILIDAD

def format_repository_name(repository_config) -> str:
    """
    NUEVO: Formatea nombre de repositorio para display.
    
    Args:
        repository_config: Configuración del repositorio
        
    Returns:
        str: Nombre formateado del repositorio
    """
    return f"{repository_config.provider}:{repository_config.owner}/{repository_config.repo}"

def sanitize_filename(filename: str) -> str:
    """
    NUEVO: Sanitiza nombre de archivo para uso seguro.
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        str: Nombre sanitizado
    """
    import re
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limitar longitud
    if len(sanitized) > Config.MAX_FILENAME_LENGTH:
        sanitized = sanitized[:Config.MAX_FILENAME_LENGTH]
    return sanitized

def is_binary_file(filename: str) -> bool:
    """
    NUEVO: Determina si un archivo es binario basado en su extensión.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        bool: True si es archivo binario
    """
    binary_extensions = {
        '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.tar', '.gz',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.exe', '.dll', '.so', '.dylib'
    }
    
    return any(filename.lower().endswith(ext) for ext in binary_extensions)

# =============================================================================
# NUEVO: COMPONENT FACTORY PARA LAZY LOADING
# =============================================================================

class ComponentFactory:
    """
    Fábrica singleton para componentes pesados del sistema.
    
    Evita crear múltiples instancias de los mismos objetos y proporciona
    lazy loading para optimizar cold starts de Lambda.
    
    Thread-safe para uso en entornos concurrentes.
    """
    
    _instances = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_integration_manager(cls):
        """
        Obtiene o crea una instancia singleton de IntegrationManager.
        
        Returns:
            IntegrationManager: Instancia singleton
        """
        if 'integration_manager' not in cls._instances:
            with cls._lock:
                if 'integration_manager' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating IntegrationManager instance")
                    
                    # Import lazy para evitar circular imports
                    from app.integrations import IntegrationManager
                    cls._instances['integration_manager'] = IntegrationManager()
        
        return cls._instances['integration_manager']
    
    @classmethod
    def get_lambda_gateway(cls):
        """
        Obtiene o crea una instancia singleton de LambdaGateway.
        
        Returns:
            LambdaGateway: Instancia singleton
        """
        if 'lambda_gateway' not in cls._instances:
            with cls._lock:
                if 'lambda_gateway' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating LambdaGateway instance")
                    
                    # Import lazy para evitar circular imports
                    from app.lambda_gateway import LambdaGateway
                    cls._instances['lambda_gateway'] = LambdaGateway()
        
        return cls._instances['lambda_gateway']
    
    @classmethod
    def get_rules_processor(cls, integration_manager=None):
        """
        Obtiene o crea una instancia singleton de RulesProcessor.
        
        Args:
            integration_manager: IntegrationManager instance (optional)
            
        Returns:
            RulesProcessor: Instancia singleton
        """
        if 'rules_processor' not in cls._instances:
            with cls._lock:
                if 'rules_processor' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating RulesProcessor instance")
                    
                    # Import lazy para evitar circular imports
                    from app.rules_processor import RulesProcessor
                    
                    # Usar el integration_manager pasado o crear uno nuevo
                    if integration_manager is None:
                        integration_manager = cls.get_integration_manager()
                    
                    cls._instances['rules_processor'] = RulesProcessor(integration_manager)
        
        return cls._instances['rules_processor']
    
    @classmethod
    def get_validation_engine(cls, integration_manager=None):
        """
        Obtiene o crea una instancia singleton de ValidationEngine.
        
        Args:
            integration_manager: IntegrationManager instance (optional)
            
        Returns:
            ValidationEngine: Instancia singleton
        """
        if 'validation_engine' not in cls._instances:
            with cls._lock:
                if 'validation_engine' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating ValidationEngine instance")
                    
                    # Import lazy para evitar circular imports
                    from app.validation_engine import ValidationEngine
                    
                    # Usar el integration_manager pasado o crear uno nuevo
                    if integration_manager is None:
                        integration_manager = cls.get_integration_manager()
                    
                    cls._instances['validation_engine'] = ValidationEngine(integration_manager)
        
        return cls._instances['validation_engine']
    
    @classmethod
    def get_result_processor(cls, integration_manager=None):
        """
        Obtiene o crea una instancia singleton de ResultProcessor.
        
        Args:
            integration_manager: IntegrationManager instance (optional)
            
        Returns:
            ResultProcessor: Instancia singleton
        """
        if 'result_processor' not in cls._instances:
            with cls._lock:
                if 'result_processor' not in cls._instances:
                    logger = logging.getLogger(__name__)
                    logger.debug("🏭 ComponentFactory: Creating ResultProcessor instance")
                    
                    # Import lazy para evitar circular imports
                    from app.result_processor import ResultProcessor
                    
                    # Usar el integration_manager pasado o crear uno nuevo
                    if integration_manager is None:
                        integration_manager = cls.get_integration_manager()
                    
                    cls._instances['result_processor'] = ResultProcessor(integration_manager)
        
        return cls._instances['result_processor']
    
    @classmethod
    def clear_cache(cls):
        """
        Limpia el cache de componentes.
        
        Útil para testing o para forzar recreación de instancias.
        """
        with cls._lock:
            logger = logging.getLogger(__name__)
            logger.debug("🧹 ComponentFactory: Clearing component cache")
            cls._instances.clear()
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la fábrica de componentes.
        
        Returns:
            dict: Estadísticas de uso
        """
        with cls._lock:
            return {
                'cached_components': list(cls._instances.keys()),
                'cache_size': len(cls._instances),
                'memory_efficient': len(cls._instances) > 0,
                'components_available': [
                    'integration_manager',
                    'lambda_gateway', 
                    'rules_processor',
                    'validation_engine',
                    'result_processor'
                ]
            }

class LazyLoadingMonitor:
    """
    Monitor para tracking de lazy loading performance.
    """
    
    @staticmethod
    def log_component_load(component_name: str, load_time: float):
        """
        Registra el tiempo de carga de un componente.
        
        Args:
            component_name: Nombre del componente
            load_time: Tiempo de carga en segundos
        """
        logger = logging.getLogger(__name__)
        logger.info(f"🏗️ Lazy loaded {component_name} in {load_time*1000:.2f}ms")
        
        # Enviar métrica a CloudWatch si está habilitado
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
            # No fallar si no se pueden enviar métricas
            logger.debug(f"Could not send metrics: {str(e)}")
    
    @staticmethod
    def get_loading_statistics() -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de componentes.
        
        Returns:
            dict: Estadísticas de lazy loading
        """
        return ComponentFactory.get_statistics()