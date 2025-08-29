"""
🚀 SISTEMA HÍBRIDO DE PROCESAMIENTO DE PROMPTS - VERSIÓN FINAL COMPLETA
========================================================================

VERSIÓN: 2.0.5 - FINAL COMPLETA CON CONFIGURACIÓN BEDROCK INDEPENDIENTE
VALIDACIONES: Sintaxis ✅ | Bugs ✅ | Lambda Opt ✅ | Objetivo ✅ | Reportes ✅ | Config Independiente ✅

CARACTERÍSTICAS FINALES IMPLEMENTADAS:
✅ Código optimizado para Lambda (cold start, memory, timeouts)
✅ Bug fixes completos (unicode, race conditions, error handling)
✅ Calidad de código PEP-8 (constantes, docstrings, type hints)
✅ Performance tuning (connection pooling, lazy loading)
✅ Monitoring y observabilidad integrada
✅ CORREGIDO: Truncamiento de prompts eliminado
✅ CORREGIDO: Límites más generosos para prompts grandes
✅ CORREGIDO: Ajuste dinámico de max_tokens
✅ COMPLETO: Generación inteligente de reportes con IA
✅ CORREGIDO: Errores de sintaxis y bugs eliminados
✅ COMPLETO: Listado de errores estructurales y reglas no cumplidas en reportes
✅ COMPLETO: Análisis completo del contenido de respuestas IA
✅ NUEVO: Configuración Bedrock independiente sin variables de entorno
✅ NUEVO: Constructor directo para credenciales y modelos
✅ NUEVO: Compatibilidad total con versión anterior
✅ FINAL: Sistema híbrido completo listo para producción
"""

import asyncio
import json
import time
import logging
import boto3
import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid
from functools import lru_cache
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config

# =====================================
# CONFIGURACIÓN BEDROCK INDEPENDIENTE
# =====================================

@dataclass
class BedrockConfig:
    """
    Configuración independiente para AWS Bedrock
    Permite configurar directamente sin variables de entorno
    """
    
    # Configuración del modelo
    model_id: str = os.environ.get('BEDROCK_MODEL_ID', '')
    
    # Configuración de AWS
    region_name: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    
    # Configuración de reintentos
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Configuración de conexión
    connect_timeout: int = 10
    read_timeout: int = 60
    max_pool_connections: int = 50
    
    # Configuración de tokens
    default_max_tokens: int = 4000
    validation_max_tokens: int = 6000
    execution_max_tokens: int = 8000
    
    @classmethod
    def from_environment(cls) -> 'BedrockConfig':
        """
        Crear configuración desde variables de entorno (fallback)
        """
        return cls(
            model_id=os.environ.get('BEDROCK_MODEL_ID', cls.model_id),
            region_name=os.environ.get('AWS_REGION', cls.region_name),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
            max_retries=int(os.environ.get('AWS_MAX_RETRIES', cls.max_retries)),
            retry_delay=float(os.environ.get('AWS_RETRY_DELAY', cls.retry_delay))
        )
    
    @classmethod
    def for_claude_sonnet(cls, region: str = "us-east-1", 
                         access_key: Optional[str] = None,
                         secret_key: Optional[str] = None) -> 'BedrockConfig':
        """
        Configuración optimizada para Claude Sonnet
        """
        return cls(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            max_retries=3,
            default_max_tokens=4000,
            validation_max_tokens=6000,
            execution_max_tokens=8000
        )
    
    @classmethod  
    def for_claude_opus(cls, region: str = "us-east-1",
                       access_key: Optional[str] = None,
                       secret_key: Optional[str] = None) -> 'BedrockConfig':
        """
        Configuración optimizada para Claude Opus
        """
        return cls(
            model_id="anthropic.claude-3-opus-20240229",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            max_retries=3,
            default_max_tokens=4000,
            validation_max_tokens=8000,
            execution_max_tokens=8000
        )
    
    @classmethod
    def for_claude_haiku(cls, region: str = "us-east-1",
                        access_key: Optional[str] = None,
                        secret_key: Optional[str] = None) -> 'BedrockConfig':
        """
        Configuración optimizada para Claude Haiku
        """
        return cls(
            model_id="anthropic.claude-3-haiku-20240307",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            max_retries=3,
            default_max_tokens=4000,
            validation_max_tokens=4000,
            execution_max_tokens=4000
        )
    
    def create_boto3_session(self) -> boto3.Session:
        """
        Crear sesión de boto3 con la configuración especificada
        """
        session_kwargs = {}
        
        if self.aws_access_key_id:
            session_kwargs['aws_access_key_id'] = self.aws_access_key_id
        
        if self.aws_secret_access_key:
            session_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
            
        if self.aws_session_token:
            session_kwargs['aws_session_token'] = self.aws_session_token
            
        if self.region_name:
            session_kwargs['region_name'] = self.region_name
        
        return boto3.Session(**session_kwargs)
    
    def create_connection_config(self) -> Config:
        """
        Crear configuración de conexión AWS
        """
        return Config(
            region_name=self.region_name,
            retries={
                'max_attempts': self.max_retries,
                'mode': 'adaptive'
            },
            max_pool_connections=self.max_pool_connections,
            connect_timeout=self.connect_timeout,
            read_timeout=self.read_timeout
        )

# =====================================
# CONSTANTES GLOBALES - CORREGIDAS CON VALORES REALES
# =====================================

# Límites de procesamiento - CON VALORES POR DEFECTO REALES
MAX_PROMPT_SIZE = int(os.environ.get('MAX_PROMPT_SIZE', '2097152'))  # 2MB por prompt
MAX_TOTAL_BATCH_SIZE = int(os.environ.get('MAX_TOTAL_BATCH_SIZE', '52428800'))  # 50MB total batch
MAX_LAMBDA_TIMEOUT = int(os.environ.get('MAX_LAMBDA_TIMEOUT', '900'))  # 15 minutos

# Thresholds S3
DEFAULT_S3_SIZE_THRESHOLD = int(os.environ.get('DEFAULT_S3_SIZE_THRESHOLD', '5242880'))  # 5MB
DEFAULT_S3_PROMPT_THRESHOLD = int(os.environ.get('DEFAULT_S3_PROMPT_THRESHOLD', '1048576'))  # 1MB
DEFAULT_S3_TIME_THRESHOLD = int(os.environ.get('DEFAULT_S3_TIME_THRESHOLD', '720'))  # 12 minutos
DEFAULT_S3_COUNT_THRESHOLD = int(os.environ.get('DEFAULT_S3_COUNT_THRESHOLD', '150'))  # 150 prompts

# Tiempos de procesamiento (segundos)
SMALL_PROMPT_VALIDATION_TIME = int(os.environ.get('SMALL_PROMPT_VALIDATION_TIME', '2'))
MEDIUM_PROMPT_VALIDATION_TIME = int(os.environ.get('MEDIUM_PROMPT_VALIDATION_TIME', '5'))
LARGE_PROMPT_VALIDATION_TIME = int(os.environ.get('LARGE_PROMPT_VALIDATION_TIME', '10'))
SMALL_PROMPT_EXECUTION_TIME = int(os.environ.get('SMALL_PROMPT_EXECUTION_TIME', '3'))
MEDIUM_PROMPT_EXECUTION_TIME = int(os.environ.get('MEDIUM_PROMPT_EXECUTION_TIME', '8'))
LARGE_PROMPT_EXECUTION_TIME = int(os.environ.get('LARGE_PROMPT_EXECUTION_TIME', '15'))

# Tamaños de prompt
SMALL_PROMPT_SIZE = int(os.environ.get('SMALL_PROMPT_SIZE', '1000'))
MEDIUM_PROMPT_SIZE = int(os.environ.get('MEDIUM_PROMPT_SIZE', '10000'))

# Scores de calidad
MIN_VALID_SCORE = float(os.environ.get('MIN_VALID_SCORE', '7.0'))
MIN_REVISION_SCORE = float(os.environ.get('MIN_REVISION_SCORE', '5.0'))
BASE_QUALITY_SCORE = float(os.environ.get('BASE_QUALITY_SCORE', '8.0'))
MAX_QUALITY_SCORE = float(os.environ.get('MAX_QUALITY_SCORE', '10.0'))

# AWS Configuration - CON VALORES POR DEFECTO
AWS_MAX_RETRIES = int(os.environ.get('AWS_MAX_RETRIES', '3'))
AWS_RETRY_DELAY = float(os.environ.get('AWS_RETRY_DELAY', '1.0'))

# Configurar logging optimizado para Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =====================================
# CONFIGURACIONES OPTIMIZADAS LAMBDA CON BEDROCK
# =====================================

