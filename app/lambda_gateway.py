"""
lambda_gateway.py - Gateway centralizado para invocaciones a Lambdas externas
"""

import json
import boto3
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from botocore.exceptions import ClientError, BotoCoreError

from app.utils import Config, ErrorHandler, setup_logger

# Configurar logging
logger = setup_logger(__name__)

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

class LambdaGateway:
    """
    Gateway centralizado para todas las invocaciones a Lambdas externas.
    
    Centraliza la lógica de invocación, manejo de errores, logging y retry.
    Proporciona una interfaz limpia y consistente para el orquestador.
    """
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name=Config.AWS_REGION)
        self.invocation_stats = {
            'total_invocations': 0,
            'successful_invocations': 0,
            'failed_invocations': 0,
            'invocations_by_function': {}
        }
    
    def get_structure(self, config: RepositoryConfig) -> Dict[str, Any]:
        """
        Obtiene la estructura completa del repositorio.
        
        Args:
            config: Configuración del repositorio
            
        Returns:
            dict: Estructura del repositorio con metadatos
            
        Raises:
            Exception: Si falla la invocación o el repositorio no es accesible
        """
        try:
            logger.info(f"Obteniendo estructura del repositorio: {config.get_repository_url()}")
            
            payload = config.build_get_structure_payload()
            
            response = self._invoke_lambda_sync(
                function_name=Config.GET_REPO_STRUCTURE_LAMBDA,
                payload=payload,
                operation="get_structure"
            )
            
            # Validar respuesta
            if not response.get('success', False):
                raise Exception(f"Lambda reportó fallo: {response.get('error', 'Error desconocido')}")
            
            structure_data = response.get('structure', {})
            if not structure_data:
                logger.warning(f"Estructura vacía retornada para {config.get_repository_url()}")
            
            logger.info(f"Estructura obtenida exitosamente: "
                       f"{len(structure_data.get('files', []))} archivos encontrados")
            
            return {
                'success': True,
                'structure': structure_data,
                'repository_url': config.get_repository_url(),
                'branch': config.branch,
                'metadata': response.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estructura de {config.get_repository_url()}: {str(e)}")
            self._record_failed_invocation(Config.GET_REPO_STRUCTURE_LAMBDA)
            return ErrorHandler.handle_lambda_error(e, f"get_structure_{config.repo}")
    
    def download_file(self, config: RepositoryConfig, file_path: str) -> Dict[str, Any]:
        """
        Descarga un archivo específico del repositorio en formato base64.
        
        Args:
            config: Configuración del repositorio
            file_path: Ruta del archivo a descargar
            
        Returns:
            dict: Archivo descargado con contenido base64
            
        Raises:
            Exception: Si falla la descarga o el archivo no existe
        """
        try:
            logger.info(f"Descargando archivo: {file_path} de {config.get_repository_url()}")
            
            payload = config.build_download_file_payload(file_path)
            
            response = self._invoke_lambda_sync(
                function_name=Config.GET_REPO_STRUCTURE_LAMBDA,
                payload=payload,
                operation="download_file"
            )
            
            # Validar respuesta
            if not response.get('success', False):
                raise Exception(f"Descarga falló: {response.get('error', 'Archivo no encontrado')}")
            
            file_data = response.get('file_data', {})
            if not file_data.get('content'):
                raise Exception(f"Contenido vacío para archivo: {file_path}")
            
            logger.info(f"Archivo descargado exitosamente: {file_path} "
                       f"({len(file_data.get('content', ''))} caracteres base64)")
            
            return {
                'success': True,
                'file_path': file_path,
                'file_data': file_data,
                'repository_url': config.get_repository_url(),
                'metadata': {
                    'branch': config.branch,
                    'download_timestamp': response.get('timestamp'),
                    'file_size_base64': len(file_data.get('content', ''))
                }
            }
            
        except Exception as e:
            logger.error(f"Error descargando {file_path} de {config.get_repository_url()}: {str(e)}")
            self._record_failed_invocation(Config.GET_REPO_STRUCTURE_LAMBDA)
            return ErrorHandler.handle_lambda_error(e, f"download_file_{file_path}")
    
    def read_file_base64(self, file_name: str, base64_content: str) -> Dict[str, Any]:
        """
        Convierte archivo base64 a Markdown optimizado para IA.
        
        Args:
            file_name: Nombre del archivo con extensión
            base64_content: Contenido del archivo en base64
            
        Returns:
            dict: Archivo convertido a Markdown optimizado
            
        Raises:
            Exception: Si falla la conversión
        """
        try:
            logger.info(f"Convirtiendo archivo a Markdown: {file_name}")
            
            if not base64_content:
                raise ValueError(f"Contenido base64 vacío para archivo: {file_name}")
            
            payload = RepositoryConfig.build_file_reader_payload(file_name, base64_content)
            
            response = self._invoke_lambda_sync(
                function_name=Config.FILE_READER_LAMBDA,
                payload=payload,
                operation="read_file_base64"
            )
            
            # Validar respuesta
            if not response.get('success', False):
                raise Exception(f"Conversión falló: {response.get('error', 'Error de procesamiento')}")
            
            markdown_content = response.get('markdown_content', '')
            if not markdown_content:
                logger.warning(f"Contenido Markdown vacío para archivo: {file_name}")
            
            logger.info(f"Archivo convertido exitosamente: {file_name} "
                       f"({len(markdown_content)} caracteres Markdown)")
            
            return {
                'success': True,
                'file_name': file_name,
                'markdown_content': markdown_content,
                'original_format': response.get('original_format', 'unknown'),
                'metadata': {
                    'conversion_timestamp': response.get('timestamp'),
                    'markdown_size': len(markdown_content),
                    'base64_size': len(base64_content),
                    'ai_optimized': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error convirtiendo archivo {file_name}: {str(e)}")
            self._record_failed_invocation(Config.FILE_READER_LAMBDA)
            return ErrorHandler.handle_lambda_error(e, f"read_file_{file_name}")
    
    def download_and_read_file(self, config: RepositoryConfig, file_path: str) -> Dict[str, Any]:
        """
        Operación compuesta: descarga y convierte archivo en una sola llamada.
        
        Args:
            config: Configuración del repositorio
            file_path: Ruta del archivo a procesar
            
        Returns:
            dict: Archivo procesado con contenido Markdown
        """
        try:
            logger.info(f"Procesando archivo completo: {file_path}")
            
            # Paso 1: Descargar archivo
            download_result = self.download_file(config, file_path)
            if not download_result.get('success'):
                return download_result
            
            # Paso 2: Convertir a Markdown
            file_data = download_result['file_data']
            file_name = file_path.split('/')[-1]  # Extraer nombre del archivo
            
            conversion_result = self.read_file_base64(file_name, file_data['content'])
            if not conversion_result.get('success'):
                return conversion_result
            
            # Combinar resultados
            return {
                'success': True,
                'file_path': file_path,
                'file_name': file_name,
                'markdown_content': conversion_result['markdown_content'],
                'repository_url': config.get_repository_url(),
                'metadata': {
                    **download_result.get('metadata', {}),
                    **conversion_result.get('metadata', {}),
                    'processing_type': 'download_and_read'
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando archivo completo {file_path}: {str(e)}")
            return ErrorHandler.handle_lambda_error(e, f"process_file_{file_path}")
    
    def batch_download_files(self, config: RepositoryConfig, file_paths: List[str]) -> Dict[str, Any]:
        """
        Descarga múltiples archivos de forma eficiente.
        
        Args:
            config: Configuración del repositorio
            file_paths: Lista de rutas de archivos
            
        Returns:
            dict: Resultados de descarga por archivo
        """
        logger.info(f"Descarga en lote: {len(file_paths)} archivos de {config.get_repository_url()}")
        
        results = {
            'success': True,
            'total_files': len(file_paths),
            'successful_downloads': 0,
            'failed_downloads': 0,
            'files': {},
            'errors': []
        }
        
        for file_path in file_paths:
            try:
                download_result = self.download_file(config, file_path)
                
                if download_result.get('success'):
                    results['files'][file_path] = download_result
                    results['successful_downloads'] += 1
                else:
                    results['failed_downloads'] += 1
                    results['errors'].append({
                        'file_path': file_path,
                        'error': download_result.get('error', 'Error desconocido')
                    })
                    
            except Exception as e:
                results['failed_downloads'] += 1
                results['errors'].append({
                    'file_path': file_path,
                    'error': str(e)
                })
        
        # Determinar éxito general
        success_rate = results['successful_downloads'] / results['total_files']
        results['success'] = success_rate > 0.5  # Al menos 50% exitoso
        results['success_rate'] = success_rate * 100
        
        logger.info(f"Descarga en lote completada: {results['successful_downloads']}/{results['total_files']} exitosos")
        
        return results
    
    def _invoke_lambda_sync(self, function_name: str, payload: Dict[str, Any], 
                           operation: str) -> Dict[str, Any]:
        """
        Invoca una función Lambda de manera síncrona con manejo robusto.
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Payload a enviar
            operation: Nombre de la operación (para logging)
            
        Returns:
            dict: Respuesta parseada de la Lambda
            
        Raises:
            Exception: Si la invocación falla críticamente
        """
        try:
            logger.debug(f"Invocando Lambda {function_name} para operación {operation}")
            
            # Registrar estadísticas
            self._record_invocation_attempt(function_name)
            
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
            self._record_successful_invocation(function_name)
            
            logger.debug(f"Lambda {function_name} invocada exitosamente para {operation}")
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS error invocando {function_name}: {error_code}")
            self._record_failed_invocation(function_name)
            
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Lambda function not found: {function_name}")
            elif error_code == 'TooManyRequestsException':
                raise Exception(f"Rate limit exceeded for: {function_name}")
            else:
                raise Exception(f"AWS error: {str(e)}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from {function_name}: {str(e)}")
            self._record_failed_invocation(function_name)
            raise Exception(f"Invalid JSON response from {function_name}")
            
        except Exception as e:
            logger.error(f"Unexpected error invoking {function_name}: {str(e)}")
            self._record_failed_invocation(function_name)
            raise e
    
    def _record_invocation_attempt(self, function_name: str):
        """Registra intento de invocación."""
        self.invocation_stats['total_invocations'] += 1
        if function_name not in self.invocation_stats['invocations_by_function']:
            self.invocation_stats['invocations_by_function'][function_name] = {
                'total': 0, 'successful': 0, 'failed': 0
            }
        self.invocation_stats['invocations_by_function'][function_name]['total'] += 1
    
    def _record_successful_invocation(self, function_name: str):
        """Registra invocación exitosa."""
        self.invocation_stats['successful_invocations'] += 1
        self.invocation_stats['invocations_by_function'][function_name]['successful'] += 1
    
    def _record_failed_invocation(self, function_name: str):
        """Registra invocación fallida."""
        self.invocation_stats['failed_invocations'] += 1
        self.invocation_stats['invocations_by_function'][function_name]['failed'] += 1
    
    def get_invocation_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de invocaciones del gateway.
        
        Returns:
            dict: Estadísticas detalladas de uso
        """
        total = self.invocation_stats['total_invocations']
        successful = self.invocation_stats['successful_invocations']
        
        return {
            'total_invocations': total,
            'successful_invocations': successful,
            'failed_invocations': self.invocation_stats['failed_invocations'],
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'invocations_by_function': self.invocation_stats['invocations_by_function']
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realiza health check de todas las Lambdas configuradas.
        
        Returns:
            dict: Estado de salud de las Lambdas
        """
        health_status = {
            'overall_status': 'healthy',
            'timestamp': time.time(),
            'lambda_functions': {},
            'issues': []
        }
        
        # Lista de funciones a verificar
        functions_to_check = [
            Config.GET_REPO_STRUCTURE_LAMBDA,
            Config.FILE_READER_LAMBDA
        ]
        
        for function_name in functions_to_check:
            try:
                # Verificar que la función existe
                self.lambda_client.get_function(FunctionName=function_name)
                health_status['lambda_functions'][function_name] = 'healthy'
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    health_status['lambda_functions'][function_name] = 'not_found'
                    health_status['issues'].append(f"Lambda not found: {function_name}")
                else:
                    health_status['lambda_functions'][function_name] = 'error'
                    health_status['issues'].append(f"Error checking {function_name}: {error_code}")
            
            except Exception as e:
                health_status['lambda_functions'][function_name] = 'error'
                health_status['issues'].append(f"Unexpected error checking {function_name}: {str(e)}")
        
        # Determinar estado general
        if any(status != 'healthy' for status in health_status['lambda_functions'].values()):
            health_status['overall_status'] = 'error' if health_status['issues'] else 'warning'
        
        return health_status