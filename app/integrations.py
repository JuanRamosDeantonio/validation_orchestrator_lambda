"""
integrations.py - Fachada simplificada usando LambdaGateway centralizado
"""

import json
import boto3
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.utils import Config, ErrorHandler, setup_logger
from app.models import RuleData
from app.lambda_gateway import LambdaGateway, RepositoryConfig

# Configurar logging
logger = setup_logger(__name__)

class S3Client:
    """
    Cliente para operaciones con Amazon S3.
    """
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
        self.bucket = Config.S3_BUCKET
        
    def read_file(self, key: str) -> str:
        """
        Lee un archivo desde S3.
        
        Args:
            key: Clave del archivo en S3
            
        Returns:
            str: Contenido del archivo
            
        Raises:
            Exception: Si no se puede leer el archivo
        """
        try:
            logger.info(f"Reading file from S3: s3://{self.bucket}/{key}")
            
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            logger.info(f"Successfully read {len(content)} characters from S3")
            return content
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"S3 ClientError reading {key}: {error_code}")
            
            if error_code == 'NoSuchKey':
                raise Exception(f"File not found in S3: {key}")
            elif error_code == 'AccessDenied':
                raise Exception(f"Access denied to S3 file: {key}")
            else:
                raise Exception(f"S3 error reading {key}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Unexpected error reading S3 file {key}: {str(e)}")
            raise Exception(f"Failed to read S3 file {key}: {str(e)}")
    
    def write_file(self, key: str, content: str) -> bool:
        """
        Escribe un archivo a S3.
        
        Args:
            key: Clave del archivo en S3
            content: Contenido a escribir
            
        Returns:
            bool: True si se escribió exitosamente
        """
        try:
            logger.info(f"Writing file to S3: s3://{self.bucket}/{key}")
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            logger.info(f"Successfully wrote {len(content)} characters to S3")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to S3 {key}: {str(e)}")
            return False