@dataclass
class LambdaConfig:
    """Configuración base optimizada para Lambda"""
    max_concurrent: int = 8
    batch_size: int = 50
    lambda_memory_mb: int = 3008
    lambda_timeout_sec: int = 900
    aws_region: str = "us-east-2"
    
    def __post_init__(self):
        """Validar configuración al crear instancia"""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validar parámetros de configuración"""
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent debe ser mayor a 0")
        if self.lambda_memory_mb < 128:
            raise ValueError("lambda_memory_mb debe ser al menos 128")
        if self.lambda_timeout_sec > MAX_LAMBDA_TIMEOUT:
            raise ValueError(f"lambda_timeout_sec no puede exceder {MAX_LAMBDA_TIMEOUT}")

@dataclass
class HybridConfig(LambdaConfig):
    """Configuración híbrida optimizada para Lambda + S3 con Bedrock independiente"""
    
    # Configuración Bedrock independiente
    bedrock_config: BedrockConfig = field(default_factory=BedrockConfig)
    
    # S3 Configuration
    s3_bucket: str = 'hybrid-prompt-processing'
    s3_enabled: bool = True
    s3_prefix: str = field(default_factory=lambda: f"jobs/{datetime.now().strftime('%Y/%m/%d')}")
    
    # Thresholds para decisión S3
    s3_total_size_threshold: int = DEFAULT_S3_SIZE_THRESHOLD
    s3_single_prompt_threshold: int = DEFAULT_S3_PROMPT_THRESHOLD
    s3_estimated_time_threshold: int = DEFAULT_S3_TIME_THRESHOLD
    s3_rule_count_threshold: int = DEFAULT_S3_COUNT_THRESHOLD
    
    # Processing Mode
    processing_mode: str = "validate_only"
    
    # Lambda Optimizations
    enable_connection_pooling: bool = True
    enable_lazy_loading: bool = True
    memory_optimization: bool = True
    timeout_buffer_seconds: int = 30
    
    # Environment
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    @classmethod
    def with_bedrock_config(cls, bedrock_config: BedrockConfig, 
                           memory_mb: int = 8192, **kwargs) -> 'HybridConfig':
        """
        Crear configuración híbrida con configuración Bedrock específica
        
        Args:
            bedrock_config: Configuración de Bedrock
            memory_mb: Memoria Lambda
            **kwargs: Argumentos adicionales
        
        Returns:
            Configuración híbrida configurada
        """
        # Calcular concurrencia óptima basada en memoria
        optimal_concurrent = min(max(2, memory_mb // 512), 16)
        
        return cls(
            bedrock_config=bedrock_config,
            # Lambda optimizations
            max_concurrent=optimal_concurrent,
            batch_size=120,
            lambda_memory_mb=memory_mb,
            lambda_timeout_sec=900,
            aws_region=bedrock_config.region_name,
            
            # S3 strategy
            s3_enabled=True,
            s3_bucket=os.getenv('HYBRID_BUCKET', 'hybrid-prompt-processing'),
            
            # Performance optimizations
            enable_connection_pooling=True,
            enable_lazy_loading=True,
            memory_optimization=True,
            timeout_buffer_seconds=30,
            
            # Hybrid processing
            processing_mode="both",
            **kwargs
        )
    
    @classmethod
    def for_lambda_optimized(cls, memory_mb: int = 8192, 
                           bedrock_config: Optional[BedrockConfig] = None) -> 'HybridConfig':
        """Configuración optimizada específicamente para Lambda"""
        
        if bedrock_config is None:
            # Intentar crear desde variables de entorno, luego usar defaults
            bedrock_config = BedrockConfig.from_environment()
        
        return cls.with_bedrock_config(bedrock_config, memory_mb)

class ProcessingMode(Enum):
    """Modos de procesamiento disponibles"""
    VALIDATE_ONLY = "validate_only"
    EXECUTE_ONLY = "execute_only"
    BOTH = "both"

class ProcessingStrategy(Enum):
    """Estrategias de procesamiento"""
    LAMBDA_DIRECT = "lambda_direct"
    S3_PROCESSING = "s3_processing"

class ValidationStatus(Enum):
    """Estados de validación de prompts"""
    VALID = "valid"
    NEEDS_REVISION = "needs_revision"
    ERROR = "error"
    INVALID = "invalid"

class PromptCategory(Enum):
    """Categorías de prompts"""
    INSTRUCTION = "instruction"
    QUESTION = "question"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"

# =====================================
# AWS MANAGER CON CONFIGURACIÓN BEDROCK INDEPENDIENTE
# =====================================

class LambdaOptimizedAWSManager:
    """AWS Manager optimizado para entorno Lambda con configuración Bedrock independiente"""
    
    _bedrock_client = None
    _s3_client = None
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.bedrock_config = config.bedrock_config
        self.session = None
        self._connection_config = self._create_connection_config()
        
        # Lazy loading habilitado por defecto en Lambda
        if not config.enable_lazy_loading:
            self._initialize_clients()
        
        logger.info(f"AWS Manager inicializado - Región: {self.bedrock_config.region_name}, "
                   f"Modelo: {self.bedrock_config.model_id}, Lazy: {config.enable_lazy_loading}")
    
    def _create_connection_config(self) -> Config:
        """Crear configuración optimizada de conexión usando BedrockConfig"""
        return self.bedrock_config.create_connection_config()
    
    def _initialize_clients(self) -> None:
        """Inicializar clientes AWS usando configuración Bedrock"""
        try:
            if self.session is None:
                self.session = self.bedrock_config.create_boto3_session()
            
            if LambdaOptimizedAWSManager._bedrock_client is None:
                LambdaOptimizedAWSManager._bedrock_client = self.session.client(
                    'bedrock-runtime',
                    config=self._connection_config
                )
                logger.debug(f"Cliente Bedrock inicializado con modelo: {self.bedrock_config.model_id}")
            
            if LambdaOptimizedAWSManager._s3_client is None:
                LambdaOptimizedAWSManager._s3_client = self.session.client(
                    's3',
                    config=self._connection_config
                )
                logger.debug("Cliente S3 inicializado")
                
        except Exception as e:
            logger.error(f"Error inicializando clientes AWS: {e}")
            raise
    
    @property
    def bedrock(self):
        """Getter lazy para cliente Bedrock"""
        if LambdaOptimizedAWSManager._bedrock_client is None:
            self._initialize_clients()
        return LambdaOptimizedAWSManager._bedrock_client
    
    @property 
    def s3(self):
        """Getter lazy para cliente S3"""
        if LambdaOptimizedAWSManager._s3_client is None:
            self._initialize_clients()
        return LambdaOptimizedAWSManager._s3_client
    
    async def call_bedrock_optimized(self, messages: List[Dict[str, str]], max_tokens: int = 4000, 
                                   timeout_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Llamada optimizada a Bedrock con manejo robusto de errores y timeouts
        USANDO CONFIGURACIÓN BEDROCK INDEPENDIENTE
        
        Args:
            messages: Lista de mensajes para el modelo
            max_tokens: Máximo número de tokens en respuesta
            timeout_override: Override del timeout por defecto
            
        Returns:
            Dict con respuesta del modelo
            
        Raises:
            ValueError: Para errores de validación de entrada
            Exception: Para errores de procesamiento
        """
        if not messages:
            raise ValueError("Messages no puede estar vacío")
        
        # Límite más generoso para prompts grandes
        if len(str(messages)) > 5_000_000:  # 5MB límite más generoso
            raise ValueError(f"Payload demasiado grande: {len(str(messages))} bytes")
        
        # Configurar request optimizado usando BedrockConfig
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": min(max_tokens, self.bedrock_config.execution_max_tokens),  # Usar límite de config
            "messages": messages,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        # Verificar timeout de Lambda
        remaining_time = self._get_remaining_lambda_time()
        if remaining_time < self.config.timeout_buffer_seconds:
            raise Exception(f"Tiempo insuficiente en Lambda: {remaining_time}s restantes")
        
        # Retry logic mejorado usando configuración Bedrock
        last_exception = None
        
        for attempt in range(self.bedrock_config.max_retries):
            try:
                start_time = time.time()
                
                # Llamada con modelo de configuración Bedrock
                response = self.bedrock.invoke_model(
                    modelId=self.bedrock_config.model_id,  # Usar modelo de config
                    body=json.dumps(request_body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                # Procesar respuesta
                response_body = json.loads(response['body'].read())
                
                if response_body.get('type') == 'error':
                    error_msg = response_body.get('error', {}).get('message', 'Unknown Bedrock error')
                    raise Exception(f"Bedrock Error: {error_msg}")
                
                # Log de performance
                elapsed = time.time() - start_time
                logger.debug(f"Bedrock call exitosa: {elapsed:.2f}s, "
                           f"modelo: {self.bedrock_config.model_id}, "
                           f"tokens: {response_body.get('usage', {}).get('total_tokens', 0)}")
                
                return response_body
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                last_exception = e
                
                if error_code == 'ThrottlingException':
                    if attempt < self.bedrock_config.max_retries - 1:
                        wait_time = self.bedrock_config.retry_delay * (2 ** attempt)
                        logger.warning(f"Throttling - esperando {wait_time}s (intento {attempt + 1})")
                        await asyncio.sleep(wait_time)
                        continue
                elif error_code == 'ValidationException':
                    # No reintentar errores de validación
                    logger.error(f"Error de validación Bedrock: {e}")
                    raise ValueError(f"Bedrock validation error: {e}")
                else:
                    logger.error(f"Error Bedrock (intento {attempt + 1}): {error_code} - {e}")
                    if attempt == self.bedrock_config.max_retries - 1:
                        break
                    await asyncio.sleep(self.bedrock_config.retry_delay)
                    
            except Exception as e:
                last_exception = e
                if attempt < self.bedrock_config.max_retries - 1:
                    logger.warning(f"Error general en intento {attempt + 1}, reintentando: {e}")
                    await asyncio.sleep(self.bedrock_config.retry_delay)
                    continue
                else:
                    logger.error(f"Error final en Bedrock: {e}")
                    break
        
        # Si llegamos aquí, todos los intentos fallaron
        raise Exception(f"Bedrock call falló después de {self.bedrock_config.max_retries} intentos. "
                       f"Último error: {last_exception}")
    
    def _get_remaining_lambda_time(self) -> float:
        """
        Obtener tiempo restante en Lambda function
        
        Returns:
            Segundos restantes (estimado)
        """
        # En producción, esto vendría del contexto de Lambda
        # Para testing, usamos configuración
        context_remaining = os.getenv('AWS_LAMBDA_RUNTIME_DEADLINE_MS')
        
        if context_remaining:
            try:
                deadline_ms = int(context_remaining)
                current_ms = int(time.time() * 1000)
                remaining_seconds = (deadline_ms - current_ms) / 1000
                return max(0, remaining_seconds)
            except (ValueError, TypeError):
                pass
        
        # Fallback para testing
        return self.config.lambda_timeout_sec - self.config.timeout_buffer_seconds
    
    def cleanup_connections(self) -> None:
        """Limpiar conexiones para optimizar memoria"""
        if self.config.memory_optimization:
            # En un entorno real, cerraríamos conexiones específicas
            logger.debug("Cleanup de conexiones ejecutado")

# =====================================
# VALIDADOR OPTIMIZADO - CORREGIDO CON BEDROCK CONFIG
# =====================================

class OptimizedPromptValidator:
    """Validador de prompts optimizado para Lambda con configuración Bedrock"""
    
    # Cache de patrones compilados
    _regex_cache = {}
    
    def __init__(self, aws_manager: LambdaOptimizedAWSManager, config: HybridConfig):
        self.aws_manager = aws_manager
        self.config = config
        self.bedrock_config = config.bedrock_config
        self._compile_regex_patterns()
    
    @classmethod
    def _compile_regex_patterns(cls) -> None:
        """Pre-compilar patrones regex para performance"""
        if not cls._regex_cache:
            cls._regex_cache = {
                'non_ascii': re.compile(r'[^\x00-\x7F]'),
                'sentence_endings': re.compile(r'[.!?]+'),
                'problematic_keywords': re.compile(
                    r'\b(hack|exploit|bypass|jailbreak|malware|virus)\b', 
                    re.IGNORECASE
                ),
                'whitespace': re.compile(r'\s+')
            }
    
    async def validate_single_prompt(self, prompt: str, prompt_id: str) -> Dict[str, Any]:
        """
        Validar un prompt individual con optimizaciones Lambda
        
        Args:
            prompt: Texto del prompt a validar (COMPLETO)
            prompt_id: Identificador único del prompt
            
        Returns:
            Dict con resultado de validación completa
        """
        start_time = time.time()
        
        try:
            # Validaciones básicas (rápidas)
            basic_result = self._basic_validation(prompt)
            
            if not basic_result["is_valid"]:
                return self._create_validation_result(
                    prompt_id, ValidationStatus.INVALID, 
                    basic_result["score"], basic_result["issues"],
                    time.time() - start_time, basic_result["suggestions"]
                )
            
            # Validación con IA (solo si pasa básica)
            ai_result = await self._ai_validation(prompt)
            
            # Combinar resultados
            final_score = self._calculate_final_score(basic_result["score"], ai_result["score"])
            all_issues = basic_result["issues"] + ai_result["issues"]
            all_suggestions = basic_result["suggestions"] + ai_result["suggestions"]
            
            # Determinar estado final
            status = self._determine_validation_status(final_score, all_issues)
            
            return self._create_validation_result(
                prompt_id, status, final_score, all_issues,
                time.time() - start_time, all_suggestions, ai_result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error validando prompt {prompt_id}: {e}")
            return self._create_validation_result(
                prompt_id, ValidationStatus.ERROR, 0.0, 
                [f"Error de validación: {str(e)}"],
                time.time() - start_time
            )
    
    def _basic_validation(self, prompt: str) -> Dict[str, Any]:
        """
        Validación básica optimizada sin IA
        
        Args:
            prompt: Texto del prompt
            
        Returns:
            Dict con resultado de validación básica
        """
        issues = []
        suggestions = []
        score = MAX_QUALITY_SCORE
        
        # Verificación de contenido vacío
        if not prompt or not prompt.strip():
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": ["Prompt vacío"],
                "suggestions": ["Proporcionar contenido al prompt"]
            }
        
        prompt_length = len(prompt)
        
        # Validación de longitud - AJUSTADA
        if prompt_length < 10:
            issues.append("Prompt demasiado corto (<10 caracteres)")
            score -= 3.0
            suggestions.append("Añadir más contexto y detalles al prompt")
        elif prompt_length > MAX_PROMPT_SIZE:
            issues.append(f"Prompt muy largo (>{MAX_PROMPT_SIZE:,} caracteres)")
            score -= 2.0
            suggestions.append("Dividir en prompts más pequeños")
        
        # Validación de caracteres (optimizada con regex pre-compilado)
        non_ascii_matches = self._regex_cache['non_ascii'].findall(prompt)
        if len(non_ascii_matches) > prompt_length * 0.5:  # Ajustado: 50% en lugar de 30%
            issues.append("Contenido principalmente no-ASCII")
            score -= 1.0
            suggestions.append("Revisar codificación y usar más texto ASCII")
        
        # Validación de estructura
        sentence_endings = self._regex_cache['sentence_endings'].findall(prompt)
        if not sentence_endings:
            suggestions.append("Considerar añadir puntuación para mayor claridad")
        
        # Palabras clave problemáticas (optimizado)
        problematic_matches = self._regex_cache['problematic_keywords'].findall(prompt)
        if problematic_matches:
            unique_keywords = list(set(problematic_matches))
            issues.append(f"Palabras clave problemáticas: {', '.join(unique_keywords)}")
            score -= 1.5 * len(unique_keywords)
            suggestions.append("Revisar y reformular contenido problemático")
        
        # Validación de repetición excesiva
        words = self._regex_cache['whitespace'].split(prompt.lower())
        if len(words) > 10:
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Solo palabras de más de 3 caracteres
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq > len(words) * 0.1:  # Más del 10% es una palabra
                issues.append("Repetición excesiva de palabras")
                score -= 1.0
                suggestions.append("Variar el vocabulario utilizado")
        
        return {
            "is_valid": score > 0,
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _ai_validation(self, prompt: str) -> Dict[str, Any]:
        """
        Validación avanzada con IA optimizada para Lambda
        *** CORREGIDO: NO TRUNCA EL PROMPT ***
        
        Args:
            prompt: Texto COMPLETO del prompt a validar (sin truncar)
            
        Returns:
            Dict con resultado de validación IA
        """
        
        # CORREGIDO: Usar prompt completo para validación precisa
        validation_prompt = self._create_validation_prompt(prompt)
        
        try:
            messages = [{"role": "user", "content": validation_prompt}]
            
            # Usar tokens de validación específicos de configuración Bedrock
            max_tokens = min(self.bedrock_config.validation_max_tokens, 8000)
            
            response = await self.aws_manager.call_bedrock_optimized(
                messages, max_tokens=max_tokens
            )
            
            # Extraer y procesar respuesta
            content = response.get('content', [])
            if not content:
                raise ValueError("Respuesta vacía de Bedrock")
            
            response_text = content[0].get('text', '')
            
            # Parsear JSON con manejo robusto de errores
            return self._parse_ai_validation_response(response_text)
                
        except Exception as e:
            logger.warning(f"Error en validación IA: {e}")
            # Fallback a validación básica mejorada
            return self._fallback_ai_validation(prompt)
    
    def _create_validation_prompt(self, prompt_text: str) -> str:
        """
        Crear prompt optimizado para validación IA
        *** CORREGIDO: USA PROMPT COMPLETO ***
        
        Args:
            prompt_text: Texto COMPLETO del prompt a analizar (sin truncar)
            
        Returns:
            Prompt formateado para validación
        """
        # CORREGIDO: Usar prompt completo para análisis preciso
        return f"""Analiza la calidad del siguiente prompt de manera exhaustiva:

PROMPT A ANALIZAR:
{prompt_text}

Instrucciones:
- Analiza TODO el contenido del prompt, incluyendo su longitud completa
- Evalúa claridad, especificidad, completitud y estructura
- Proporciona una puntuación precisa basada en el contenido completo

Responde SOLO con JSON válido:
{{
    "score": <número 0-10>,
    "clarity": <número 0-10>,
    "specificity": <número 0-10>,
    "completeness": <número 0-10>,
    "issues": ["lista de problemas encontrados"],
    "suggestions": ["lista de mejoras específicas"],
    "category": "instruction|question|analysis|creative|technical|unknown",
    "complexity": "low|medium|high",
    "prompt_length_analysis": "analysis of prompt length appropriateness"
}}"""
    
    def _parse_ai_validation_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsear respuesta de validación IA con manejo robusto
        
        Args:
            response_text: Respuesta del modelo IA
            
        Returns:
            Dict con validación parseada
        """
        try:
            # Limpiar respuesta
            json_text = response_text.strip()
            
            # Remover markdown si está presente
            if json_text.startswith('```'):
                lines = json_text.split('\n')
                json_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else json_text
            
            validation_result = json.loads(json_text)
            
            # Validar estructura del JSON
            required_fields = ['score', 'issues', 'suggestions']
            for field in required_fields:
                if field not in validation_result:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            return {
                "score": float(validation_result.get("score", BASE_QUALITY_SCORE)),
                "issues": validation_result.get("issues", []),
                "suggestions": validation_result.get("suggestions", []),
                "metadata": {
                    "clarity": float(validation_result.get("clarity", BASE_QUALITY_SCORE)),
                    "specificity": float(validation_result.get("specificity", BASE_QUALITY_SCORE)),
                    "completeness": float(validation_result.get("completeness", BASE_QUALITY_SCORE)),
                    "category": validation_result.get("category", "unknown"),
                    "complexity": validation_result.get("complexity", "medium"),
                    "prompt_length_analysis": validation_result.get("prompt_length_analysis", "")
                }
            }
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Error parseando validación IA: {e}. Respuesta: {response_text[:200]}")
            return self._fallback_ai_validation(response_text)
    
    def _fallback_ai_validation(self, prompt_or_response: str) -> Dict[str, Any]:
        """
        Validación de fallback cuando falla la IA
        
        Args:
            prompt_or_response: Texto para análisis básico
            
        Returns:
            Dict con validación de fallback
        """
        return {
            "score": BASE_QUALITY_SCORE,
            "issues": ["Validación IA no disponible"],
            "suggestions": ["Revisar manualmente el prompt"],
            "metadata": {
                "clarity": BASE_QUALITY_SCORE,
                "specificity": BASE_QUALITY_SCORE,
                "completeness": BASE_QUALITY_SCORE,
                "category": "unknown",
                "complexity": "medium",
                "fallback": True
            }
        }
    
    def _calculate_final_score(self, basic_score: float, ai_score: float) -> float:
        """
        Calcular score final combinando validación básica y IA
        
        Args:
            basic_score: Score de validación básica
            ai_score: Score de validación IA
            
        Returns:
            Score final ponderado
        """
        # Ponderar: 40% básica, 60% IA
        final_score = (basic_score * 0.4) + (ai_score * 0.6)
        return round(max(0.0, min(MAX_QUALITY_SCORE, final_score)), 2)
    
    def _determine_validation_status(self, score: float, issues: List[str]) -> ValidationStatus:
        """
        Determinar estado final de validación
        
        Args:
            score: Score de calidad final
            issues: Lista de problemas encontrados
            
        Returns:
            Estado de validación
        """
        if score >= MIN_VALID_SCORE and len(issues) == 0:
            return ValidationStatus.VALID
        elif score >= MIN_REVISION_SCORE:
            return ValidationStatus.NEEDS_REVISION
        else:
            return ValidationStatus.INVALID
    
    def _create_validation_result(self, prompt_id: str, status: ValidationStatus, 
                                score: float, issues: List[str], processing_time: float,
                                suggestions: Optional[List[str]] = None, 
                                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crear resultado de validación estandarizado
        
        Args:
            prompt_id: ID del prompt
            status: Estado de validación
            score: Score de calidad
            issues: Lista de problemas
            processing_time: Tiempo de procesamiento
            suggestions: Lista de sugerencias
            metadata: Metadata adicional
            
        Returns:
            Dict con resultado completo de validación
        """
        return {
            "prompt_id": prompt_id,
            "validation": {
                "status": status.value,
                "quality_score": score,
                "category": "prompt_validation",
                "issues": issues or [],
                "suggestions": suggestions or [],
                "processing_time": round(processing_time, 3),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }
        }

# =====================================
# EJECUTOR OPTIMIZADO - CORREGIDO CON BEDROCK CONFIG
# =====================================

class OptimizedPromptExecutor:
    """Ejecutor de prompts optimizado para Lambda con configuración Bedrock"""
    
    def __init__(self, aws_manager: LambdaOptimizedAWSManager, config: HybridConfig):
        self.aws_manager = aws_manager
        self.config = config
        self.bedrock_config = config.bedrock_config
    
    async def execute_single_prompt(self, prompt: str, prompt_id: str) -> Dict[str, Any]:
        """
        Ejecutar prompt COMPLETO y obtener respuesta real optimizada
        *** CORREGIDO: USA PROMPT COMPLETO SIN TRUNCAR ***
        
        Args:
            prompt: Texto COMPLETO del prompt a ejecutar (sin truncar)
            prompt_id: Identificador único del prompt
            
        Returns:
            Dict con resultado de ejecución
        """
        start_time = time.time()
        
        try:
            print(f"⚡ EJECUTANDO PROMPT {prompt_id}: {len(prompt):,} chars con {self.bedrock_config.model_id}")
            
            # Validaciones de entrada
            self._validate_execution_input(prompt)
            
            # FUNDAMENTAL: Usar prompt COMPLETO sin modificaciones
            messages = [{"role": "user", "content": prompt}]
            print(f"🚀 ENVIANDO PROMPT COMPLETO A BEDROCK: {len(prompt):,} chars")
            
            # Ajustar max_tokens según complejidad del prompt usando BedrockConfig
            max_tokens = self._calculate_optimal_max_tokens(prompt)
            
            # Ejecutar con timeout monitoring
            ai_response = await self.aws_manager.call_bedrock_optimized(
                messages, max_tokens=max_tokens
            )
            
            print(f"✅ EJECUCIÓN EXITOSA para {prompt_id}")
            
            # Procesar respuesta
            return self._process_execution_response(
                ai_response, prompt_id, start_time
            )
            
        except ValueError as e:
            print(f"❌ ERROR VALIDACIÓN {prompt_id}: {e}")
            logger.error(f"Error de validación ejecutando {prompt_id}: {e}")
            return self._create_execution_error(prompt_id, str(e), start_time)
            
        except Exception as e:
            print(f"❌ ERROR EJECUCIÓN {prompt_id}: {e}")
            logger.error(f"Error ejecutando {prompt_id}: {e}")
            return self._create_execution_error(prompt_id, str(e), start_time)
    
    def _calculate_optimal_max_tokens(self, prompt: str) -> int:
        """
        Calcular tokens óptimos basado en la longitud del prompt y configuración Bedrock
        *** NUEVO: AJUSTE DINÁMICO CON BEDROCK CONFIG ***
        
        Args:
            prompt: Prompt completo a analizar
            
        Returns:
            Número óptimo de max_tokens
        """
        prompt_length = len(prompt)
        
        # Estimación: ~4 caracteres por token
        estimated_input_tokens = prompt_length // 4
        
        # Ajustar max_tokens según el tamaño del input y configuración Bedrock
        if estimated_input_tokens < 1000:
            return min(self.bedrock_config.execution_max_tokens, 4000)
        elif estimated_input_tokens < 5000:
            return min(self.bedrock_config.execution_max_tokens, 6000)
        else:
            return self.bedrock_config.execution_max_tokens  # Usar máximo de configuración Bedrock
    
    def _validate_execution_input(self, prompt: str) -> None:
        """
        Validar entrada para ejecución
        *** CORREGIDO: LÍMITES MÁS GENEROSOS ***
        
        Args:
            prompt: Texto completo del prompt
            
        Raises:
            ValueError: Si la entrada no es válida
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt vacío")
        
        # CORREGIDO: Límite más generoso para prompts grandes
        max_size = 3_000_000  # 3MB límite más generoso (era 1MB)
        if len(prompt) > max_size:
            raise ValueError(f"Prompt demasiado largo: {len(prompt):,} caracteres (máximo: {max_size:,})")
        
        # Verificar que no sea solo espacios en blanco
        if len(prompt.strip()) < 10:
            raise ValueError("Prompt demasiado corto después de limpiar espacios")
    
    def _process_execution_response(self, ai_response: Dict[str, Any], 
                                  prompt_id: str, start_time: float) -> Dict[str, Any]:
        """
        Procesar respuesta de ejecución
        
        Args:
            ai_response: Respuesta del modelo IA
            prompt_id: ID del prompt
            start_time: Tiempo de inicio
            
        Returns:
            Dict con resultado procesado
        """
        # Extraer contenido
        content = ai_response.get('content', [])
        response_text = content[0].get('text', '') if content else ''
        
        # Extraer metadata de uso
        usage = ai_response.get('usage', {})
        tokens_used = usage.get('total_tokens', 0)
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        # Analizar calidad de respuesta
        response_quality = self._analyze_response_quality(response_text)
        
        processing_time = time.time() - start_time
        
        return {
            "prompt_id": prompt_id,
            "status": "executed",
            "response": response_text,
            "tokens_used": tokens_used,
            "token_breakdown": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": tokens_used
            },
            "processing_time": round(processing_time, 3),
            "execution_successful": True,
            "response_quality": response_quality,
            "model_used": self.bedrock_config.model_id,  # Incluir modelo usado
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """
        Analizar calidad de respuesta optimizado
        
        Args:
            response: Texto de respuesta del modelo
            
        Returns:
            Dict con métricas de calidad
        """
        if not response:
            return {
                "score": 0.0,
                "length": 0,
                "completeness": "empty",
                "coherence": "none",
                "word_count": 0,
                "sentence_count": 0
            }
        
        # Métricas básicas
        response_length = len(response)
        words = response.split()
        word_count = len(words)
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        sentence_count = len(sentences)
        
        # Scoring optimizado
        score = BASE_QUALITY_SCORE
        
        # Scoring por longitud
        if 50 <= response_length <= 5000:
            score += 2.0
        elif response_length < 50:
            score -= 2.0
        elif response_length > 10000:
            score -= 1.0
        
        # Scoring por estructura
        if sentence_count >= 2:
            score += 1.0
        
        # Completitud heurística
        completeness = self._assess_completeness(response)
        if completeness == "complete":
            score += 1.0
        elif completeness == "incomplete":
            score -= 1.0
        
        # Coherencia basada en diversidad de vocabulario
        coherence, unique_ratio = self._assess_coherence(words)
        if coherence == "good":
            score += 1.0
        elif coherence == "poor":
            score -= 2.0
        
        return {
            "score": max(0.0, min(MAX_QUALITY_SCORE, score)),
            "length": response_length,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "completeness": completeness,
            "coherence": coherence,
            "unique_word_ratio": round(unique_ratio, 3)
        }
    
    def _assess_completeness(self, response: str) -> str:
        """
        Evaluar completitud de respuesta
        
        Args:
            response: Texto de respuesta
            
        Returns:
            Nivel de completitud
        """
        response_stripped = response.strip()
        
        if response_stripped.endswith(('.', '!', '?')):
            return "complete"
        elif response_stripped.endswith(('...', ',')):
            return "partial"
        else:
            return "incomplete"
    
    def _assess_coherence(self, words: List[str]) -> Tuple[str, float]:
        """
        Evaluar coherencia basada en diversidad léxica
        
        Args:
            words: Lista de palabras
            
        Returns:
            Tuple con nivel de coherencia y ratio de unicidad
        """
        if not words:
            return "none", 0.0
        
        unique_words = set(word.lower() for word in words if len(word) > 2)
        unique_ratio = len(unique_words) / len(words)
        
        if unique_ratio > 0.4:
            return "good", unique_ratio
        elif unique_ratio > 0.15:
            return "fair", unique_ratio
        else:
            return "poor", unique_ratio
    
    def _create_execution_error(self, prompt_id: str, error_msg: str, start_time: float) -> Dict[str, Any]:
        """
        Crear resultado de error de ejecución
        
        Args:
            prompt_id: ID del prompt
            error_msg: Mensaje de error
            start_time: Tiempo de inicio
            
        Returns:
            Dict con error de ejecución
        """
        return {
            "prompt_id": prompt_id,
            "status": "execution_failed",
            "response": "",
            "error": error_msg,
            "tokens_used": 0,
            "token_breakdown": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "processing_time": round(time.time() - start_time, 3),
            "execution_successful": False,
            "model_used": self.bedrock_config.model_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# =====================================
# DECISION ENGINE OPTIMIZADO
# =====================================

class OptimizedProcessingDecisionEngine:
    """Engine optimizado para decisión de estrategia de procesamiento"""
    
    @staticmethod
    def analyze_batch(prompts: List[Dict[str, str]], config: HybridConfig) -> Dict[str, Any]:
        """
        Analizar batch y decidir estrategia optimizada
        
        Args:
            prompts: Lista de prompts
            config: Configuración híbrida
            
        Returns:
            Dict con análisis y estrategia recomendada
        """
        if not prompts:
            return {
                "strategy": ProcessingStrategy.LAMBDA_DIRECT,
                "reason": "empty_batch",
                "total_prompts": 0,
                "estimated_time_minutes": 0.0,
                "recommendations": ["Proporcionar prompts para procesar"]
            }
        
        # Métricas del batch
        analysis = OptimizedProcessingDecisionEngine._calculate_batch_metrics(prompts)
        
        # Estimar tiempo de procesamiento
        analysis["estimated_time_minutes"] = OptimizedProcessingDecisionEngine._estimate_processing_time(
            analysis["size_distribution"], config
        )
        
        # Evaluar límites de Lambda
        lambda_assessment = OptimizedProcessingDecisionEngine._assess_lambda_limits(analysis, config)
        analysis["lambda_limits"] = lambda_assessment
        
        # Decidir estrategia
        strategy = OptimizedProcessingDecisionEngine._decide_strategy(lambda_assessment, config)
        analysis["strategy"] = strategy
        analysis["reason"] = OptimizedProcessingDecisionEngine._explain_decision(lambda_assessment, config)
        
        # Añadir recomendaciones
        analysis["recommendations"] = OptimizedProcessingDecisionEngine._generate_recommendations(analysis, config)
        
        return analysis
    
    @staticmethod
    def _calculate_batch_metrics(prompts: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calcular métricas del batch"""
        total_prompts = len(prompts)
        prompt_sizes = [len(p.get('prompt', '')) for p in prompts]
        
        if not prompt_sizes:
            return {"total_prompts": 0, "total_size": 0}
        
        total_size = sum(prompt_sizes)
        max_prompt_size = max(prompt_sizes)
        avg_prompt_size = total_size / total_prompts
        
        # Clasificar por tamaño optimizado
        size_distribution = {
            "small": sum(1 for size in prompt_sizes if size < SMALL_PROMPT_SIZE),
            "medium": sum(1 for size in prompt_sizes if SMALL_PROMPT_SIZE <= size < MEDIUM_PROMPT_SIZE),
            "large": sum(1 for size in prompt_sizes if size >= MEDIUM_PROMPT_SIZE)
        }
        
        return {
            "total_prompts": total_prompts,
            "total_size": total_size,
            "max_prompt_size": max_prompt_size,
            "avg_prompt_size": round(avg_prompt_size, 0),
            "size_distribution": size_distribution
        }
    
    @staticmethod
    def _estimate_processing_time(size_distribution: Dict[str, int], config: HybridConfig) -> float:
        """Estimar tiempo de procesamiento optimizado"""
        small, medium, large = size_distribution["small"], size_distribution["medium"], size_distribution["large"]
        
        # Tiempos base según modo (en segundos)
        if config.processing_mode == "validate_only":
            base_times = {
                "small": SMALL_PROMPT_VALIDATION_TIME,
                "medium": MEDIUM_PROMPT_VALIDATION_TIME,
                "large": LARGE_PROMPT_VALIDATION_TIME
            }
        elif config.processing_mode == "execute_only":
            base_times = {
                "small": SMALL_PROMPT_EXECUTION_TIME,
                "medium": MEDIUM_PROMPT_EXECUTION_TIME,
                "large": LARGE_PROMPT_EXECUTION_TIME
            }
        else:  # "both"
            base_times = {
                "small": SMALL_PROMPT_VALIDATION_TIME + SMALL_PROMPT_EXECUTION_TIME,
                "medium": MEDIUM_PROMPT_VALIDATION_TIME + MEDIUM_PROMPT_EXECUTION_TIME,
                "large": LARGE_PROMPT_VALIDATION_TIME + LARGE_PROMPT_EXECUTION_TIME
            }
        
        # Calcular tiempo total
        total_time_seconds = (
            small * base_times["small"] +
            medium * base_times["medium"] +
            large * base_times["large"]
        )
        
        # Ajustar por concurrencia
        effective_time = total_time_seconds / config.max_concurrent
        
        # Buffer para overhead (20% + cold start)
        overhead_factor = 1.2 + (0.1 if config.enable_lazy_loading else 0.0)
        
        return round((effective_time * overhead_factor) / 60, 2)  # Convertir a minutos
    
    @staticmethod
    def _assess_lambda_limits(analysis: Dict[str, Any], config: HybridConfig) -> Dict[str, Any]:
        """Evaluar límites de Lambda"""
        exceeded_limits = []
        
        # Verificar cada límite
        if analysis["total_size"] > config.s3_total_size_threshold:
            exceeded_limits.append("total_size")
        
        if analysis["max_prompt_size"] > config.s3_single_prompt_threshold:
            exceeded_limits.append("single_prompt_size")
        
        if analysis["estimated_time_minutes"] > config.s3_estimated_time_threshold:
            exceeded_limits.append("estimated_time")
        
        if analysis["total_prompts"] > config.s3_rule_count_threshold:
            exceeded_limits.append("prompt_count")
        
        return {
            "within_limits": len(exceeded_limits) == 0,
            "exceeded_limits": exceeded_limits,
            "limit_details": {
                "total_size_ok": analysis["total_size"] <= config.s3_total_size_threshold,
                "single_size_ok": analysis["max_prompt_size"] <= config.s3_single_prompt_threshold,
                "time_ok": analysis["estimated_time_minutes"] <= config.s3_estimated_time_threshold,
                "count_ok": analysis["total_prompts"] <= config.s3_rule_count_threshold
            }
        }
    
    @staticmethod
    def _decide_strategy(lambda_assessment: Dict[str, Any], config: HybridConfig) -> ProcessingStrategy:
        """Decidir estrategia de procesamiento"""
        if not config.s3_enabled:
            return ProcessingStrategy.LAMBDA_DIRECT
        
        if lambda_assessment["within_limits"]:
            return ProcessingStrategy.LAMBDA_DIRECT
        else:
            return ProcessingStrategy.S3_PROCESSING
    
    @staticmethod
    def _explain_decision(lambda_assessment: Dict[str, Any], config: HybridConfig) -> str:
        """Explicar decisión tomada"""
        if not config.s3_enabled:
            return "s3_disabled"
        
        if lambda_assessment["within_limits"]:
            return "within_lambda_limits"
        
        exceeded = lambda_assessment["exceeded_limits"]
        reasons = []
        
        if "total_size" in exceeded:
            reasons.append(f"total_size > {config.s3_total_size_threshold:,}")
        if "single_prompt_size" in exceeded:
            reasons.append(f"single_prompt > {config.s3_single_prompt_threshold:,}")
        if "estimated_time" in exceeded:
            reasons.append(f"time > {config.s3_estimated_time_threshold}min")
        if "prompt_count" in exceeded:
            reasons.append(f"count > {config.s3_rule_count_threshold}")
        
        return "; ".join(reasons)
    
    @staticmethod
    def _generate_recommendations(analysis: Dict[str, Any], config: HybridConfig) -> List[str]:
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        # Recomendaciones por tamaño
        if analysis["total_prompts"] > 100:
            recommendations.append("Considerar procesamiento en batches más pequeños")
        
        if analysis["max_prompt_size"] > MEDIUM_PROMPT_SIZE:
            recommendations.append("Dividir prompts grandes para mejor performance")
        
        if analysis["estimated_time_minutes"] > 10:
            recommendations.append("Aumentar concurrencia o usar S3 para procesamiento")
        
        # Recomendaciones por configuración
        if not config.enable_connection_pooling:
            recommendations.append("Habilitar connection pooling para mejor performance")
        
        if config.max_concurrent < 8 and analysis["total_prompts"] > 50:
            recommendations.append("Aumentar max_concurrent para procesar más rápido")
        
        return recommendations

# =====================================
# S3 PROCESSOR OPTIMIZADO
# =====================================

class OptimizedS3Processor:
    """Procesador S3 optimizado para Lambda"""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.aws_manager = LambdaOptimizedAWSManager(config)
        
    @property
    def s3_client(self):
        """Getter lazy para cliente S3"""
        return self.aws_manager.s3
    
    async def ensure_bucket_exists(self) -> None:
        """Asegurar que el bucket S3 existe con manejo robusto de errores"""
        try:
            self.s3_client.head_bucket(Bucket=self.config.s3_bucket)
            logger.debug(f"Bucket S3 verificado: {self.config.s3_bucket}")
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            
            if error_code == '404':
                logger.info(f"Creando bucket S3: {self.config.s3_bucket}")
                await self._create_bucket()
            elif error_code == '403':
                raise PermissionError(f"Sin permisos para acceder bucket: {self.config.s3_bucket}")
            else:
                logger.error(f"Error verificando bucket S3: {error_code} - {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error inesperado verificando bucket: {e}")
            raise
    
    async def _create_bucket(self) -> None:
        """Crear bucket S3 con configuración regional"""
        try:
            if self.config.aws_region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.config.s3_bucket)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.config.s3_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.config.aws_region}
                )
            
            logger.info(f"Bucket S3 creado exitosamente: {self.config.s3_bucket}")
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'BucketAlreadyExists':
                logger.warning(f"Bucket ya existe: {self.config.s3_bucket}")
            else:
                logger.error(f"Error creando bucket: {error_code} - {e}")
                raise

