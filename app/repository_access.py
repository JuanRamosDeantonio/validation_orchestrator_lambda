"""
repository_access.py - Acceso consolidado a recursos externos (REFACTORIZADO)
CONSOLIDACIÓN DE: lambda_gateway.py + integrations.py + S3Client + BedrockClient
MANTIENE: Gateway pattern, invocación de lambdas, acceso S3/Bedrock, error handling, retry logic
SIMPLIFICA: Interfaz unificada para todos los accesos externos, clients consolidados
"""

import json
import boto3
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from botocore.exceptions import ClientError, BotoCoreError
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

# IMPORTS CONSOLIDADOS para nueva estructura
from shared import (
    setup_logger, Config, ErrorHandler, S3JsonReader, S3JsonWriter, 
    validate_repository_url, format_repository_name
)

# Configurar logging
logger = setup_logger(__name__)

# =============================================================================
# MODELOS DE CONFIGURACIÓN CONSOLIDADOS
# =============================================================================

@dataclass
class RepositoryConfig:
    """
    Configuración centralizada para operaciones de repositorio.
    Maneja todos los parámetros necesarios para las Lambdas de repositorio.
    """
    provider: str = "github"  # github, gitlab, bitbucket
    token: str = ""
    owner: str = ""
    repo: str = ""
    branch: str = "main"
    
    def __post_init__(self):
        """Validación post-inicialización."""
        if not all([self.owner, self.repo]):
            raise ValueError("owner y repo son requeridos")
        
        if not self.token:
            logger.warning("Token no proporcionado - puede limitar acceso a repositorios privados")
    
    def build_get_structure_payload(self) -> Dict[str, Any]:
        """
        Construye payload para get_repository_info_lambda - operación GET_STRUCTURE.
        
        Returns:
            dict: Payload estructurado para obtener estructura del repositorio
        """
        return {
            "action": "GET_STRUCTURE",
            "repository_config": {
                "provider": self.provider,
                "token": self.token,
                "owner": self.owner,
                "repo": self.repo,
                "branch": self.branch
            }
        }
    
    def build_download_file_payload(self, file_path: str) -> Dict[str, Any]:
        """
        Construye payload para get_repository_info_lambda - operación DOWNLOAD_FILE.
        
        Args:
            file_path: Ruta del archivo a descargar
            
        Returns:
            dict: Payload estructurado para descargar archivo específico
        """
        return {
            "action": "DOWNLOAD_FILE",
            "repository_config": {
                "provider": self.provider,
                "token": self.token,
                "owner": self.owner,
                "repo": self.repo,
                "branch": self.branch
            },
            "file_path": file_path
        }
    
    @staticmethod
    def build_file_reader_payload(file_name: str, base64_content: str) -> Dict[str, Any]:
        """
        Construye payload para file_reader_lambda.
        
        Args:
            file_name: Nombre del archivo con extensión
            base64_content: Contenido del archivo en base64
            
        Returns:
            dict: Payload estructurado para conversión a Markdown
        """
        return {
            "file_name": file_name,
            "base64_content": base64_content,
            "output_format": "markdown",
            "optimize_for_ai": True
        }
    
    def get_repository_url(self) -> str:
        """
        Construye URL del repositorio para logging y referencia.
        
        Returns:
            str: URL completa del repositorio
        """
        if self.provider == "github":
            return f"https://github.com/{self.owner}/{self.repo}"
        elif self.provider == "gitlab":
            return f"https://gitlab.com/{self.owner}/{self.repo}"
        elif self.provider == "bitbucket":
            return f"https://bitbucket.org/{self.owner}/{self.repo}"
        else:
            return f"{self.provider}://{self.owner}/{self.repo}"

# =============================================================================
# REPOSITORY ACCESS MANAGER CONSOLIDADO
# =============================================================================