class LambdaClient:
    """
    Cliente simplificado que actúa como fachada hacia LambdaGateway.
    Mantiene compatibilidad con el código existente mientras usa el gateway centralizado.
    """
    
    def __init__(self):
        self.lambda_gateway = LambdaGateway()
        self.repository_configs = {}  # Cache de configuraciones por repositorio
        
    async def invoke_async(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca una función Lambda de manera asíncrona.
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Payload a enviar
            
        Returns:
            dict: Respuesta de la función Lambda
        """
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self._invoke_lambda_sync, 
                function_name, 
                payload
            )
        return result
    
    def _invoke_lambda_sync(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compatibilidad con invocaciones lambda directas legacy.
        """
        try:
            logger.info(f"Legacy Lambda invocation: {function_name}")
            
            # Para funciones no migradas al gateway, usar invocación directa
            lambda_client = boto3.client('lambda', region_name=Config.AWS_REGION)
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda returned status {response['StatusCode']}")
            
            response_payload = response['Payload'].read().decode('utf-8')
            result = json.loads(response_payload)
            
            if 'errorMessage' in result:
                raise Exception(f"Lambda error: {result['errorMessage']}")
            
            logger.info(f"Successfully invoked {function_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error invoking {function_name}: {str(e)}")
            return ErrorHandler.handle_lambda_error(e, function_name)
    
    # Métodos actualizados para usar LambdaGateway
    
    async def sync_rules(self) -> Dict[str, Any]:
        """
        Invoca sync_rules_lambda para obtener reglas actualizadas.
        
        Returns:
            dict: Respuesta con reglas sincronizadas
        """
        payload = {
            'action': 'get_latest_rules'
        }
        return await self.invoke_async(Config.SYNC_RULES_LAMBDA, payload)
    
    async def get_repository_structure(self, repository_url: str) -> Dict[str, Any]:
        """
        Obtiene estructura del repositorio usando LambdaGateway.
        
        Args:
            repository_url: URL del repositorio
            
        Returns:
            dict: Estructura del repositorio
        """
        try:
            # Crear configuración del repositorio
            config = self._parse_repository_config(repository_url)
            
            # Usar gateway para obtener estructura
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    self.lambda_gateway.get_structure,
                    config
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting repository structure: {str(e)}")
            return ErrorHandler.handle_lambda_error(e, "get_repository_structure")
    
    async def read_files(self, repository_url: str, file_patterns: List[str]) -> Dict[str, Any]:
        """
        Lee archivos específicos del repositorio usando LambdaGateway.
        
        Args:
            repository_url: URL del repositorio
            file_patterns: Patrones de archivos a leer
            
        Returns:
            dict: Archivos y su contenido
        """
        try:
            config = self._parse_repository_config(repository_url)
            
            # Obtener estructura primero para identificar archivos
            structure_result = await self.get_repository_structure(repository_url)
            if not structure_result.get('success'):
                return structure_result
            
            # Filtrar archivos que coinciden con los patrones
            matching_files = self._filter_files_by_patterns(
                structure_result['structure'].get('files', []),
                file_patterns
            )
            
            # Descargar archivos usando gateway
            files_content = {}
            
            for file_path in matching_files:
                try:
                    # Determinar si necesita conversión especial
                    if self._requires_special_processing(file_path):
                        # Usar download_and_read_file para archivos que necesitan conversión
                        loop = asyncio.get_event_loop()
                        with ThreadPoolExecutor() as executor:
                            file_result = await loop.run_in_executor(
                                executor,
                                self.lambda_gateway.download_and_read_file,
                                config,
                                file_path
                            )
                        
                        if file_result.get('success'):
                            files_content[file_path] = file_result['markdown_content']
                    else:
                        # Descarga directa para archivos de texto
                        loop = asyncio.get_event_loop()
                        with ThreadPoolExecutor() as executor:
                            download_result = await loop.run_in_executor(
                                executor,
                                self.lambda_gateway.download_file,
                                config,
                                file_path
                            )
                        
                        if download_result.get('success'):
                            # Decodificar base64 para archivos de texto
                            import base64
                            content_b64 = download_result['file_data']['content']
                            content_decoded = base64.b64decode(content_b64).decode('utf-8')
                            files_content[file_path] = content_decoded
                            
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {str(e)}")
                    # Continuar con otros archivos
                    continue
            
            return {
                'success': True,
                'files': files_content,
                'repository_url': repository_url,
                'total_files': len(matching_files),
                'processed_files': len(files_content)
            }
            
        except Exception as e:
            logger.error(f"Error reading files: {str(e)}")
            return ErrorHandler.handle_lambda_error(e, "read_files")
    
    async def trigger_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca report_lambda para generar reporte.
        
        Args:
            validation_results: Resultados de validación
            
        Returns:
            dict: Respuesta del reporte
        """
        payload = {
            'validation_results': validation_results
        }
        return await self.invoke_async(Config.REPORT_LAMBDA, payload)
    
    def _parse_repository_config(self, repository_url: str) -> RepositoryConfig:
        """
        Convierte URL de repositorio a RepositoryConfig.
        
        Args:
            repository_url: URL del repositorio (ej: https://github.com/owner/repo)
            
        Returns:
            RepositoryConfig: Configuración parseada
        """
        # Cache por URL
        if repository_url in self.repository_configs:
            return self.repository_configs[repository_url]
        
        try:
            # Parsear URL de GitHub
            if 'github.com' in repository_url:
                parts = repository_url.replace('https://github.com/', '').replace('http://github.com/', '')
                path_parts = parts.split('/')
                
                if len(path_parts) >= 2:
                    owner = path_parts[0]
                    repo = path_parts[1]
                    
                    config = RepositoryConfig(
                        provider="github",
                        token="",  # Se puede configurar desde variables de entorno
                        owner=owner,
                        repo=repo,
                        branch="main"
                    )
                    
                    # Cache para reutilizar
                    self.repository_configs[repository_url] = config
                    return config
            
            # Otros proveedores se pueden agregar aquí
            raise ValueError(f"Formato de URL no soportado: {repository_url}")
            
        except Exception as e:
            logger.error(f"Error parsing repository URL {repository_url}: {str(e)}")
            raise Exception(f"Invalid repository URL: {repository_url}")
    
    def _filter_files_by_patterns(self, all_files: List[str], patterns: List[str]) -> List[str]:
        """
        Filtra archivos que coinciden con los patrones especificados.
        
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
                if fnmatch.fnmatch(file_path, pattern) or pattern in file_path:
                    if file_path not in matching_files:
                        matching_files.append(file_path)
        
        logger.info(f"Found {len(matching_files)} files matching patterns: {patterns}")
        
        return matching_files
    
    def _requires_special_processing(self, file_path: str) -> bool:
        """
        Determina si un archivo requiere procesamiento especial (conversión).
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            bool: True si requiere procesamiento especial
        """
        special_extensions = ['.docx', '.pdf', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
        return any(file_path.lower().endswith(ext) for ext in special_extensions)

class BedrockClient:
    """
    Cliente para interactuar con AWS Bedrock (modelos de IA).
    """
    
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime', 
            region_name=Config.BEDROCK_REGION
        )
        
    async def invoke_model_async(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Invoca un modelo de Bedrock de manera asíncrona.
        
        Args:
            model_name: Nombre del modelo (claude-3-haiku, claude-3-sonnet)
            prompt: Prompt a enviar al modelo
            
        Returns:
            dict: Respuesta del modelo
        """
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self._invoke_model_sync, 
                model_name, 
                prompt
            )
        return result
    
    def _invoke_model_sync(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Invoca un modelo de Bedrock de manera síncrona.
        
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
            
            logger.info(f"Invoking Bedrock model: {model_name} (ID: {model_id})")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
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
                
                logger.info(f"Model {model_name} responded with {len(content)} characters")
                
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
            logger.error(f"Bedrock ClientError with {model_name}: {error_code}")
            
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
            logger.error(f"JSON decode error from Bedrock {model_name}: {str(e)}")
            return ErrorHandler.handle_bedrock_error(e, f"model_{model_name}")
            
        except Exception as e:
            logger.error(f"Unexpected error with Bedrock {model_name}: {str(e)}")
            return ErrorHandler.handle_bedrock_error(e, f"model_{model_name}")
    
    # Métodos específicos para cada modelo
    
    async def invoke_haiku(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Haiku (modelo rápido y económico).
        
        Args:
            prompt: Prompt a enviar
            
        Returns:
            dict: Respuesta del modelo
        """
        return await self.invoke_model_async('claude-3-haiku', prompt)
    
    async def invoke_sonnet(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Sonnet (modelo balanceado).
        
        Args:
            prompt: Prompt a enviar
            
        Returns:
            dict: Respuesta del modelo
        """
        return await self.invoke_model_async('claude-3-sonnet', prompt)

# Clase de fachada para facilitar el uso
class IntegrationManager:
    """
    Manager central para todas las integraciones externas.
    Ahora usa LambdaGateway como backend principal.
    """
    
    def __init__(self):
        self.s3_client = S3Client()
        self.lambda_client = LambdaClient()
        self.bedrock_client = BedrockClient()
        self.lambda_gateway = LambdaGateway()  # Acceso directo al gateway
        
    # Métodos de conveniencia que combinan múltiples integraciones
    
    async def load_rules_and_content(self, repository_url: str, required_files: List[str]) -> Dict[str, Any]:
        """
        Carga reglas y contenido del repositorio en paralelo usando LambdaGateway.
        
        Args:
            repository_url: URL del repositorio
            required_files: Archivos requeridos por las reglas
            
        Returns:
            dict: Reglas y contenido combinados
        """
        try:
            logger.info("Loading rules and repository content in parallel using LambdaGateway")
            
            # Ejecutar en paralelo
            rules_task = self.lambda_client.sync_rules()
            structure_task = self.lambda_client.get_repository_structure(repository_url)
            files_task = self.lambda_client.read_files(repository_url, required_files)
            
            # Esperar resultados
            rules_result, structure_result, files_result = await asyncio.gather(
                rules_task, structure_task, files_task,
                return_exceptions=True
            )
            
            # Verificar errores
            errors = []
            if isinstance(rules_result, Exception):
                errors.append(f"Rules loading failed: {str(rules_result)}")
            if isinstance(structure_result, Exception):
                errors.append(f"Structure loading failed: {str(structure_result)}")
            if isinstance(files_result, Exception):
                errors.append(f"Files loading failed: {str(files_result)}")
            
            if errors:
                raise Exception("; ".join(errors))
            
            return {
                'rules': rules_result,
                'structure': structure_result,
                'files': files_result
            }
            
        except Exception as e:
            logger.error(f"Error loading rules and content: {str(e)}")
            raise e
    
    async def validate_with_optimal_model(self, prompt: str, model_preference: str = 'sonnet') -> Dict[str, Any]:
        """
        Valida usando el modelo óptimo con fallback automático.
        
        Args:
            prompt: Prompt a validar
            model_preference: Modelo preferido ('haiku' o 'sonnet')
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            if model_preference == 'haiku':
                result = await self.bedrock_client.invoke_haiku(prompt)
            else:
                result = await self.bedrock_client.invoke_sonnet(prompt)
            
            if result.get('success'):
                return result
            else:
                # Fallback al otro modelo
                logger.warning(f"Primary model {model_preference} failed, trying fallback")
                fallback_model = 'haiku' if model_preference == 'sonnet' else 'sonnet'
                
                if fallback_model == 'haiku':
                    return await self.bedrock_client.invoke_haiku(prompt)
                else:
                    return await self.bedrock_client.invoke_sonnet(prompt)
                    
        except Exception as e:
            logger.error(f"Error in model validation: {str(e)}")
            return ErrorHandler.handle_bedrock_error(e, f"optimal_model_{model_preference}")
    
    def get_lambda_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gateway y clientes lambda.
        
        Returns:
            dict: Estadísticas combinadas
        """
        return {
            'lambda_gateway_stats': self.lambda_gateway.get_invocation_statistics(),
            'lambda_client_stats': getattr(self.lambda_client, 'invocation_stats', {})
        }