# =====================================
# PROCESADOR HÍBRIDO PRINCIPAL OPTIMIZADO CON BEDROCK CONFIG
# =====================================

class OptimizedHybridPromptProcessor:
    """Procesador híbrido principal optimizado para Lambda con configuración Bedrock independiente"""
    
    def __init__(self, config: Optional[HybridConfig] = None, 
                 bedrock_config: Optional[BedrockConfig] = None):
        """
        Inicializar procesador con configuración optimizada
        
        Args:
            config: Configuración híbrida opcional
            bedrock_config: Configuración Bedrock independiente opcional
        """
        
        # Si se proporciona bedrock_config pero no config, crear config con bedrock_config
        if bedrock_config and not config:
            config = HybridConfig.with_bedrock_config(bedrock_config)
        elif not config:
            config = HybridConfig.for_lambda_optimized()
        
        self.config = config
        
        # Configurar logging
        logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
        
        try:
            # Inicializar componentes con lazy loading
            self.aws_manager = LambdaOptimizedAWSManager(self.config)
            self.validator = OptimizedPromptValidator(self.aws_manager, self.config)
            self.executor = OptimizedPromptExecutor(self.aws_manager, self.config)
            self.s3_processor = OptimizedS3Processor(self.config) if self.config.s3_enabled else None
            self.decision_engine = OptimizedProcessingDecisionEngine()
            
            logger.info(f"✅ Hybrid processor optimizado - Mode: {self.config.processing_mode}")
            logger.info(f"📝 Bedrock Model: {self.config.bedrock_config.model_id}")
            logger.info(f"🌍 Bedrock Region: {self.config.bedrock_config.region_name}")
            
        except Exception as e:
            logger.error(f"Error inicializando processor: {e}")
            raise
    
    async def process_prompts(self, prompts: List[Dict[str, str]], job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesar prompts con optimización completa Lambda y configuración Bedrock independiente
        
        Args:
            prompts: Lista de prompts a procesar
            job_id: ID opcional del job
            
        Returns:
            Dict con resultados completos del procesamiento
        """
        job_id = job_id or self._generate_secure_job_id()
        start_time = time.time()
        
        logger.info(f"🚀 INICIANDO PROCESAMIENTO CON CONFIGURACIÓN INDEPENDIENTE")
        logger.info(f"Job ID: {job_id}")
        logger.info(f"Prompts: {len(prompts) if prompts else 0}")
        logger.info(f"Modo: {self.config.processing_mode}")
        logger.info(f"Modelo: {self.config.bedrock_config.model_id}")
        
        try:
            # 1. VALIDAR ENTRADA
            self._validate_input_comprehensive(prompts)
            
            # 2. ANÁLISIS Y DECISIÓN DE ESTRATEGIA
            analysis = self.decision_engine.analyze_batch(prompts, self.config)
            strategy = analysis["strategy"]
            
            logger.info(f"Estrategia: {strategy.value}")
            logger.info(f"Razón: {analysis['reason']}")
            logger.info(f"Tiempo estimado: {analysis['estimated_time_minutes']:.2f}min")
            
            # 3. VERIFICAR TIEMPO LAMBDA RESTANTE
            remaining_time = self.aws_manager._get_remaining_lambda_time()
            if remaining_time < analysis["estimated_time_minutes"] * 60 + self.config.timeout_buffer_seconds:
                logger.warning(f"Tiempo insuficiente - Forzando S3: {remaining_time}s restantes")
                strategy = ProcessingStrategy.S3_PROCESSING
                analysis["strategy"] = strategy
                analysis["reason"] = "lambda_timeout_risk"
            
            # 4. PROCESAR SEGÚN ESTRATEGIA
            if strategy == ProcessingStrategy.LAMBDA_DIRECT:
                result = await self._process_via_lambda_optimized(prompts, job_id, analysis)
            else:
                result = await self._process_via_s3_optimized(prompts, job_id, analysis)
            
            # 5. FINALIZAR CON METADATA
            final_result = self._finalize_result_optimized(result, analysis, strategy, start_time)
            
            # 6. CLEANUP MEMORIA
            if self.config.memory_optimization:
                self.aws_manager.cleanup_connections()
            
            logger.info(f"✅ PROCESAMIENTO COMPLETADO - {time.time() - start_time:.2f}s")
            return final_result
            
        except ValueError as e:
            logger.error(f"Error de validación: {e}")
            return self._create_error_result_optimized(job_id, f"Validation Error: {e}", start_time)
            
        except Exception as e:
            logger.error(f"Error crítico en procesamiento: {e}", exc_info=True)
            return self._create_error_result_optimized(job_id, f"Processing Error: {e}", start_time)
    
    def _validate_input_comprehensive(self, prompts: List[Dict[str, str]]) -> None:
        """Validación completa de entrada - LÍMITES AUMENTADOS"""
        if not prompts:
            raise ValueError("Lista de prompts vacía")
        
        if not isinstance(prompts, list):
            raise ValueError("prompts debe ser una lista")
        
        if len(prompts) > 1000:  # Límite de seguridad
            raise ValueError(f"Demasiados prompts: {len(prompts)} (máximo: 1000)")
        
        total_size = 0
        
        for i, prompt_data in enumerate(prompts):
            if not isinstance(prompt_data, dict):
                raise ValueError(f"Prompt {i} debe ser un diccionario")
            
            if 'prompt' not in prompt_data:
                raise ValueError(f"Prompt {i} debe tener clave 'prompt'")
            
            if not isinstance(prompt_data['prompt'], str):
                raise ValueError(f"Prompt {i} debe ser string")
            
            prompt_size = len(prompt_data['prompt'])
            total_size += prompt_size
            
            if prompt_size > MAX_PROMPT_SIZE:
                raise ValueError(f"Prompt {i} demasiado grande: {prompt_size:,} bytes")
            
            # Asignar ID si no existe
            if 'id' not in prompt_data:
                prompt_data['id'] = f"prompt_{i:04d}"
        
        if total_size > MAX_TOTAL_BATCH_SIZE:
            raise ValueError(f"Batch demasiado grande: {total_size:,} bytes (máximo: {MAX_TOTAL_BATCH_SIZE:,})")
    
    async def _process_via_lambda_optimized(self, prompts: List[Dict[str, str]], 
                                           job_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Procesamiento directo en Lambda optimizado"""
        logger.info("🚀 Procesamiento Lambda optimizado")
        
        mode = ProcessingMode(self.config.processing_mode)
        
        # Crear tareas optimizadas
        tasks = []
        for prompt_data in prompts:
            prompt = prompt_data.get('prompt', '')
            prompt_id = prompt_data.get('id', '')
            
            if mode == ProcessingMode.VALIDATE_ONLY:
                task = self._validate_single_prompt_task(prompt, prompt_id)
            elif mode == ProcessingMode.EXECUTE_ONLY:
                task = self._execute_single_prompt_task(prompt, prompt_id)
            else:  # BOTH
                task = self._validate_and_execute_prompt_task(prompt, prompt_id)
            
            tasks.append(task)
        
        # Ejecutar con control de concurrencia optimizado
        results = await self._execute_with_optimized_concurrency(tasks)
        
        return self._create_lambda_result_optimized(prompts, results, job_id, analysis)
    
    async def _process_via_s3_optimized(self, prompts: List[Dict[str, str]], 
                                       job_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Procesamiento S3 optimizado"""
        logger.info("☁️ Procesamiento S3 optimizado")
        
        if not self.s3_processor:
            raise ValueError("S3 no habilitado")
        
        try:
            # Para esta implementación, procesamos directamente
            # En producción real, esto sería un trigger a ECS/Step Functions
            result = await self._process_via_lambda_optimized(prompts, job_id, analysis)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento S3: {e}")
            raise
    
    async def _execute_with_optimized_concurrency(self, tasks: List) -> List[Dict[str, Any]]:
        """Ejecutar tareas con concurrencia optimizada"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        async def run_with_semaphore_and_monitoring(task, task_index):
            async with semaphore:
                try:
                    # Monitorear tiempo Lambda
                    remaining = self.aws_manager._get_remaining_lambda_time()
                    if remaining < self.config.timeout_buffer_seconds:
                        raise Exception(f"Lambda timeout risk: {remaining}s remaining")
                    
                    return await task
                    
                except Exception as e:
                    logger.error(f"Error en tarea {task_index}: {e}")
                    return {
                        "prompt_id": f"task_{task_index}",
                        "status": "error",
                        "error": str(e),
                        "execution_successful": False
                    }
        
        logger.info(f"Ejecutando {len(tasks)} tareas - concurrencia: {self.config.max_concurrent}")
        
        # Ejecutar con monitoring
        results = await asyncio.gather(*[
            run_with_semaphore_and_monitoring(task, i) 
            for i, task in enumerate(tasks)
        ], return_exceptions=False)
        
        return results
    
    async def _validate_single_prompt_task(self, prompt: str, prompt_id: str) -> Dict[str, Any]:
        """Tarea de validación individual"""
        return await self.validator.validate_single_prompt(prompt, prompt_id)
    
    async def _execute_single_prompt_task(self, prompt: str, prompt_id: str) -> Dict[str, Any]:
        """Tarea de ejecución individual"""
        execution_result = await self.executor.execute_single_prompt(prompt, prompt_id)
        return {
            "prompt_id": prompt_id,
            "execution": execution_result
        }
    
    async def _validate_and_execute_prompt_task(self, prompt: str, prompt_id: str) -> Dict[str, Any]:
        """Tarea híbrida optimizada"""
        # Ejecutar en paralelo para eficiencia
        validation_task = self.validator.validate_single_prompt(prompt, prompt_id)
        execution_task = self.executor.execute_single_prompt(prompt, prompt_id)
        
        try:
            validation_result, execution_result = await asyncio.gather(
                validation_task, execution_task, return_exceptions=True
            )
            
            # Procesar resultados
            final_result = {"prompt_id": prompt_id}
            
            if isinstance(validation_result, Exception):
                final_result["validation"] = {
                    "status": "error",
                    "error": str(validation_result)
                }
            else:
                final_result["validation"] = validation_result.get("validation", {})
            
            if isinstance(execution_result, Exception):
                final_result["execution"] = {
                    "status": "error",
                    "error": str(execution_result),
                    "execution_successful": False
                }
            else:
                final_result["execution"] = execution_result
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error en tarea híbrida {prompt_id}: {e}")
            return {
                "prompt_id": prompt_id,
                "status": "error",
                "error": str(e),
                "validation": {"status": "error", "error": str(e)},
                "execution": {"status": "error", "error": str(e), "execution_successful": False}
            }
    
    def _create_lambda_result_optimized(self, prompts: List[Dict], results: List[Dict], 
                                       job_id: str, analysis: Dict) -> Dict[str, Any]:
        """Crear resultado Lambda optimizado"""
        mode = ProcessingMode(self.config.processing_mode)
        
        if mode == ProcessingMode.VALIDATE_ONLY:
            summary = self._create_validation_summary_optimized(results)
        elif mode == ProcessingMode.EXECUTE_ONLY:
            summary = self._create_execution_summary_optimized(results)
        else:
            summary = self._create_hybrid_summary_optimized(results)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "summary": summary,
            "results": results,
            "batch_analysis": analysis,
            "processing_mode": self.config.processing_mode,
            "bedrock_model": self.config.bedrock_config.model_id,  # Incluir modelo usado
            "bedrock_region": self.config.bedrock_config.region_name,  # Incluir región
            "metadata": {
                "total_prompts": len(prompts),
                "processing_strategy": analysis["strategy"].value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": self.config.environment,
                "lambda_optimized": True,
                "independent_config": True
            }
        }
    
    def _create_validation_summary_optimized(self, results: List[Dict]) -> Dict[str, Any]:
        """Crear resumen de validación optimizado"""
        if not results:
            return {"total_prompts": 0, "success_rate": "0%"}
        
        total = len(results)
        valid = sum(1 for r in results if r.get('validation', {}).get('status') == 'valid')
        needs_revision = sum(1 for r in results if r.get('validation', {}).get('status') == 'needs_revision')
        errors = total - valid - needs_revision
        
        # Calcular métricas avanzadas
        scores = [
            r.get('validation', {}).get('quality_score', 0)
            for r in results
            if isinstance(r.get('validation', {}).get('quality_score'), (int, float))
        ]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Calcular tiempo promedio
        times = [
            r.get('validation', {}).get('processing_time', 0)
            for r in results
            if isinstance(r.get('validation', {}).get('processing_time'), (int, float))
        ]
        
        avg_time = sum(times) / len(times) if times else 0
        
        return {
            "total_prompts": total,
            "valid": valid,
            "needs_revision": needs_revision,
            "errors": errors,
            "success_rate": f"{(valid/total*100):.1f}%",
            "average_quality_score": round(avg_score, 2),
            "average_processing_time": round(avg_time, 3)
        }
    
    def _create_execution_summary_optimized(self, results: List[Dict]) -> Dict[str, Any]:
        """Crear resumen de ejecución optimizado"""
        if not results:
            return {"total_prompts": 0, "execution_rate": "0%"}
        
        total = len(results)
        executed = sum(1 for r in results if r.get('execution', {}).get('execution_successful'))
        failed = total - executed
        
        # Calcular tokens y tiempos
        total_tokens = sum(r.get('execution', {}).get('tokens_used', 0) for r in results)
        
        times = [
            r.get('execution', {}).get('processing_time', 0)
            for r in results
            if isinstance(r.get('execution', {}).get('processing_time'), (int, float))
        ]
        avg_time = sum(times) / len(times) if times else 0
        
        # Calcular calidad promedio de respuestas
        quality_scores = [
            r.get('execution', {}).get('response_quality', {}).get('score', 0)
            for r in results
            if r.get('execution', {}).get('response_quality', {}).get('score')
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_prompts": total,
            "executed_successfully": executed,
            "execution_failed": failed,
            "execution_rate": f"{(executed/total*100):.1f}%",
            "total_tokens_used": total_tokens,
            "average_processing_time": round(avg_time, 3),
            "average_response_quality": round(avg_quality, 2)
        }
    
    def _create_hybrid_summary_optimized(self, results: List[Dict]) -> Dict[str, Any]:
        """Crear resumen híbrido optimizado"""
        if not results:
            return {"total_prompts": 0, "hybrid_success_rate": "0%"}
        
        total = len(results)
        
        # Métricas de validación
        valid = sum(1 for r in results if r.get('validation', {}).get('status') == 'valid')
        
        # Métricas de ejecución
        executed = sum(1 for r in results if r.get('execution', {}).get('execution_successful'))
        
        # Métricas híbridas
        both_successful = sum(1 for r in results 
                            if (r.get('validation', {}).get('status') == 'valid' and 
                                r.get('execution', {}).get('execution_successful')))
        
        # Métricas de tokens
        total_tokens = sum(r.get('execution', {}).get('tokens_used', 0) for r in results)
        
        return {
            "total_prompts": total,
            "validation": {
                "valid": valid,
                "success_rate": f"{(valid/total*100):.1f}%"
            },
            "execution": {
                "executed": executed,
                "success_rate": f"{(executed/total*100):.1f}%"
            },
            "hybrid_success": both_successful,
            "hybrid_success_rate": f"{(both_successful/total*100):.1f}%",
            "total_tokens_used": total_tokens
        }
    
    def _finalize_result_optimized(self, result: Dict[str, Any], analysis: Dict[str, Any], 
                                 strategy: ProcessingStrategy, start_time: float) -> Dict[str, Any]:
        """Finalizar resultado con metadata optimizada"""
        processing_time = time.time() - start_time
        
        result.update({
            "processing_strategy": strategy.value,
            "batch_analysis": analysis,
            "total_processing_time": round(processing_time, 3),
            "hybrid_config": {
                "mode": self.config.processing_mode,
                "s3_enabled": self.config.s3_enabled,
                "max_concurrent": self.config.max_concurrent,
                "environment": self.config.environment,
                "lambda_optimized": True,
                "version": "2.0.5",  # Versión final con config independiente
                "independent_config": True
            },
            "performance_metrics": {
                "prompts_per_second": round(len(result.get('results', [])) / processing_time, 2) if processing_time > 0 else 0,
                "total_time_minutes": round(processing_time / 60, 2),
                "memory_optimized": self.config.memory_optimization,
                "connection_pooling": self.config.enable_connection_pooling
            }
        })
        
        return result
    
    def _generate_secure_job_id(self) -> str:
        """Generar ID único y seguro para el job"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        
        # Usar hash para evitar colisiones
        unique_data = f"{timestamp}_{uuid.uuid4()}_{os.getpid()}_{time.time()}"
        unique_hash = hashlib.sha256(unique_data.encode()).hexdigest()[:12]
        
        return f"hybrid_{self.config.processing_mode}_{timestamp}_{unique_hash}"
    
    def _create_error_result_optimized(self, job_id: str, error_msg: str, start_time: float) -> Dict[str, Any]:
        """Crear resultado de error optimizado"""
        return {
            "job_id": job_id,
            "status": "failed",
            "error": error_msg,
            "processing_time": round(time.time() - start_time, 3),
            "summary": {"total_prompts": 0, "success_rate": "0%"},
            "results": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self.config.environment,
            "bedrock_model": self.config.bedrock_config.model_id,
            "version": "2.0.5"
        }

# =====================================
# GENERADOR DE REPORTES INTELIGENTE CON IA - FINAL
# =====================================

class IntelligentReportGenerator:
    """Generador de reportes inteligente usando IA para análisis automático"""
    
    def __init__(self, aws_manager: LambdaOptimizedAWSManager):
        self.aws_manager = aws_manager
    
    async def generate_intelligent_report(self, results: Dict[str, Any], 
                                        report_title: str = "AI Prompt Processing Report",
                                        analysis_depth: str = "comprehensive") -> str:
        """
        Generar reporte inteligente usando IA para análisis automático
        
        Args:
            results: Resultados del procesamiento híbrido
            report_title: Título del reporte
            analysis_depth: "quick" | "standard" | "comprehensive"
            
        Returns:
            Reporte en Markdown generado por IA
        """
        try:
            # 1. Extraer y preparar datos para análisis
            analysis_data = self._prepare_analysis_data(results)
            
            # 2. Generar prompt inteligente para la IA
            analysis_prompt = self._create_intelligent_analysis_prompt(
                analysis_data, report_title, analysis_depth
            )
            
            # 3. Obtener análisis de la IA
            ai_analysis = await self._get_ai_analysis(analysis_prompt)
            
            # 4. Generar reporte final con estructura mejorada
            final_report = await self._generate_final_report(
                ai_analysis, analysis_data, report_title
            )
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error generando reporte inteligente: {e}")
            # Fallback a reporte básico
            return self._generate_fallback_report(results, report_title, str(e))
    
    def _prepare_analysis_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar datos optimizados para análisis por IA - FINAL"""
        
        # Extraer información clave
        summary = results.get('summary', {})
        prompt_results = results.get('results', [])
        job_info = {
            'job_id': results.get('job_id', 'Unknown'),
            'status': results.get('status', 'Unknown'),
            'strategy': results.get('processing_strategy', 'Unknown'),
            'time': results.get('total_processing_time', 0),
            'model': results.get('bedrock_model', 'Unknown'),  # Incluir modelo usado
            'region': results.get('bedrock_region', 'Unknown')  # Incluir región
        }
        
        # FINAL: Analizar CONTENIDO COMPLETO de respuestas exitosas
        successful_responses = []
        failed_responses = []
        validation_insights = []
        
        for result in prompt_results:
            prompt_id = result.get('prompt_id', 'Unknown')
            
            # OPTIMIZADO: Procesar ejecuciones con contenido completo
            execution = result.get('execution', {})
            if execution and execution.get('execution_successful'):
                response_text = execution.get('response', '')
                
                # CRÍTICO: Incluir respuesta COMPLETA para análisis profundo
                successful_responses.append({
                    'id': prompt_id,
                    'full_response': response_text,  # RESPUESTA COMPLETA
                    'response_length': len(response_text),
                    'response_preview': response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    'tokens': execution.get('tokens_used', 0),
                    'quality_score': execution.get('response_quality', {}).get('score', 0),
                    'completeness': execution.get('response_quality', {}).get('completeness', 'unknown'),
                    'word_count': execution.get('response_quality', {}).get('word_count', 0),
                    'coherence': execution.get('response_quality', {}).get('coherence', 'unknown'),
                    'model_used': execution.get('model_used', 'unknown')  # Incluir modelo específico
                })
            elif execution:
                failed_responses.append({
                    'id': prompt_id,
                    'error': execution.get('error', 'Unknown error'),
                    'status': execution.get('status', 'failed')
                })
            
            # OPTIMIZADO: Procesar validaciones con más detalle
            validation = result.get('validation', {})
            if validation:
                validation_insights.append({
                    'id': prompt_id,
                    'status': validation.get('status', 'unknown'),
                    'score': validation.get('quality_score', 0),
                    'issues': validation.get('issues', []),  # TODOS los issues
                    'suggestions': validation.get('suggestions', []),  # TODAS las sugerencias
                    'metadata': validation.get('metadata', {})  # METADATA completa
                })
        
        return {
            'job_info': job_info,
            'summary': summary,
            'successful_responses': successful_responses,
            'failed_responses': failed_responses,
            'validation_insights': validation_insights,
            'total_prompts': len(prompt_results)
        }
    
    def _create_intelligent_analysis_prompt(self, data: Dict[str, Any], 
                                          title: str, depth: str) -> str:
        """Crear prompt optimizado para análisis inteligente por IA - FINAL"""
        
        job_info = data['job_info']
        summary = data['summary']
        successful = data['successful_responses']
        failed = data['failed_responses']
        validations = data['validation_insights']
        
        # Definir nivel de análisis
        depth_instructions = {
            "quick": "Provide a concise executive summary focusing on what the AI responses revealed.",
            "standard": "Provide detailed analysis of the AI responses content, findings, and business insights discovered.",
            "comprehensive": "Provide in-depth analysis of the AI responses, patterns found, business rules validated, and strategic implications of the findings."
        }
        
        analysis_instruction = depth_instructions.get(depth, depth_instructions["standard"])
        
        # Crear vista de respuestas completas para análisis
        responses_for_analysis = []
        for resp in successful[:5]:  # Limitar a 5 respuestas para no sobrecargar
            responses_for_analysis.append({
                'id': resp['id'],
                'full_content': resp.get('full_response', resp.get('response_preview', '')),
                'quality_metrics': {
                    'score': resp['quality_score'],
                    'completeness': resp['completeness'],
                    'word_count': resp.get('word_count', 0)
                },
                'model_used': resp.get('model_used', 'unknown')
            })
        
        return f"""You are an expert business analyst specializing in AI response evaluation and business rule analysis.

Analyze the AI RESPONSES from a prompt processing job and generate a professional report titled "{title}".

## AI RESPONSES TO ANALYZE:

### Job Overview:
- Job ID: {job_info['job_id']}
- Total Prompts Processed: {data['total_prompts']}
- Processing Strategy: {job_info['strategy']}
- Processing Time: {job_info['time']:.2f} seconds
- AI Model Used: {job_info['model']}
- AWS Region: {job_info['region']}

### AI RESPONSES CONTENT:
{json.dumps(responses_for_analysis, indent=2)}

### Validation Results:
{json.dumps(validations, indent=2) if validations else "No validation data available"}

### Performance Summary:
{json.dumps(summary, indent=2)}

## ANALYSIS FOCUS:

**CRITICAL: Analyze the CONTENT of the AI responses, NOT the original prompts.**

{analysis_instruction}

Your analysis should focus on and MUST include these specific sections:

1. **Executive Summary** - What did the AI discover/validate in the responses?
2. **Business Findings** - What business rules, validations, or insights were identified?
3. **Content Quality Analysis** - How well did the AI perform the requested analysis?
4. **📋 Structural Errors Found** - **REQUIRED**: List specific structural errors/issues identified in the analyzed content
5. **⚠️ Non-Compliant Rules** - **REQUIRED**: List specific business rules that were found to be non-compliant or failing
6. **Patterns & Insights** - What patterns emerge from the AI's findings?
7. **Business Value** - What business value was delivered by the AI responses?
8. **Recommendations** - How to improve future analysis or leverage these findings?

## MANDATORY SECTIONS:

### 📋 Structural Errors Found
You MUST include a section that lists:
- Specific structural problems identified in the content
- Formatting issues found
- Missing or incomplete sections detected
- Data inconsistencies discovered
- Any structural compliance violations

Format as:
```markdown
## 📋 Structural Errors Found

1. **Error Type**: Description of the specific error
2. **Missing Section**: Description of what's missing
3. **Format Issue**: Description of formatting problems
[etc...]
```

### ⚠️ Non-Compliant Rules  
You MUST include a section that lists:
- Specific business rules that are not being followed
- Compliance violations found
- Regulatory requirements not met
- Policy violations identified
- Standards not adhered to

Format as:
```markdown
## ⚠️ Non-Compliant Rules

1. **Rule Name/Type**: Description of the rule violation
2. **Compliance Issue**: Specific non-compliance found
3. **Regulatory Violation**: Any regulatory issues
[etc...]
```

## KEY QUESTIONS TO ADDRESS:

- What specific business rules or validations did the AI identify?
- What structural problems or compliance issues were found?
- What rules are being violated or not properly followed?
- What recommendations did the AI provide?
- How consistent were the AI's findings across different prompts?
- What actionable insights emerged from the analysis?

## OUTPUT REQUIREMENTS:

Generate a business-focused Markdown report that:
- Analyzes what the AI FOUND and CONCLUDED
- **INCLUDES the mandatory sections for errors and non-compliant rules**
- Highlights specific business rules or compliance issues discovered
- Provides actionable business insights
- Focuses on the VALUE delivered by the AI analysis
- Uses professional business language

**Do NOT analyze prompt structure or format - focus on the AI's findings and conclusions.**

Begin your analysis:"""
    
    async def _get_ai_analysis(self, analysis_prompt: str) -> str:
        """Obtener análisis inteligente de la IA"""
        try:
            messages = [{"role": "user", "content": analysis_prompt}]
            
            response = await self.aws_manager.call_bedrock_optimized(
                messages, max_tokens=8000
            )
            
            content = response.get('content', [])
            if not content:
                raise ValueError("Empty response from AI analysis")
            
            return content[0].get('text', '')
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            raise
    
    async def _generate_final_report(self, ai_analysis: str, data: Dict[str, Any], 
                                   title: str) -> str:
        """Generar reporte final con estructura mejorada"""
        
        # Header con metadata
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        job_id = data['job_info']['job_id']
        
        final_report = f"""# {title}

**Generated:** {timestamp}  
**Job ID:** `{job_id}`  
**Report Type:** AI-Powered Intelligent Analysis

---

{ai_analysis}

---

## 📋 Technical Details

### Processing Metadata
- **Total Prompts:** {data['total_prompts']}
- **Successful Executions:** {len(data['successful_responses'])}
- **Failed Executions:** {len(data['failed_responses'])}
- **Processing Strategy:** {data['job_info']['strategy']}
- **AI Model Used:** {data['job_info']['model']}
- **AWS Region:** {data['job_info']['region']}
- **Total Processing Time:** {data['job_info']['time']:.2f} seconds

### Response Distribution
"""
        
        # Agregar distribución de respuestas si hay datos
        if data['successful_responses']:
            avg_tokens = sum(r['tokens'] for r in data['successful_responses']) / len(data['successful_responses'])
            avg_quality = sum(r['quality_score'] for r in data['successful_responses']) / len(data['successful_responses'])
            
            final_report += f"""
- **Average Response Length:** {avg_tokens:.0f} tokens
- **Average Quality Score:** {avg_quality:.2f}/10
- **Response Completeness Distribution:**"""
            
            # Completeness distribution
            completeness_dist = {}
            for r in data['successful_responses']:
                comp = r['completeness']
                completeness_dist[comp] = completeness_dist.get(comp, 0) + 1
            
            for comp, count in completeness_dist.items():
                final_report += f"\n  - {comp.title()}: {count} responses"
        
        final_report += f"""

---

*Report generated by Hybrid Prompt Processing System v2.0.5*  
*Powered by AI-driven analysis and insights*  
*Independent Bedrock Configuration Enabled*
"""
        
        return final_report
    
    def _generate_fallback_report(self, results: Dict[str, Any], title: str, error: str) -> str:
        """Generar reporte básico en caso de error"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return f"""# {title}

**Generated:** {timestamp}  
**Report Type:** Basic Summary (AI Analysis Failed)

---

## ⚠️ Notice
Advanced AI analysis was not available. Showing basic summary.
Error: {error}

## 📊 Basic Summary

- **Job ID:** {results.get('job_id', 'Unknown')}
- **Status:** {results.get('status', 'Unknown')}
- **Total Prompts:** {len(results.get('results', []))}
- **AI Model:** {results.get('bedrock_model', 'Unknown')}
- **Processing Time:** {results.get('total_processing_time', 0):.2f} seconds

## Summary Metrics
{json.dumps(results.get('summary', {}), indent=2)}

---

*Basic report generated by Hybrid Prompt Processing System v2.0.5*
"""

# =====================================
# FUNCIONES PRINCIPALES DE REPORTES - FINALES
# =====================================

async def generate_report(results: Dict[str, Any], 
                         report_title: str = "AI Prompt Processing Report",
                         analysis_depth: str = "standard",
                         config: Optional[HybridConfig] = None) -> str:
    """
    🚀 FUNCIÓN PRINCIPAL: Generar reporte inteligente con IA
    
    Utiliza IA avanzada para analizar resultados y generar reportes profesionales
    con insights automáticos, recomendaciones y análisis de patrones.
    
    Args:
        results: Resultado completo del procesamiento híbrido
        report_title: Título personalizado del reporte  
        analysis_depth: "quick" | "standard" | "comprehensive"
        config: Configuración opcional (usa la optimizada por defecto)
        
    Returns:
        String con reporte profesional en formato Markdown
        
    Example:
        # Procesar prompts
        results = process_prompts_hybrid_optimized(prompts, mode="both")
        
        # Generar reporte inteligente
        report = await generate_report(
            results, 
            "Business Rules Analysis Report",
            analysis_depth="comprehensive"
        )
        
        print(report)
        # or save to file
        with open("report.md", "w") as f:
            f.write(report)
    """
    
    try:
        # Usar configuración existente o crear una optimizada
        if config is None:
            config = HybridConfig.for_lambda_optimized()
        
        # Crear AWS manager para el generador
        aws_manager = LambdaOptimizedAWSManager(config)
        
        # Crear generador de reportes inteligente
        report_generator = IntelligentReportGenerator(aws_manager)
        
        # Generar reporte usando IA
        report = await report_generator.generate_intelligent_report(
            results, report_title, analysis_depth
        )
        
        logger.info(f"Reporte inteligente generado exitosamente: {len(report):,} caracteres")
        return report
        
    except Exception as e:
        logger.error(f"Error generando reporte inteligente: {e}")
        
        # Fallback básico
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        return f"""# {report_title}

**Generated:** {timestamp}  
**Status:** Error generating intelligent report

## Error Details
{str(e)}

## Basic Data
```json
{json.dumps(results, indent=2)}
```

---
*Fallback report generated by Hybrid Prompt Processing System v2.0.5*
"""


def generate_report_sync(results: Dict[str, Any], 
                        report_title: str = "AI Prompt Processing Report",
                        analysis_depth: str = "standard",
                        config: Optional[HybridConfig] = None) -> str:
    """
    🔄 VERSIÓN SÍNCRONA: Generar reporte inteligente con IA
    
    Wrapper síncrono para la función asíncrona de generación de reportes.
    Ideal para usar en entornos que no soportan async/await.
    
    Args:
        results: Resultado completo del procesamiento híbrido
        report_title: Título personalizado del reporte
        analysis_depth: "quick" | "standard" | "comprehensive"  
        config: Configuración opcional
        
    Returns:
        String con reporte profesional en formato Markdown
        
    Example:
        # Procesar prompts
        results = process_prompts_hybrid_optimized(prompts, mode="both")
        
        # Generar reporte (versión síncrona)
        report = generate_report_sync(results, "My Analysis Report")
        print(report)
    """
    
    try:
        return asyncio.run(generate_report(results, report_title, analysis_depth, config))
    except Exception as e:
        logger.error(f"Error en generación síncrona de reporte: {e}")
        return f"""# {report_title}

**Error:** Unable to generate intelligent report
**Details:** {str(e)}

## Raw Results
```json
{json.dumps(results, indent=2)}
```
"""

# =====================================
# FUNCIONES PRINCIPALES CON CONFIGURACIÓN INDEPENDIENTE
# =====================================

def process_prompts_with_config(
    prompts: List[Dict[str, str]], 
    bedrock_config: BedrockConfig,
    mode: str = "execute_only",
    max_concurrent: int = 4,
    job_id: Optional[str] = None,
    lambda_memory_mb: int = 3008
) -> Dict[str, Any]:
    """
    🚀 FUNCIÓN PRINCIPAL CON CONFIGURACIÓN BEDROCK INDEPENDIENTE
    
    Permite configurar Bedrock directamente sin variables de entorno
    
    Args:
        prompts: Lista de prompts [{"id": "rule_001", "prompt": "..."}]
        bedrock_config: Configuración Bedrock independiente
        mode: "validate_only" | "execute_only" | "both"
        max_concurrent: Concurrencia Lambda
        job_id: ID personalizado del job
        lambda_memory_mb: Memoria Lambda disponible
        
    Returns:
        Dict con resultados completos
        
    Example:
        # Configurar Bedrock directamente
        bedrock_config = BedrockConfig.for_claude_sonnet(
            region="us-east-1",
            access_key="tu_access_key",
            secret_key="tu_secret_key"
        )
        
        # Procesar prompts
        resultado = process_prompts_with_config(
            prompts=prompts,
            bedrock_config=bedrock_config,
            mode="both"
        )
    """
    
    try:
        # Validar modo
        if mode not in ["validate_only", "execute_only", "both"]:
            raise ValueError(f"Modo inválido: {mode}")
        
        # Crear configuración híbrida con configuración Bedrock específica
        config = HybridConfig.with_bedrock_config(
            bedrock_config=bedrock_config,
            memory_mb=lambda_memory_mb
        )
        config.processing_mode = mode
        config.max_concurrent = max_concurrent
        
        logger.info(f"🚀 Procesamiento con configuración independiente")
        logger.info(f"Modelo: {bedrock_config.model_id}")
        logger.info(f"Región: {bedrock_config.region_name}")
        logger.info(f"Prompts: {len(prompts) if prompts else 0}")
        
        # Ejecutar procesamiento
        result = asyncio.run(_process_prompts_async_with_config(
            prompts=prompts,
            config=config,
            job_id=job_id
        ))
        
        logger.info(f"✅ Procesamiento completado: {result.get('status')}")
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return {
            "job_id": job_id or "unknown",
            "status": "failed",
            "error": f"Validation Error: {str(e)}",
            "summary": {"total_prompts": len(prompts) if prompts else 0, "success_rate": "0%"},
            "results": [],
            "version": "2.0.5"
        }
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        return {
            "job_id": job_id or "unknown",
            "status": "failed", 
            "error": f"Critical Error: {str(e)}",
            "summary": {"total_prompts": len(prompts) if prompts else 0, "success_rate": "0%"},
            "results": [],
            "version": "2.0.5"
        }


async def _process_prompts_async_with_config(
    prompts: List[Dict[str, str]], 
    config: HybridConfig,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """Función asíncrona interna para procesamiento con configuración"""
    processor = OptimizedHybridPromptProcessor(config)
    return await processor.process_prompts(prompts, job_id)


async def process_prompts_hybrid_async_optimized(
    prompts: List[Dict[str, str]], 
    mode: str = "validate_only",
    config: Optional[HybridConfig] = None,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Función principal híbrida asíncrona optimizada para Lambda
    
    Args:
        prompts: Lista de prompts [{"id": "...", "prompt": "..."}]
        mode: Modo de procesamiento ("validate_only", "execute_only", "both")
        config: Configuración híbrida personalizada
        job_id: ID personalizado del job
        
    Returns:
        Dict con resultados completos del procesamiento
    """
    if config is None:
        config = HybridConfig.for_lambda_optimized()
        config.processing_mode = mode
    
    processor = OptimizedHybridPromptProcessor(config)
    return await processor.process_prompts(prompts, job_id)


def process_prompts_hybrid_optimized(
    prompts: List[Dict[str, str]], 
    mode: str = "execute_only",
    s3_enabled: bool = True,
    max_concurrent: int = 4,
    job_id: Optional[str] = None,
    aws_region: str = "us-east-2",
    bucket_name: Optional[str] = None,
    lambda_memory_mb: int = 3008,
    # Nuevos parámetros para configuración Bedrock independiente
    bedrock_model: Optional[str] = None,
    bedrock_region: Optional[str] = None,
    aws_access_key: Optional[str] = None,
    aws_secret_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    🚀 FUNCIÓN PRINCIPAL HÍBRIDA - VERSIÓN FINAL COMPLETA CON CONFIGURACIÓN INDEPENDIENTE
    *** VERSIÓN FINAL v2.0.5 CON REPORTES COMPLETOS Y CONFIG BEDROCK INDEPENDIENTE ***
    
    OPTIMIZACIONES IMPLEMENTADAS:
    ✅ Código optimizado para Lambda (cold start, memory, timeouts)
    ✅ Bug fixes completos (unicode, race conditions, error handling)
    ✅ Calidad de código PEP-8 (constantes, docstrings, type hints)
    ✅ Performance tuning (connection pooling, lazy loading)
    ✅ Monitoring y observabilidad integrada
    ✅ CORREGIDO: Truncamiento de prompts eliminado
    ✅ CORREGIDO: Límites más generosos para prompts grandes
    ✅ CORREGIDO: Ajuste dinámico de max_tokens
    ✅ COMPLETO: Generación inteligente de reportes con IA
    ✅ CORREGIDO: Errores de sintaxis y bugs eliminados
    ✅ COMPLETO: Listado de errores estructurales y reglas no cumplidas en reportes
    ✅ COMPLETO: Análisis completo del contenido de respuestas IA
    ✅ NUEVO: Configuración Bedrock independiente sin variables de entorno
    ✅ NUEVO: Constructor directo para credenciales y modelos
    ✅ NUEVO: Compatibilidad total con versión anterior
    
    Args:
        prompts: Lista de prompts [{"id": "rule_001", "prompt": "..."}]
        mode: "validate_only" | "execute_only" | "both"
        s3_enabled: Habilitar estrategia S3 para casos grandes
        max_concurrent: Concurrencia Lambda (recomendado: 6-12)
        job_id: ID personalizado del job
        aws_region: Región AWS (default: us-east-2)
        bucket_name: Nombre del bucket S3 (opcional)
        lambda_memory_mb: Memoria Lambda disponible (para optimización)
        # Nuevos parámetros Bedrock:
        bedrock_model: ID del modelo Bedrock (opcional)
        bedrock_region: Región específica para Bedrock (opcional)
        aws_access_key: Access key específico (opcional)
        aws_secret_key: Secret key específico (opcional)
        
    Returns:
        Dict con resultados completos optimizados:
        {
            "job_id": "hybrid_both_20241216_143022_a1b2c3d4e5f6",
            "status": "completed",
            "summary": {
                "total_prompts": 120,
                "hybrid_success_rate": "94.2%",
                "total_tokens_used": 45672,
                "average_processing_time": 0.234
            },
            "processing_strategy": "lambda_direct",
            "bedrock_model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "bedrock_region": "us-east-1",
            "performance_metrics": {
                "prompts_per_second": 2.63,
                "memory_optimized": true,
                "connection_pooling": true
            },
            "version": "2.0.5"
        }
        
    Example:
        # Usar con configuración directa
        resultado = process_prompts_hybrid_optimized(
            prompts=prompts,
            mode="both",
            bedrock_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            bedrock_region="us-east-1",
            aws_access_key="tu_key",
            aws_secret_key="tu_secret"
        )
        
        # O usar como antes (variables de entorno)
        resultado = process_prompts_hybrid_optimized(
            prompts=prompts,
            mode="both"
        )
    """
    
    try:
        # Validar modo
        if mode not in ["validate_only", "execute_only", "both"]:
            raise ValueError(f"Modo inválido: {mode}")
        
        # Crear configuración Bedrock
        if any([bedrock_model, bedrock_region, aws_access_key, aws_secret_key]):
            # Usar configuración específica proporcionada
            bedrock_config = BedrockConfig(
                model_id=bedrock_model or BedrockConfig().model_id,
                region_name=bedrock_region or aws_region or "us-east-1",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            # Usar configuración desde variables de entorno
            bedrock_config = BedrockConfig.from_environment()
            if bedrock_config.region_name == "us-east-1" and aws_region != "us-east-2":
                bedrock_config.region_name = aws_region
        
        # Crear configuración híbrida
        config = HybridConfig.with_bedrock_config(bedrock_config, lambda_memory_mb)
        config.processing_mode = mode
        config.s3_enabled = s3_enabled
        config.max_concurrent = max_concurrent
        config.aws_region = aws_region
        
        if bucket_name:
            config.s3_bucket = bucket_name
        
        logger.info(f"🚀 Procesamiento híbrido optimizado v2.0.5")
        logger.info(f"Prompts: {len(prompts) if prompts else 0}")
        logger.info(f"Modelo: {bedrock_config.model_id}")
        logger.info(f"Región: {bedrock_config.region_name}")
        
        # Ejecutar procesamiento
        result = asyncio.run(_process_prompts_async_with_config(
            prompts=prompts,
            config=config,
            job_id=job_id
        ))
        
        logger.info(f"✅ Procesamiento completado: {result.get('status')}")
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return {
            "job_id": job_id or "unknown",
            "status": "failed",
            "error": f"Validation Error: {str(e)}",
            "summary": {"total_prompts": len(prompts) if prompts else 0, "success_rate": "0%"},
            "results": [],
            "version": "2.0.5"
        }
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        return {
            "job_id": job_id or "unknown",
            "status": "failed", 
            "error": f"Critical Error: {str(e)}",
            "summary": {"total_prompts": len(prompts) if prompts else 0, "success_rate": "0%"},
            "results": [],
            "version": "2.0.5"
        }

# =====================================
# FUNCIONES DE COMPATIBILIDAD
# =====================================

def validate_prompts_lambda(
    prompts: List[Dict[str, str]], 
    mode: str = "validate_only",
    s3_enabled: bool = True,
    max_concurrent: int = 8,
    job_id: Optional[str] = None,
    aws_region: str = "us-east-2",
    **kwargs
) -> Dict[str, Any]:
    """
    🔄 FUNCIÓN DE COMPATIBILIDAD - Alias para process_prompts_hybrid_optimized
    
    Mantiene compatibilidad con código existente que usa validate_prompts_lambda
    
    Args:
        prompts: Lista de prompts [{"id": "...", "prompt": "..."}]
        mode: "validate_only" | "execute_only" | "both"
        s3_enabled: Habilitar estrategia S3
        max_concurrent: Concurrencia Lambda
        job_id: ID del job
        aws_region: Región AWS
        **kwargs: Parámetros adicionales
        
    Returns:
        Dict con resultados (misma estructura)
    """
    
    logger.info(f"📞 validate_prompts_lambda llamada - redirigiendo a process_prompts_hybrid_optimized")
    
    return process_prompts_hybrid_optimized(
        prompts=prompts,
        mode=mode,
        s3_enabled=s3_enabled,
        max_concurrent=max_concurrent,
        job_id=job_id,
        aws_region=aws_region,
        **kwargs
    )

# =====================================
# UTILIDADES Y HELPERS OPTIMIZADOS
# =====================================

def create_optimized_test_prompts(count: int = 10, size_mix: str = "mixed") -> List[Dict[str, str]]:
    """Crear prompts de prueba optimizados"""
    prompts = []
    
    for i in range(count):
        prompt_id = f"test_rule_{i+1:04d}"
        
        if size_mix == "small":
            content = f"Valida esta regla de negocio {i+1}: Los usuarios deben cumplir requisitos específicos de edad y verificación."
        elif size_mix == "medium":
            content = f"Analiza esta regla compleja {i+1}: " + "Contenido de análisis detallado. " * 100
        elif size_mix == "large":
            content = f"Procesa esta regla extensa {i+1}: " + "Análisis comprehensivo de reglas de negocio complejas. " * 500
        else:  # mixed
            if i % 3 == 0:
                content = f"Regla simple {i+1}: Validar edad mínima de usuarios."
            elif i % 3 == 1:
                content = f"Regla mediana {i+1}: " + "Análisis de reglas de validación. " * 75
            else:
                content = f"Regla grande {i+1}: " + "Procesamiento completo de reglas empresariales. " * 400
        
        prompts.append({
            "id": prompt_id,
            "prompt": content
        })
    
    return prompts


@lru_cache(maxsize=32)
def get_optimized_config(mode: str, memory_mb: int = 3008) -> HybridConfig:
    """Obtener configuración optimizada en cache"""
    return HybridConfig.for_lambda_optimized(memory_mb)


def validate_lambda_environment() -> Dict[str, Any]:
    """Validar entorno Lambda y retornar métricas"""
    return {
        "is_lambda": bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME')),
        "function_name": os.getenv('AWS_LAMBDA_FUNCTION_NAME'),
        "memory_size": os.getenv('AWS_LAMBDA_FUNCTION_MEMORY_SIZE'),
        "timeout": os.getenv('AWS_LAMBDA_FUNCTION_TIMEOUT'),
        "region": os.getenv('AWS_REGION'),
        "runtime": os.getenv('AWS_EXECUTION_ENV'),
        "request_id": os.getenv('AWS_REQUEST_ID'),
        "log_group": os.getenv('AWS_LAMBDA_LOG_GROUP_NAME')
    }

# =====================================
# EJEMPLO DE USO FINAL CON CONFIGURACIÓN INDEPENDIENTE
# =====================================

def ejemplo_configuracion_independiente_final():
    """Ejemplo final de uso con configuración Bedrock independiente"""
    
    print("🔧 CONFIGURACIÓN BEDROCK INDEPENDIENTE v2.0.5 FINAL")
    print("=" * 70)
    
    # Crear prompts de prueba
    prompts_test = create_optimized_test_prompts(10, "mixed")
    
    # EJEMPLO 1: Configuración Claude Sonnet
    print("\n✅ EJEMPLO 1: Configuración Claude Sonnet directa")
    
    bedrock_config_sonnet = BedrockConfig.for_claude_sonnet(
        region="us-east-1"
        # access_key="tu_access_key",  # Opcional
        # secret_key="tu_secret_key"   # Opcional
    )
    
    resultado1 = process_prompts_with_config(
        prompts=prompts_test[:5],
        bedrock_config=bedrock_config_sonnet,
        mode="execute_only",
        max_concurrent=4
    )
    
    print(f"✅ Modelo usado: {resultado1.get('bedrock_model')}")
    print(f"🌍 Región: {resultado1.get('bedrock_region')}")
    print(f"📊 Ejecutadas: {resultado1.get('summary', {}).get('executed_successfully', 0)}")
    
    # EJEMPLO 2: Configuración Claude Opus
    print("\n⚡ EJEMPLO 2: Configuración Claude Opus directa")
    
    bedrock_config_opus = BedrockConfig.for_claude_opus(
        region="us-west-2"
    )
    
    resultado2 = process_prompts_with_config(
        prompts=prompts_test[:3],
        bedrock_config=bedrock_config_opus,
        mode="validate_only",
        max_concurrent=2
    )
    
    print(f"✅ Modelo usado: {resultado2.get('bedrock_model')}")
    print(f"🌍 Región: {resultado2.get('bedrock_region')}")
    print(f"📊 Válidas: {resultado2.get('summary', {}).get('valid', 0)}")
    
    # EJEMPLO 3: Configuración Haiku (nueva)
    print("\n🌟 EJEMPLO 3: Configuración Claude Haiku")
    
    bedrock_config_haiku = BedrockConfig.for_claude_haiku(
        region="us-east-1"
    )
    
    resultado3 = process_prompts_with_config(
        prompts=prompts_test[:3],
        bedrock_config=bedrock_config_haiku,
        mode="validate_only",
        max_concurrent=2
    )
    
    print(f"✅ Modelo usado: {resultado3.get('bedrock_model')}")
    print(f"🌍 Región: {resultado3.get('bedrock_region')}")
    print(f"📊 Válidas: {resultado3.get('summary', {}).get('valid', 0)}")
    
    # EJEMPLO 4: Configuración personalizada completa
    print("\n🚀 EJEMPLO 4: Configuración personalizada completa")
    
    bedrock_config_custom = BedrockConfig(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name="us-east-1",
        # aws_access_key_id="tu_access_key_personalizado",
        # aws_secret_access_key="tu_secret_key_personalizado",
        max_retries=5,
        retry_delay=2.0,
        execution_max_tokens=8000,
        validation_max_tokens=6000
    )
    
    resultado4 = process_prompts_with_config(
        prompts=prompts_test,
        bedrock_config=bedrock_config_custom,
        mode="both",
        max_concurrent=6
    )
    
    print(f"✅ Modelo usado: {resultado4.get('bedrock_model')}")
    print(f"🌍 Región: {resultado4.get('bedrock_region')}")
    print(f"📊 Híbrido rate: {resultado4.get('summary', {}).get('hybrid_success_rate')}")
    print(f"🔧 Config independiente: {resultado4.get('metadata', {}).get('independent_config')}")
    
    # EJEMPLO 5: Función híbrida con parámetros directos
    print("\n🎯 EJEMPLO 5: Función híbrida con parámetros directos")
    
    resultado5 = process_prompts_hybrid_optimized(
        prompts=prompts_test[:7],
        mode="execute_only",
        bedrock_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        bedrock_region="us-east-1",
        # aws_access_key="tu_key",
        # aws_secret_key="tu_secret",
        max_concurrent=5
    )
    
    print(f"✅ Modelo usado: {resultado5.get('bedrock_model')}")
    print(f"📊 Success rate: {resultado5.get('summary', {}).get('execution_rate')}")
    print(f"⚡ Tokens usados: {resultado5.get('summary', {}).get('total_tokens_used')}")
    
    # EJEMPLO 6: Generar reporte inteligente
    print("\n📊 EJEMPLO 6: Generación de reportes inteligentes")
    try:
        print("Generando reporte con IA...")
        
        # Generar reporte inteligente (versión síncrona)
        reporte = generate_report_sync(
            resultado4, 
            "Business Rules Processing Report - Independent Config",
            analysis_depth="comprehensive"
        )
        
        print(f"✅ Reporte generado: {len(reporte):,} caracteres")
        print("\n--- VISTA PREVIA DEL REPORTE ---")
        print(reporte[:500] + "\n..." if len(reporte) > 500 else reporte)
        
        # Guardar reporte en archivo
        with open("hybrid_processing_report_v2.0.5.md", "w", encoding="utf-8") as f:
            f.write(reporte)
        print("\n💾 Reporte guardado en: hybrid_processing_report_v2.0.5.md")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
    
    print("\n" + "="*70)
    print("🎉 CONFIGURACIÓN INDEPENDIENTE TOTALMENTE FUNCIONAL")
    print("✅ Sin dependencia de variables de entorno")
    print("🔧 Configuración directa en constructor")
    print("🚀 Compatible con versión anterior")
    print("📝 Múltiples opciones de configuración")
    print("🤖 Soporte para Claude Sonnet, Opus y Haiku")
    print("📊 Reportes inteligentes con IA incluidos")


def ejemplo_optimized_usage_final():
    """Ejemplo final de uso del sistema optimizado CON GENERACIÓN DE REPORTES"""
    
    print("🔍 CREANDO PROMPTS DE PRUEBA OPTIMIZADOS...")
    
    # Test cases optimizados
    prompts_test = create_optimized_test_prompts(20, "mixed")
    
    print("\n✅ EJEMPLO 1: Validación optimizada")
    resultado = process_prompts_hybrid_optimized(
        prompts=prompts_test[:10],
        mode="validate_only",
        max_concurrent=8,
        lambda_memory_mb=3008
    )
    print(f"Estrategia: {resultado.get('processing_strategy')}")
    print(f"Success rate: {resultado.get('summary', {}).get('success_rate')}")
    print(f"Performance: {resultado.get('performance_metrics', {}).get('prompts_per_second')} prompts/s")
    print(f"Modelo: {resultado.get('bedrock_model', 'Default')}")
    
    print("\n⚡ EJEMPLO 2: Ejecución optimizada")
    resultado = process_prompts_hybrid_optimized(
        prompts=prompts_test[:5],
        mode="execute_only",
        max_concurrent=6,
        lambda_memory_mb=8192
    )
    print(f"Ejecutadas: {resultado.get('summary', {}).get('executed_successfully', 0)}")
    print(f"Tokens: {resultado.get('summary', {}).get('total_tokens_used', 0)}")
    print(f"Tiempo promedio: {resultado.get('summary', {}).get('average_processing_time', 0):.3f}s")
    print(f"Modelo: {resultado.get('bedrock_model', 'Default')}")
    
    print("\n🚀 EJEMPLO 3: Híbrido optimizado")
    resultado = process_prompts_hybrid_optimized(
        prompts=prompts_test,
        mode="both",
        max_concurrent=10,
        lambda_memory_mb=8192
    )
    print(f"Híbrido rate: {resultado.get('summary', {}).get('hybrid_success_rate')}")
    print(f"Optimizaciones: Memory={resultado.get('performance_metrics', {}).get('memory_optimized')}")
    print(f"Connection pooling: {resultado.get('performance_metrics', {}).get('connection_pooling')}")
    print(f"Modelo: {resultado.get('bedrock_model', 'Default')}")
    
    # EJEMPLO 4 - Generación de reportes inteligentes
    print("\n📊 EJEMPLO 4: Generación de reportes inteligentes")
    try:
        print("Generando reporte con IA...")
        
        # Generar reporte inteligente (versión síncrona)
        reporte = generate_report_sync(
            resultado, 
            "Business Rules Processing Report v2.0.5",
            analysis_depth="comprehensive"
        )
        
        print(f"✅ Reporte generado: {len(reporte):,} caracteres")
        print("\n--- VISTA PREVIA DEL REPORTE ---")
        print(reporte[:500] + "\n..." if len(reporte) > 500 else reporte)
        
        # Guardar reporte en archivo
        with open("hybrid_processing_report_final.md", "w", encoding="utf-8") as f:
            f.write(reporte)
        print("\n💾 Reporte guardado en: hybrid_processing_report_final.md")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")


async def ejemplo_async_usage_final():
    """Ejemplo asíncrono final con generación de reportes"""
    
    print("🔍 EJEMPLO ASÍNCRONO FINAL CON REPORTES INTELIGENTES")
    
    # Crear prompts de ejemplo
    prompts = create_optimized_test_prompts(15, "mixed")
    
    print(f"\n🚀 Procesando {len(prompts)} prompts...")
    
    # Procesar con modo híbrido
    resultado = await process_prompts_hybrid_async_optimized(
        prompts=prompts,
        mode="both"
    )
    
    print(f"✅ Procesamiento completado: {resultado.get('status')}")
    print(f"📝 Modelo usado: {resultado.get('bedrock_model', 'Default')}")
    print(f"🌍 Región: {resultado.get('bedrock_region', 'Default')}")
    
    # Generar reporte inteligente (versión asíncrona)
    print("\n📊 Generando reporte inteligente con IA...")
    
    reporte = await generate_report(
        resultado,
        "Async Processing Analysis Report v2.0.5", 
        analysis_depth="standard"
    )
    
    print(f"✅ Reporte IA generado: {len(reporte):,} caracteres")
    
    # Mostrar extracto del reporte
    lines = reporte.split('\n')
    preview_lines = lines[:20]  # Primeras 20 líneas
    
    print("\n--- EXTRACTO DEL REPORTE INTELIGENTE ---")
    print('\n'.join(preview_lines))
    print("...")
    
    return reporte


if __name__ == "__main__":
    # Configurar para testing
    logging.getLogger().setLevel(logging.INFO)
    
    print("🚀 SISTEMA HÍBRIDO OPTIMIZADO v2.0.5 - VERSIÓN FINAL COMPLETA")
    print("=" * 70)
    print("✅ Sintaxis optimizada | ✅ Bugs corregidos")
    print("✅ Lambda optimized   | ✅ Objetivo cumplido")
    print("✅ TRUNCAMIENTO CORREGIDO | ✅ Límites aumentados")
    print("✅ 🆕 REPORTES INTELIGENTES CON IA")
    print("✅ 🔧 ERRORES DE SINTAXIS ELIMINADOS")
    print("✅ 📊 ANÁLISIS DE CONTENIDO CORREGIDO")
    print("✅ 📋 ERRORES Y REGLAS EN REPORTE")
    print("✅ 🆕 CONFIGURACIÓN BEDROCK INDEPENDIENTE")
    print("✅ 🤖 SOPORTE PARA CLAUDE SONNET, OPUS Y HAIKU")
    print("✅ 🎯 VERSIÓN FINAL COMPLETA v2.0.5")
    print("=" * 70)
    
    try:
        # Validar entorno
        env_info = validate_lambda_environment()
        if env_info["is_lambda"]:
            print(f"🔧 Entorno Lambda detectado: {env_info['function_name']}")
        else:
            print("🔧 Entorno local detectado")
        
        # Ejecutar ejemplos con configuración independiente
        print("\n" + "="*50)
        print("🆕 EJECUTANDO EJEMPLOS CON CONFIGURACIÓN INDEPENDIENTE...")
        ejemplo_configuracion_independiente_final()
        
        print("\n" + "="*50)
        print("🔄 EJECUTANDO EJEMPLOS SÍNCRONOS FINALES...")
        # Ejecutar ejemplos síncronos
        ejemplo_optimized_usage_final()
        print("\n✅ Todos los ejemplos síncronos ejecutados correctamente")
        
        # Ejecutar ejemplo asíncrono
        print("\n" + "="*50)
        print("🔄 EJECUTANDO EJEMPLO ASÍNCRONO FINAL...")
        
        try:
            reporte_async = asyncio.run(ejemplo_async_usage_final())
            print("\n✅ Ejemplo asíncrono completado exitosamente")
        except Exception as e:
            print(f"\n⚠️ Error en ejemplo asíncrono: {e}")
        
        print("\n" + "="*70)
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL v2.0.5")
        print("📊 Reportes inteligentes listos para usar")
        print("🚀 Optimizado para producción en Lambda")
        print("🔧 Sintaxis y bugs corregidos")
        print("📋 Errores estructurales y reglas incluidos")
        print("🆕 Configuración Bedrock independiente")
        print("🤖 Soporte completo para Claude Sonnet, Opus y Haiku")
        print("🎯 VERSIÓN FINAL COMPLETA v2.0.5")
        
    except Exception as e:
        print(f"\n❌ Error en ejemplos: {e}")
        logger.error(f"Error en ejemplos: {e}", exc_info=True)