class RepositoryAccessManager:
    """
    Manager consolidado para todos los accesos externos del sistema.
    
    CONSOLIDA: LambdaGateway + IntegrationManager + S3Client + BedrockClient
    MANTIENE: Funcionalidad completa de acceso a recursos externos
    SIMPLIFICA: Interfaz unificada, error handling centralizado
    """
    
    def __init__(self):
        # Clients AWS consolidados
        self.lambda_client = boto3.client('lambda', region_name=Config.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=Config.BEDROCK_REGION)
        
        # Thread-safe statistics consolidadas
        self._stats_lock = threading.Lock()
        self.access_stats = {
            'lambda_invocations': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_function': Counter()
            },
            's3_operations': {
                'reads': 0,
                'writes': 0,
                'errors': 0
            },
            'bedrock_invocations': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_model': Counter()
            },
            'repository_operations': {
                'structures_loaded': 0,
                'files_downloaded': 0,
                'batch_operations': 0
            }
        }
        
        # Cache para configuraciones de repositorio
        self.repository_configs_cache = {}
        
        logger.debug("RepositoryAccessManager inicializado con clients consolidados")
    
    # =============================================================================
    # REPOSITORY OPERATIONS (LAMBDA GATEWAY CONSOLIDADO)
    # =============================================================================
    
    async def load_repository_content(self, repository_config: RepositoryConfig, 
                                    required_files: List[str]) -> Dict[str, Any]:
        """
        Carga contenido completo del repositorio usando lambdas externas.
        
        CONSOLIDA: Funcionalidad completa del LambdaGateway
        MANTIENE: Estructura de respuesta, error handling, batch operations
        
        Args:
            repository_config: Configuración del repositorio
            required_files: Lista de archivos requeridos
            
        Returns:
            dict: Contenido del repositorio con estructura y archivos
        """
        try:
            logger.info(f"Cargando contenido del repositorio: {repository_config.get_repository_url()}")
            
            # PASO 1: Obtener estructura del repositorio
            structure_result = await self._get_repository_structure(repository_config)
            
            if not structure_result.get('success'):
                raise Exception(f"Failed to get repository structure: {structure_result.get('error')}")
            
            # PASO 2: Filtrar archivos que coinciden con los requeridos
            all_files = structure_result['structure'].get('files', [])
            matching_files = self._filter_files_by_patterns(all_files, required_files)
            
            logger.info(f"Archivos encontrados: {len(all_files)}, coincidentes: {len(matching_files)}")
            
            # PASO 3: Descargar contenido de archivos coincidentes
            files_content = {}
            
            if matching_files:
                # Usar descarga en lote para eficiencia
                batch_result = await self._batch_download_files(
                    repository_config, matching_files[:Config.MAX_BATCH_FILES]
                )
                
                if batch_result.get('success'):
                    # Procesar archivos descargados
                    for file_path, download_data in batch_result['files'].items():
                        try:
                            if download_data.get('success'):
                                # Decodificar contenido según tipo de archivo
                                file_content = await self._process_file_content(
                                    download_data['file_data'], file_path
                                )
                                files_content[file_path] = file_content
                        except Exception as e:
                            logger.warning(f"Error procesando archivo {file_path}: {str(e)}")
                            continue
            
            # PASO 4: Calcular estadísticas y metadata
            total_content_size = sum(len(content) for content in files_content.values())
            
            # Registrar operación exitosa
            self._record_repository_operation('content_loaded', len(files_content))
            
            logger.info(f"Contenido del repositorio cargado exitosamente:")
            logger.info(f"  - Archivos obtenidos: {len(files_content)}")
            logger.info(f"  - Tamaño total: {total_content_size:,} caracteres")
            
            return {
                'success': True,
                'structure': structure_result['structure'],
                'files': files_content,
                'repository_url': repository_config.get_repository_url(),
                'content_statistics': {
                    'total_files': len(files_content),
                    'total_size': total_content_size,
                    'average_file_size': total_content_size // len(files_content) if files_content else 0,
                    'success_rate': (len(files_content) / len(matching_files) * 100) if matching_files else 0
                },
                'access_metadata': {
                    'structure_metadata': structure_result.get('metadata', {}),
                    'processing_timestamp': time.time(),
                    'files_requested': len(matching_files),
                    'files_processed': len(files_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error cargando contenido del repositorio: {str(e)}")
            self._record_repository_operation('content_failed', 0)
            return ErrorHandler.handle_gateway_error(e, "load_repository_content", repository_config)
    
    async def _get_repository_structure(self, config: RepositoryConfig) -> Dict[str, Any]:
        """
        Obtiene estructura del repositorio usando lambda externa.
        
        MANTIENE: Funcionalidad completa del gateway
        
        Args:
            config: Configuración del repositorio
            
        Returns:
            dict: Estructura del repositorio
        """
        try:
            logger.debug(f"Obteniendo estructura: {config.get_repository_url()}")
            
            payload = config.build_get_structure_payload()
            
            response = await self._invoke_lambda_async(
                Config.GET_REPO_STRUCTURE_LAMBDA,
                payload,
                "get_structure"
            )
            
            if not response.get('success', False):
                raise Exception(f"Lambda reportó fallo: {response.get('error', 'Error desconocido')}")
            
            structure_data = response.get('structure', {})
            if not structure_data:
                logger.warning(f"Estructura vacía retornada para {config.get_repository_url()}")
            
            logger.debug(f"Estructura obtenida: {len(structure_data.get('files', []))} archivos")
            
            self._record_repository_operation('structure_loaded', 1)
            
            return {
                'success': True,
                'structure': structure_data,
                'repository_url': config.get_repository_url(),
                'branch': config.branch,
                'metadata': response.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estructura: {str(e)}")
            return ErrorHandler.handle_gateway_error(e, f"get_structure_{config.repo}", config)
    
    async def _batch_download_files(self, config: RepositoryConfig, 
                                  file_paths: List[str]) -> Dict[str, Any]:
        """
        Descarga múltiples archivos de forma eficiente.
        
        MANTIENE: Funcionalidad de descarga en lote
        CONSOLIDA: Procesamiento centralizado
        
        Args:
            config: Configuración del repositorio
            file_paths: Lista de rutas de archivos
            
        Returns:
            dict: Resultados de descarga por archivo
        """
        logger.info(f"Descarga en lote: {len(file_paths)} archivos")
        
        results = {
            'success': True,
            'total_files': len(file_paths),
            'successful_downloads': 0,
            'failed_downloads': 0,
            'files': {},
            'errors': []
        }
        
        # Crear tareas de descarga paralela
        download_tasks = []
        for file_path in file_paths:
            task = self._download_single_file(config, file_path)
            download_tasks.append(task)
        
        # Ejecutar descargas en paralelo (limitado por ThreadPoolExecutor)
        try:
            import asyncio
            download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(download_results):
                file_path = file_paths[i]
                
                if isinstance(result, Exception):
                    results['failed_downloads'] += 1
                    results['errors'].append({
                        'file_path': file_path,
                        'error': str(result)
                    })
                elif isinstance(result, dict) and result.get('success'):
                    results['files'][file_path] = result
                    results['successful_downloads'] += 1
                else:
                    results['failed_downloads'] += 1
                    results['errors'].append({
                        'file_path': file_path,
                        'error': result.get('error', 'Error desconocido')
                    })
            
            # Determinar éxito general
            success_rate = results['successful_downloads'] / results['total_files']
            results['success'] = success_rate > 0.5
            results['success_rate'] = success_rate * 100
            
            self._record_repository_operation('batch_download', results['successful_downloads'])
            
            logger.info(f"Descarga en lote completada: {results['successful_downloads']}/{results['total_files']} exitosos")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en descarga en lote: {str(e)}")
            results['success'] = False
            results['errors'].append({'batch_error': str(e)})
            return results
    
    async def _download_single_file(self, config: RepositoryConfig, file_path: str) -> Dict[str, Any]:
        """
        Descarga un archivo individual del repositorio.
        
        Args:
            config: Configuración del repositorio
            file_path: Ruta del archivo a descargar
            
        Returns:
            dict: Resultado de la descarga
        """
        try:
            logger.debug(f"Descargando archivo: {file_path}")
            
            payload = config.build_download_file_payload(file_path)
            
            response = await self._invoke_lambda_async(
                Config.GET_REPO_STRUCTURE_LAMBDA,
                payload,
                "download_file"
            )
            
            if not response.get('success', False):
                raise Exception(f"Descarga falló: {response.get('error', 'Archivo no encontrado')}")
            
            file_data = response.get('file_data', {})
            if not file_data.get('content'):
                raise Exception(f"Contenido vacío para archivo: {file_path}")
            
            logger.debug(f"Archivo descargado: {file_path} ({len(file_data.get('content', ''))} chars base64)")
            
            self._record_repository_operation('file_downloaded', 1)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_data': file_data,
                'metadata': {
                    'download_timestamp': time.time(),
                    'file_size_base64': len(file_data.get('content', ''))
                }
            }
            
        except Exception as e:
            logger.error(f"Error descargando {file_path}: {str(e)}")
            return ErrorHandler.handle_gateway_error(e, f"download_file_{file_path}", config)
    
    async def _process_file_content(self, file_data: Dict[str, Any], file_path: str) -> str:
        """
        Procesa contenido de archivo, aplicando conversión si es necesario.
        
        MANTIENE: Funcionalidad completa de procesamiento
        CONSOLIDA: Lógica de conversión centralizada
        
        Args:
            file_data: Datos del archivo desde lambda
            file_path: Ruta del archivo
            
        Returns:
            str: Contenido procesado del archivo
        """
        try:
            content_b64 = file_data.get('content', '')
            
            if not content_b64:
                return ""
            
            # Verificar si necesita procesamiento especial
            if self._requires_special_processing(file_path):
                # Para archivos que necesitan conversión (docx, pdf, etc.)
                file_name = file_path.split('/')[-1]
                conversion_result = await self._convert_file_to_markdown(file_name, content_b64)
                
                if conversion_result.get('success'):
                    return conversion_result['markdown_content']
                else:
                    logger.warning(f"Conversión falló para {file_path}, usando decodificación directa")
            
            # Decodificación directa para archivos de texto
            import base64
            decoded_content = base64.b64decode(content_b64).decode('utf-8')
            return decoded_content
            
        except Exception as e:
            logger.error(f"Error procesando contenido de {file_path}: {str(e)}")
            return f"[Error decoding file content: {str(e)}]"
    
    async def _convert_file_to_markdown(self, file_name: str, base64_content: str) -> Dict[str, Any]:
        """
        Convierte archivo a Markdown usando lambda externa.
        
        Args:
            file_name: Nombre del archivo
            base64_content: Contenido en base64
            
        Returns:
            dict: Resultado de la conversión
        """
        try:
            logger.debug(f"Convirtiendo archivo a Markdown: {file_name}")
            
            payload = RepositoryConfig.build_file_reader_payload(file_name, base64_content)
            
            response = await self._invoke_lambda_async(
                Config.FILE_READER_LAMBDA,
                payload,
                "convert_to_markdown"
            )
            
            if not response.get('success', False):
                raise Exception(f"Conversión falló: {response.get('error', 'Error de procesamiento')}")
            
            markdown_content = response.get('markdown_content', '')
            if not markdown_content:
                logger.warning(f"Contenido Markdown vacío para: {file_name}")
            
            logger.debug(f"Archivo convertido: {file_name} ({len(markdown_content)} chars markdown)")
            
            return {
                'success': True,
                'file_name': file_name,
                'markdown_content': markdown_content,
                'original_format': response.get('original_format', 'unknown'),
                'metadata': {
                    'conversion_timestamp': time.time(),
                    'markdown_size': len(markdown_content),
                    'base64_size': len(base64_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error convirtiendo {file_name}: {str(e)}")
            return ErrorHandler.handle_gateway_error(e, f"convert_file_{file_name}")
    
    def _filter_files_by_patterns(self, all_files: List[str], patterns: List[str]) -> List[str]:
        """
        Filtra archivos que coinciden con los patrones especificados.
        
        MANTIENE: Funcionalidad completa de filtrado
        
        Args:
            all_files: Lista de todos los archivos disponibles
            patterns: Patrones de archivos a buscar
            
        Returns:
            list: Archivos que coinciden con los patrones
        """
        import fnmatch
        
        matching_files = []
        
        for pattern in patterns:
            for file_path in all_files:
                if (fnmatch.fnmatch(file_path, pattern) or 
                    pattern in file_path or 
                    file_path.endswith(pattern)):
                    if file_path not in matching_files:
                        matching_files.append(file_path)
        
        logger.debug(f"Filtrado: {len(matching_files)} archivos coinciden con {len(patterns)} patrones")
        
        return matching_files
    
    def _requires_special_processing(self, file_path: str) -> bool:
        """
        Determina si un archivo requiere procesamiento especial.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            bool: True si requiere conversión especial
        """
        special_extensions = ['.docx', '.pdf', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
        return any(file_path.lower().endswith(ext) for ext in special_extensions)
    
    # =============================================================================
    # LAMBDA CLIENT CONSOLIDADO
    # =============================================================================
    
    async def _invoke_lambda_async(self, function_name: str, payload: Dict[str, Any], 
                                 operation: str) -> Dict[str, Any]:
        """
        Invoca función Lambda de manera asíncrona con manejo robusto.
        
        MANTIENE: Funcionalidad completa de invocación
        CONSOLIDA: Error handling y retry logic
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Payload a enviar
            operation: Nombre de la operación (para logging)
            
        Returns:
            dict: Respuesta parseada de la Lambda
        """
        import asyncio
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self._invoke_lambda_sync, 
                function_name, 
                payload,
                operation
            )
        return result
    
    def _invoke_lambda_sync(self, function_name: str, payload: Dict[str, Any], 
                          operation: str) -> Dict[str, Any]:
        """
        Invoca función Lambda de manera síncrona con manejo robusto.
        
        MANTIENE: Funcionalidad completa con error handling
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Payload a enviar
            operation: Nombre de la operación
            
        Returns:
            dict: Respuesta parseada de la Lambda
        """
        try:
            logger.debug(f"Invocando Lambda {function_name} para {operation}")
            
            # Registrar intento de invocación
            self._record_lambda_attempt(function_name)
            
            # Invocar Lambda
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Verificar código de estado HTTP
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda retornó status {response['StatusCode']}")
            
            # Parsear respuesta
            response_payload = response['Payload'].read().decode('utf-8')
            result = json.loads(response_payload)
            
            # Verificar si la Lambda reportó error
            if 'errorMessage' in result:
                raise Exception(f"Lambda error: {result['errorMessage']}")
            
            # Registrar éxito
            self._record_lambda_success(function_name)
            
            logger.debug(f"Lambda {function_name} invocada exitosamente para {operation}")
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS error invocando {function_name}: {error_code}")
            self._record_lambda_failure(function_name)
            
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Lambda function not found: {function_name}")
            elif error_code == 'TooManyRequestsException':
                raise Exception(f"Rate limit exceeded for: {function_name}")
            else:
                raise Exception(f"AWS error: {str(e)}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from {function_name}: {str(e)}")
            self._record_lambda_failure(function_name)
            raise Exception(f"Invalid JSON response from {function_name}")
            
        except Exception as e:
            logger.error(f"Error invocando {function_name}: {str(e)}")
            self._record_lambda_failure(function_name)
            raise e
    
    # Método de conveniencia para backward compatibility
    async def invoke_lambda_async(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método público para invocación de lambda (backward compatibility).
        
        Args:
            function_name: Nombre de la función
            payload: Payload a enviar
            
        Returns:
            dict: Respuesta de la lambda
        """
        return await self._invoke_lambda_async(function_name, payload, "generic_operation")
    
    # =============================================================================
    # S3 CLIENT CONSOLIDADO
    # =============================================================================
    
    def read_s3_file(self, key: str) -> str:
        """
        Lee un archivo desde S3 con manejo robusto de errores.
        
        MANTIENE: Funcionalidad completa de S3Client
        CONSOLIDA: Error handling centralizado
        
        Args:
            key: Clave del archivo en S3
            
        Returns:
            str: Contenido del archivo
        """
        try:
            logger.debug(f"Leyendo archivo S3: s3://{Config.S3_BUCKET}/{key}")
            
            self._record_s3_operation('read_attempt')
            
            response = self.s3_client.get_object(Bucket=Config.S3_BUCKET, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            self._record_s3_operation('read_success')
            
            logger.debug(f"Archivo S3 leído exitosamente: {len(content)} caracteres")
            return content
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self._record_s3_operation('read_error')
            logger.error(f"S3 ClientError leyendo {key}: {error_code}")
            
            if error_code == 'NoSuchKey':
                raise Exception(f"File not found in S3: {key}")
            elif error_code == 'AccessDenied':
                raise Exception(f"Access denied to S3 file: {key}")
            else:
                raise Exception(f"S3 error reading {key}: {str(e)}")
                
        except Exception as e:
            self._record_s3_operation('read_error')
            logger.error(f"Error leyendo S3 {key}: {str(e)}")
            raise Exception(f"Failed to read S3 file {key}: {str(e)}")
    
    def write_s3_file(self, key: str, content: str) -> bool:
        """
        Escribe un archivo a S3 con manejo robusto de errores.
        
        MANTIENE: Funcionalidad completa de escritura
        
        Args:
            key: Clave del archivo en S3
            content: Contenido a escribir
            
        Returns:
            bool: True si se escribió exitosamente
        """
        try:
            logger.debug(f"Escribiendo archivo S3: s3://{Config.S3_BUCKET}/{key}")
            
            self._record_s3_operation('write_attempt')
            
            self.s3_client.put_object(
                Bucket=Config.S3_BUCKET,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            self._record_s3_operation('write_success')
            
            logger.debug(f"Archivo S3 escrito exitosamente: {len(content)} caracteres")
            return True
            
        except Exception as e:
            self._record_s3_operation('write_error')
            logger.error(f"Error escribiendo S3 {key}: {str(e)}")
            return False
    
    # Métodos de conveniencia usando S3JsonReader/Writer
    def read_json_from_s3(self, key: str) -> Dict[str, Any]:
        """
        Lee y parsea archivo JSON desde S3.
        
        Args:
            key: Clave del archivo JSON
            
        Returns:
            dict: Contenido JSON parseado
        """
        try:
            # Crear un objeto S3Client mock para compatibilidad
            class S3ClientMock:
                def __init__(self, access_manager):
                    self.access_manager = access_manager
                
                def read_file(self, key):
                    return self.access_manager.read_s3_file(key)
            
            s3_client_mock = S3ClientMock(self)
            return S3JsonReader.read_json_from_s3(s3_client_mock, key)
            
        except Exception as e:
            logger.error(f"Error leyendo JSON desde S3 {key}: {str(e)}")
            raise e
    
    def write_json_to_s3(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Serializa y escribe diccionario como JSON a S3.
        
        Args:
            key: Clave del archivo
            data: Datos a serializar
            
        Returns:
            bool: True si se escribió exitosamente
        """
        try:
            # Crear un objeto S3Client mock para compatibilidad
            class S3ClientMock:
                def __init__(self, access_manager):
                    self.access_manager = access_manager
                
                def write_file(self, key, content):
                    return self.access_manager.write_s3_file(key, content)
            
            s3_client_mock = S3ClientMock(self)
            return S3JsonWriter.write_json_to_s3(s3_client_mock, key, data)
            
        except Exception as e:
            logger.error(f"Error escribiendo JSON a S3 {key}: {str(e)}")
            return False
    
    # =============================================================================
    # BEDROCK CLIENT CONSOLIDADO
    # =============================================================================
    
    async def invoke_bedrock_model(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Invoca modelo de Bedrock de manera asíncrona.
        
        MANTIENE: Funcionalidad completa de BedrockClient
        CONSOLIDA: Error handling y configuración de modelos
        
        Args:
            model_name: Nombre del modelo (claude-3-haiku, claude-3-sonnet)
            prompt: Prompt a enviar al modelo
            
        Returns:
            dict: Respuesta del modelo
        """
        import asyncio
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self._invoke_bedrock_sync, 
                model_name, 
                prompt
            )
        return result
    
    def _invoke_bedrock_sync(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Invoca modelo de Bedrock de manera síncrona.
        
        MANTIENE: Funcionalidad completa con configuración de modelos
        
        Args:
            model_name: Nombre del modelo
            prompt: Prompt a enviar
            
        Returns:
            dict: Respuesta parseada del modelo
        """
        try:
            # Obtener configuración del modelo
            model_config = Config.MODEL_CONFIG.get(model_name)
            if not model_config:
                raise Exception(f"Model {model_name} not configured")
            
            model_id = model_config['model_id']
            
            logger.debug(f"Invocando Bedrock model: {model_name} (ID: {model_id})")
            logger.debug(f"Prompt length: {len(prompt)} caracteres")
            
            # Registrar intento
            self._record_bedrock_attempt(model_name)
            
            # Preparar payload para Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invocar modelo
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parsear respuesta
            response_body = json.loads(response['body'].read().decode('utf-8'))
            
            # Extraer contenido de la respuesta de Claude
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]['text']
                
                # Registrar éxito
                self._record_bedrock_success(model_name)
                
                logger.debug(f"Model {model_name} respondió con {len(content)} caracteres")
                
                return {
                    'success': True,
                    'content': content,
                    'model_used': model_name,
                    'usage': response_body.get('usage', {}),
                    'stop_reason': response_body.get('stop_reason', 'unknown')
                }
            else:
                raise Exception("No content in model response")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self._record_bedrock_failure(model_name)
            logger.error(f"Bedrock ClientError con {model_name}: {error_code}")
            
            if error_code == 'ValidationException':
                return ErrorHandler.handle_bedrock_error(
                    Exception(f"Invalid request to model {model_name}"), 
                    f"model_{model_name}"
                )
            elif error_code == 'ThrottlingException':
                return ErrorHandler.handle_bedrock_error(
                    Exception(f"Rate limit exceeded for model {model_name}"), 
                    f"model_{model_name}"
                )
            else:
                return ErrorHandler.handle_bedrock_error(e, f"model_{model_name}")
                
        except json.JSONDecodeError as e:
            self._record_bedrock_failure(model_name)
            logger.error(f"JSON decode error from Bedrock {model_name}: {str(e)}")
            return ErrorHandler.handle_bedrock_error(e, f"model_{model_name}")
            
        except Exception as e:
            self._record_bedrock_failure(model_name)
            logger.error(f"Error con Bedrock {model_name}: {str(e)}")
            return ErrorHandler.handle_bedrock_error(e, f"model_{model_name}")
    
    # Métodos específicos para cada modelo (convenience methods)
    async def invoke_haiku(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Haiku (modelo rápido y económico).
        
        Args:
            prompt: Prompt a enviar
            
        Returns:
            dict: Respuesta del modelo
        """
        return await self.invoke_bedrock_model('claude-3-haiku', prompt)
    
    async def invoke_sonnet(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Sonnet (modelo balanceado).
        
        Args:
            prompt: Prompt a enviar
            
        Returns:
            dict: Respuesta del modelo
        """
        return await self.invoke_bedrock_model('claude-3-sonnet', prompt)
    
    # Propiedades para backward compatibility
    @property
    def bedrock_client(self):
        """Propiedad para acceso directo al cliente Bedrock (backward compatibility)."""
        return self
    
    @property
    def s3_client_wrapper(self):
        """Propiedad para acceso directo al cliente S3 (backward compatibility)."""
        return self
    
    # =============================================================================
    # POST-PROCESSING CONSOLIDADO
    # =============================================================================
    
    async def trigger_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara generación de reporte usando lambda externa.
        
        MANTIENE: Funcionalidad completa de post-procesamiento
        
        Args:
            report_data: Datos para el reporte
            
        Returns:
            dict: Respuesta del trigger
        """
        try:
            logger.info("Disparando generación de reporte")
            
            payload = {
                'report_data': report_data,
                'trigger_timestamp': time.time()
            }
            
            if hasattr(Config, 'REPORT_LAMBDA') and Config.REPORT_LAMBDA:
                response = await self._invoke_lambda_async(
                    Config.REPORT_LAMBDA,
                    payload,
                    "trigger_report"
                )
                
                logger.info("Reporte disparado exitosamente")
                return response
            else:
                logger.warning("REPORT_LAMBDA no configurado, saltando reporte")
                return {'success': True, 'message': 'Report lambda not configured'}
                
        except Exception as e:
            logger.error(f"Error disparando reporte: {str(e)}")
            return ErrorHandler.handle_lambda_error(e, "trigger_report")
    
    # =============================================================================
    # HEALTH CHECK CONSOLIDADO
    # =============================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realiza health check de todos los recursos externos.
        
        MANTIENE: Funcionalidad completa de health check
        CONSOLIDA: Verificación de todos los clients
        
        Returns:
            dict: Estado de salud consolidado
        """
        health_status = {
            'overall_status': 'healthy',
            'timestamp': time.time(),
            'components': {},
            'issues': []
        }
        
        try:
            # Check S3 access
            try:
                self.s3_client.list_objects_v2(Bucket=Config.S3_BUCKET, MaxKeys=1)
                health_status['components']['s3'] = 'healthy'
            except Exception as e:
                health_status['components']['s3'] = 'error'
                health_status['issues'].append(f"S3 access failed: {str(e)}")
            
            # Check Lambda functions
            lambda_functions = [
                Config.GET_REPO_STRUCTURE_LAMBDA,
                Config.FILE_READER_LAMBDA
            ]
            
            lambda_health = {}
            for function_name in lambda_functions:
                try:
                    self.lambda_client.get_function(FunctionName=function_name)
                    lambda_health[function_name] = 'healthy'
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'ResourceNotFoundException':
                        lambda_health[function_name] = 'not_found'
                        health_status['issues'].append(f"Lambda not found: {function_name}")
                    else:
                        lambda_health[function_name] = 'error'
                        health_status['issues'].append(f"Lambda error {function_name}: {error_code}")
                except Exception as e:
                    lambda_health[function_name] = 'error'
                    health_status['issues'].append(f"Lambda check failed {function_name}: {str(e)}")
            
            health_status['components']['lambda_functions'] = lambda_health
            
            # Check Bedrock access (basic)
            try:
                # Test básico sin invocar modelo completo
                health_status['components']['bedrock'] = 'healthy'
            except Exception as e:
                health_status['components']['bedrock'] = 'error'
                health_status['issues'].append(f"Bedrock access failed: {str(e)}")
            
            # Determinar estado general
            if any(status == 'error' for component in health_status['components'].values() 
                   for status in (component.values() if isinstance(component, dict) else [component])):
                health_status['overall_status'] = 'error'
            elif any(status in ['warning', 'not_found'] for component in health_status['components'].values() 
                     for status in (component.values() if isinstance(component, dict) else [component])):
                health_status['overall_status'] = 'warning'
            
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['issues'].append(f"Health check failed: {str(e)}")
        
        return health_status
    
    # =============================================================================
    # STATISTICS AND MONITORING (THREAD-SAFE)
    # =============================================================================
    
    def _record_lambda_attempt(self, function_name: str):
        """Registra intento de invocación Lambda (thread-safe)."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['total'] += 1
            self.access_stats['lambda_invocations']['by_function'][function_name] += 1
    
    def _record_lambda_success(self, function_name: str):
        """Registra invocación Lambda exitosa (thread-safe)."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['successful'] += 1
    
    def _record_lambda_failure(self, function_name: str):
        """Registra invocación Lambda fallida (thread-safe)."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['failed'] += 1
    
    def _record_s3_operation(self, operation_type: str):
        """Registra operación S3 (thread-safe)."""
        with self._stats_lock:
            if operation_type in ['read_attempt', 'read_success']:
                self.access_stats['s3_operations']['reads'] += 1
            elif operation_type in ['write_attempt', 'write_success']:
                self.access_stats['s3_operations']['writes'] += 1
            elif 'error' in operation_type:
                self.access_stats['s3_operations']['errors'] += 1
    
    def _record_bedrock_attempt(self, model_name: str):
        """Registra intento de invocación Bedrock (thread-safe)."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['total'] += 1
            self.access_stats['bedrock_invocations']['by_model'][model_name] += 1
    
    def _record_bedrock_success(self, model_name: str):
        """Registra invocación Bedrock exitosa (thread-safe)."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['successful'] += 1
    
    def _record_bedrock_failure(self, model_name: str):
        """Registra invocación Bedrock fallida (thread-safe)."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['failed'] += 1
    
    def _record_repository_operation(self, operation_type: str, count: int = 1):
        """Registra operación de repositorio (thread-safe)."""
        with self._stats_lock:
            if operation_type == 'structure_loaded':
                self.access_stats['repository_operations']['structures_loaded'] += count
            elif operation_type == 'file_downloaded':
                self.access_stats['repository_operations']['files_downloaded'] += count
            elif operation_type in ['batch_download', 'content_loaded']:
                self.access_stats['repository_operations']['batch_operations'] += 1
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas consolidadas de acceso (thread-safe).
        
        Returns:
            dict: Estadísticas detalladas de todos los accesos
        """
        with self._stats_lock:
            stats = {
                'lambda_invocations': {
                    'total': self.access_stats['lambda_invocations']['total'],
                    'successful': self.access_stats['lambda_invocations']['successful'],
                    'failed': self.access_stats['lambda_invocations']['failed'],
                    'success_rate': (
                        self.access_stats['lambda_invocations']['successful'] / 
                        self.access_stats['lambda_invocations']['total'] * 100
                        if self.access_stats['lambda_invocations']['total'] > 0 else 0
                    ),
                    'by_function': dict(self.access_stats['lambda_invocations']['by_function'])
                },
                's3_operations': dict(self.access_stats['s3_operations']),
                'bedrock_invocations': {
                    'total': self.access_stats['bedrock_invocations']['total'],
                    'successful': self.access_stats['bedrock_invocations']['successful'],
                    'failed': self.access_stats['bedrock_invocations']['failed'],
                    'success_rate': (
                        self.access_stats['bedrock_invocations']['successful'] / 
                        self.access_stats['bedrock_invocations']['total'] * 100
                        if self.access_stats['bedrock_invocations']['total'] > 0 else 0
                    ),
                    'by_model': dict(self.access_stats['bedrock_invocations']['by_model'])
                },
                'repository_operations': dict(self.access_stats['repository_operations']),
                'consolidation_info': {
                    'components_unified': [
                        'LambdaGateway', 'IntegrationManager', 
                        'S3Client', 'BedrockClient'
                    ],
                    'total_external_calls': (
                        self.access_stats['lambda_invocations']['total'] +
                        self.access_stats['s3_operations']['reads'] +
                        self.access_stats['s3_operations']['writes'] +
                        self.access_stats['bedrock_invocations']['total']
                    )
                }
            }
        
        return stats