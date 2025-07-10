"""
repository_access.py - Gestor de acceso a repositorios con detección automática de entorno
Código limpio que funciona tanto en entorno local como en AWS Lambda
"""

import json
import boto3
import os
import time
import threading
import asyncio  # ← FALTABA ESTE IMPORT
from typing import Dict, List, Any
from dataclasses import dataclass
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

from app.shared import setup_logger, Config

logger = setup_logger(__name__)

# =============================================================================
# REPOSITORY ACCESS MANAGER - GESTOR PRINCIPAL DE ACCESO
# =============================================================================

class RepositoryAccessManager:
    """
    Gestor centralizado para todas las operaciones de acceso a recursos externos.
    
    Detecta automáticamente el entorno de ejecución (Lambda vs Local) y configura
    las credenciales AWS apropiadamente. Maneja operaciones con:
    - S3 (lectura/escritura de archivos y JSON)
    - Lambda (invocación de funciones externas)
    - Bedrock (modelos de IA Claude 3)
    - Repositorios (GitHub, GitLab, Bitbucket)
    
    Características:
    - Thread-safe para estadísticas
    - Manejo robusto de errores con reintentos
    - Optimización de costos con modelos apropiados
    - Logging detallado en español para debugging
    """
    
    def __init__(self):
        """
        Inicializa el gestor con detección automática de entorno.
        
        Detecta si está ejecutándose en Lambda o localmente y configura
        las credenciales AWS apropiadamente. En Lambda usa IAM Role,
        en local carga credenciales desde .env file.
        """
        # Detectar si estamos en Lambda usando variables de entorno específicas
        self.is_lambda = bool(
            os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or 
            os.environ.get('_HANDLER')
        )
        
        # Cargar variables de entorno desde .env si estamos en desarrollo local
        if not self.is_lambda:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.info("📁 Cargando credenciales desde archivo .env para desarrollo local")
            except ImportError:
                logger.warning("⚠️ Dotenv no disponible - usando variables de entorno del sistema")
                pass
        
        # Configurar clients AWS según el entorno
        if self.is_lambda:
            # En Lambda: usar IAM Role automáticamente
            logger.info("☁️ Configurando clients AWS para entorno Lambda con IAM Role")
            self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
        else:
            # En local: usar credenciales explícitas desde variables de entorno
            logger.info("💻 Configurando clients AWS para entorno local con credenciales explícitas")
            self.s3_client = boto3.client(
                's3',
                region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                aws_session_token=os.environ.get('AWS_SESSION_TOKEN')  # Para STS tokens temporales
            )
        
        # Clients comunes para ambos entornos
        self.lambda_client = boto3.client('lambda', region_name=Config.AWS_REGION)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=Config.BEDROCK_REGION)
        
        # Inicializar estadísticas thread-safe para monitoreo
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
        
        environment_name = 'Lambda' if self.is_lambda else 'Local'
        logger.debug(f"🚀 RepositoryAccessManager inicializado - Entorno: {environment_name}")
    
    # =============================================================================
    # OPERACIONES S3 - Lectura y escritura de archivos
    # =============================================================================
    
    def read_s3_file(self, key: str) -> str:
        """
        Lee un archivo desde S3 con manejo robusto de errores.
        
        Args:
            key: Ruta del archivo en el bucket S3
            
        Returns:
            str: Contenido del archivo como string UTF-8
            
        Raises:
            Exception: Si el archivo no existe, no hay permisos, o hay errores de conectividad
        """
        try:
            logger.debug(f"📖 Leyendo archivo S3: s3://{Config.S3_BUCKET}/{key}")
            
            # Registrar intento de lectura para estadísticas
            self._record_s3_operation('read_attempt')
            
            # Realizar la operación de lectura
            response = self.s3_client.get_object(Bucket=Config.S3_BUCKET, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            # Registrar éxito
            self._record_s3_operation('read_success')
            
            logger.debug(f"✅ Lectura S3 exitosa: {len(content):,} caracteres")
            return content
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self._record_s3_operation('read_error')
            logger.error(f"❌ Error de cliente S3 leyendo {key}: {error_code}")
            
            # Mapear códigos de error AWS a mensajes en español
            if error_code == 'NoSuchKey':
                raise Exception(f"Archivo no encontrado en S3: {key}")
            elif error_code == 'AccessDenied':
                raise Exception(f"Acceso denegado al archivo S3: {key}")
            elif error_code == 'InvalidAccessKeyId':
                raise Exception(f"AWS Access Key ID inválido")
            elif error_code == 'SignatureDoesNotMatch':
                raise Exception(f"AWS Secret Key inválido")
            else:
                raise Exception(f"Error S3 leyendo {key}: {str(e)}")
                
        except Exception as e:
            self._record_s3_operation('read_error')
            logger.error(f"💥 Error general leyendo S3 {key}: {str(e)}")
            raise Exception(f"Falló la lectura del archivo S3 {key}: {str(e)}")
    
    def write_s3_file(self, key: str, content: str) -> bool:
        """
        Escribe un archivo a S3 con configuración UTF-8.
        
        Args:
            key: Ruta donde guardar el archivo en S3
            content: Contenido a escribir como string
            
        Returns:
            bool: True si la escritura fue exitosa, False si falló
        """
        try:
            logger.debug(f"✍️ Escribiendo archivo S3: s3://{Config.S3_BUCKET}/{key}")
            
            # Registrar intento de escritura
            self._record_s3_operation('write_attempt')
            
            # Escribir archivo con encoding UTF-8 y Content-Type apropiado
            self.s3_client.put_object(
                Bucket=Config.S3_BUCKET,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Registrar éxito
            self._record_s3_operation('write_success')
            
            logger.debug(f"✅ Escritura S3 exitosa: {len(content):,} caracteres")
            return True
            
        except Exception as e:
            self._record_s3_operation('write_error')
            logger.error(f"❌ Error escribiendo S3 {key}: {str(e)}")
            return False
    
    def read_json_from_s3(self, key: str) -> Dict[str, Any]:
        """
        Lee y parsea un archivo JSON desde S3.
        
        Args:
            key: Ruta del archivo JSON en S3
            
        Returns:
            dict: Contenido JSON parseado
            
        Raises:
            Exception: Si el JSON es inválido o hay errores de S3
        """
        try:
            # Leer contenido como texto
            json_content = self.read_s3_file(key)
            
            # Parsear JSON con manejo de errores
            parsed_json = json.loads(json_content)
            logger.debug(f"📋 JSON parseado exitosamente desde {key}")
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON inválido en {key}: {str(e)}")
            raise Exception(f"Formato JSON inválido en {key}: {str(e)}")
        except Exception as e:
            logger.error(f"💥 Error leyendo JSON desde S3 {key}: {str(e)}")
            raise e
    
    def write_json_to_s3(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Serializa y escribe un diccionario como JSON a S3.
        
        Args:
            key: Ruta donde guardar el archivo JSON
            data: Diccionario a serializar
            
        Returns:
            bool: True si la escritura fue exitosa
        """
        try:
            # Serializar con formato legible y caracteres UTF-8
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Escribir usando el método base
            success = self.write_s3_file(key, json_content)
            
            if success:
                logger.debug(f"📋 JSON escrito exitosamente a {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error escribiendo JSON a S3 {key}: {str(e)}")
            return False
    
    # =============================================================================
    # OPERACIONES LAMBDA - Invocación de funciones externas
    # =============================================================================
    
    async def invoke_lambda_async(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca una función Lambda de manera asíncrona usando ThreadPoolExecutor.
        
        Args:
            function_name: Nombre de la función Lambda a invocar
            payload: Datos a enviar a la función
            
        Returns:
            dict: Respuesta de la función Lambda
        """
        # Obtener el event loop actual
        loop = asyncio.get_event_loop()
        
        # Ejecutar la invocación síncrona en un thread separado
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
        Invoca una función Lambda de manera síncrona con manejo robusto de errores.
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Payload JSON a enviar
            
        Returns:
            dict: Respuesta parseada de la Lambda
            
        Raises:
            Exception: Si la función no existe, hay límites de rate, o errores de ejecución
        """
        try:
            logger.debug(f"⚡ Invocando Lambda {function_name}")
            
            # Registrar intento para estadísticas
            self._record_lambda_attempt(function_name)
            
            # Invocar función con tipo RequestResponse (síncrono)
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Verificar código de respuesta HTTP
            if response['StatusCode'] != 200:
                raise Exception(f"Lambda retornó código de estado {response['StatusCode']}")
            
            # Leer y parsear la respuesta
            response_payload = response['Payload'].read().decode('utf-8')
            result = json.loads(response_payload)
            
            # Verificar si la Lambda reportó un error interno
            if 'errorMessage' in result:
                raise Exception(f"Error interno de Lambda: {result['errorMessage']}")
            
            # Registrar éxito
            self._record_lambda_success(function_name)
            logger.debug(f"✅ Lambda {function_name} invocada exitosamente")
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self._record_lambda_failure(function_name)
            logger.error(f"❌ Error AWS invocando {function_name}: {error_code}")
            
            # Mapear errores comunes de Lambda
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Función Lambda no encontrada: {function_name}")
            elif error_code == 'TooManyRequestsException':
                raise Exception(f"Límite de invocaciones excedido para: {function_name}")
            else:
                raise Exception(f"Error AWS: {str(e)}")
                
        except json.JSONDecodeError as e:
            self._record_lambda_failure(function_name)
            logger.error(f"❌ Error decodificando JSON de {function_name}: {str(e)}")
            raise Exception(f"Respuesta JSON inválida de {function_name}")
            
        except Exception as e:
            self._record_lambda_failure(function_name)
            logger.error(f"💥 Error invocando {function_name}: {str(e)}")
            raise e
    
    # =============================================================================
    # OPERACIONES BEDROCK - Modelos de IA Claude 3
    # =============================================================================
    
    async def invoke_bedrock_model(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Invoca un modelo de Bedrock (Claude 3) de manera asíncrona.
        
        Args:
            model_name: Nombre del modelo ('claude-3-haiku' o 'claude-3-sonnet')
            prompt: Prompt de texto para el modelo
            
        Returns:
            dict: Respuesta del modelo con contenido generado
        """
        # Ejecutar invocación síncrona en thread separado
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
        Invoca un modelo de Bedrock de manera síncrona con configuración optimizada.
        
        Args:
            model_name: Nombre del modelo configurado
            prompt: Texto a enviar al modelo
            
        Returns:
            dict: Respuesta estructurada con éxito/error y contenido
        """
        try:
            # Obtener configuración del modelo desde Config
            model_config = Config.MODEL_CONFIG.get(model_name)
            if not model_config:
                raise Exception(f"Modelo {model_name} no está configurado")
            
            model_id = model_config['model_id']
            logger.debug(f"🤖 Invocando modelo Bedrock: {model_name} (ID: {model_id})")
            
            # Registrar intento para estadísticas y costos
            self._record_bedrock_attempt(model_name)
            
            # Construir payload para API de Claude 3
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Invocar modelo via Bedrock Runtime
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parsear respuesta del modelo
            response_body = json.loads(response['body'].read().decode('utf-8'))
            
            # Extraer contenido generado
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]['text']
                
                # Registrar éxito
                self._record_bedrock_success(model_name)
                logger.debug(f"✅ Modelo {model_name} respondió con {len(content)} caracteres")
                
                return {
                    'success': True,
                    'content': content,
                    'model_used': model_name,
                    'usage': response_body.get('usage', {}),
                    'stop_reason': response_body.get('stop_reason', 'unknown')
                }
            else:
                raise Exception("El modelo no retornó contenido")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self._record_bedrock_failure(model_name)
            logger.error(f"❌ Error de cliente Bedrock con {model_name}: {error_code}")
            
            return {
                'success': False,
                'error': f"Error Bedrock: {error_code}",
                'model_used': model_name
            }
                
        except Exception as e:
            self._record_bedrock_failure(model_name)
            logger.error(f"💥 Error con Bedrock {model_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': model_name
            }
    
    async def invoke_haiku(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Haiku (modelo rápido y económico).
        
        Ideal para:
        - Validaciones estructurales simples
        - Análisis de contenido básico
        - Operaciones que requieren velocidad
        
        Args:
            prompt: Prompt para el modelo
            
        Returns:
            dict: Respuesta del modelo Haiku
        """
        return await self.invoke_bedrock_model('claude-3-haiku', prompt)
    
    async def invoke_sonnet(self, prompt: str) -> Dict[str, Any]:
        """
        Invoca Claude 3 Sonnet (modelo balanceado y más potente).
        
        Ideal para:
        - Análisis semántico complejo
        - Validaciones que requieren comprensión profunda
        - Casos donde la calidad es más importante que la velocidad
        
        Args:
            prompt: Prompt para el modelo
            
        Returns:
            dict: Respuesta del modelo Sonnet
        """
        return await self.invoke_bedrock_model('claude-3-sonnet', prompt)
    
    # =============================================================================
    # OPERACIONES DE REPOSITORIO - Funcionalidad principal
    # =============================================================================
    
    async def load_repository_content(self, repository_config, required_files: List[str]) -> Dict[str, Any]:
        """
        Carga el contenido completo de un repositorio usando lambdas externas.
        
        Proceso:
        1. Obtiene la estructura del repositorio (archivos y directorios)
        2. Filtra archivos que coinciden con los patrones requeridos
        3. Descarga contenido de archivos en lotes paralelos
        4. Procesa archivos especiales (PDF, DOCX, etc.) convirtiéndolos a Markdown
        
        Args:
            repository_config: Configuración del repositorio (provider, owner, repo, etc.)
            required_files: Lista de patrones de archivos requeridos para validación
            
        Returns:
            dict: Estructura completa con metadatos y contenido de archivos
        """
        try:
            logger.info(f"📦 Cargando contenido del repositorio: {repository_config.get_repository_url()}")
            
            # PASO 1: Obtener estructura del repositorio
            structure_result = await self._get_repository_structure(repository_config)
            if not structure_result.get('success'):
                raise Exception(f"Falló obtener estructura: {structure_result.get('error')}")
            
            # PASO 2: Filtrar archivos que coinciden con patrones requeridos
            all_files = structure_result.get('files', [])
            matching_files = self._filter_files_by_patterns(all_files, required_files)
            
            logger.info(f"📁 Archivos: {len(all_files)} totales, {len(matching_files)} coincidentes")
            
            # PASO 3: Descargar contenido de archivos en lotes
            files_content = {}
            if matching_files:
                # Limitar a MAX_BATCH_FILES para evitar timeouts
                files_to_download = matching_files[:Config.MAX_BATCH_FILES]
                
                batch_result = await self._batch_download_files(repository_config, files_to_download)
                
                if batch_result.get('success'):
                    # Procesar cada archivo descargado
                    for file_path, download_data in batch_result['files'].items():
                        if download_data.get('success'):
                            try:
                                # Convertir contenido según tipo de archivo
                                file_content = await self._process_file_content(
                                    download_data['file_data'], file_path
                                )
                                files_content[file_path] = file_content
                            except Exception as e:
                                logger.warning(f"⚠️ Error procesando {file_path}: {str(e)}")
                                continue
            
            # PASO 4: Calcular estadísticas y preparar respuesta
            total_content_size = sum(len(content) for content in files_content.values())
            self._record_repository_operation('content_loaded', len(files_content))
            
            logger.info(f"✅ Contenido cargado: {len(files_content)} archivos, {total_content_size:,} caracteres")
            
            return {
                'success': True,
                'structure': structure_result['structure'],
                'files': files_content,
                'repository_url': repository_config.get_repository_url(),
                'content_statistics': {
                    'total_files': len(files_content),
                    'total_size': total_content_size,
                    'success_rate': (len(files_content) / len(matching_files) * 100) if matching_files else 0
                }
            }
            
        except Exception as e:
            logger.error(f"💥 Error cargando contenido del repositorio: {str(e)}")
            self._record_repository_operation('content_failed', 0)
            return {'success': False, 'error': str(e)}
    
    async def _get_repository_structure(self, config) -> Dict[str, Any]:
        """
        Obtiene la estructura de directorios y archivos del repositorio.
        
        Args:
            config: Configuración del repositorio con provider, owner, repo, etc.
            
        Returns:
            dict: Estructura del repositorio con lista de archivos
        """
        try:
            logger.debug(f"🏗️ Obteniendo estructura del repositorio: {config.get_repository_url()}")
            
            # Construir payload para lambda externa
            payload = {
                "operation": "GET_STRUCTURE",
                "provider": config.provider,
                "config": {
                    "token": config.token,
                    "owner": config.owner,
                    "repo": config.repo,
                    "branch": config.branch
                }
            }
            
            # Invocar lambda externa que maneja APIs de repositorios
            response = await self.invoke_lambda_async(Config.GET_REPO_STRUCTURE_LAMBDA, payload)
            
            # Validar respuesta HTTP
            if response.get('statusCode') != 200:
                raise Exception(f"Lambda reportó fallo: {response.get('error', 'Error desconocido')}")
            
            # Obtener body de la respuesta
            # Obtener body de la respuesta y parsearlo como JSON
            body_raw = response.get('body', '{}')
            if isinstance(body_raw, str):
                import json
                body = json.loads(body_raw)
            else:
                body = body_raw
            
            # Validar éxito en el body
            if not body.get('success', False):
                raise Exception(f"Operación fallida: {body.get('mensaje', 'Error desconocido')}")
            
            # Extraer datos de estructura
            markdown = body.get('markdown', "")
            archivos_lista = body.get('archivos', [])
            metadatos = body.get('metadatos', {})
            
            logger.debug(f"📋 Estructura obtenida: {len(archivos_lista)} archivos, {metadatos.get('total_nodes', 0)} nodos totales")
            
            # Registrar operación exitosa
            self._record_repository_operation('structure_loaded', 1)
            
            return {
                'success': True,
                'structure': markdown,
                'files':archivos_lista,
                'repository_url': config.get_repository_url(),
                'branch': config.branch,
                'provider': body.get('proveedor'),
                'timestamp': body.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estructura del repositorio: {str(e)}")
            self._record_repository_operation('structure_error', 1)
            return {
                'success': False,
                'error': str(e),
                'repository_url': config.get_repository_url() if config else 'unknown'
            }
    
    async def _batch_download_files(self, config, file_paths: List[str]) -> Dict[str, Any]:
        """
        Descarga múltiples archivos en paralelo para optimizar velocidad.
        
        Args:
            config: Configuración del repositorio
            file_paths: Lista de rutas de archivos a descargar
            
        Returns:
            dict: Resultados de descarga con estadísticas de éxito/fallo
        """
        logger.info(f"⬇️ Descarga en lote: {len(file_paths)} archivos")
        
        # Inicializar estructura de resultados
        results = {
            'success': True,
            'total_files': len(file_paths),
            'successful_downloads': 0,
            'failed_downloads': 0,
            'files': {},
            'errors': []
        }
        
        # Crear tareas de descarga paralela
        download_tasks = [
            self._download_single_file(config, file_path) 
            for file_path in file_paths
        ]
        
        try:
            # Ejecutar todas las descargas simultáneamente
            download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Procesar resultados individuales
            for i, result in enumerate(download_results):
                file_path = file_paths[i]
                
                if isinstance(result, Exception):
                    # Error en descarga individual
                    results['failed_downloads'] += 1
                    results['errors'].append({
                        'file_path': file_path, 
                        'error': str(result)
                    })
                elif isinstance(result, dict) and result.get('success'):
                    # Descarga exitosa
                    results['files'][file_path] = result
                    results['successful_downloads'] += 1
                else:
                    # Fallo reportado por la función
                    results['failed_downloads'] += 1
                    results['errors'].append({
                        'file_path': file_path, 
                        'error': result.get('error', 'Error desconocido')
                    })
            
            # Calcular métricas de éxito
            success_rate = results['successful_downloads'] / results['total_files']
            results['success'] = success_rate > 0.5  # Considerar exitoso si >50% se descargó
            results['success_rate'] = success_rate * 100
            
            # Registrar operación
            self._record_repository_operation('batch_download', results['successful_downloads'])
            
            logger.info(f"✅ Descarga completada: {results['successful_downloads']}/{results['total_files']} exitosos")
            
            return results
            
        except Exception as e:
            logger.error(f"💥 Error en descarga en lote: {str(e)}")
            results['success'] = False
            results['errors'].append({'batch_error': str(e)})
            return results
    
    async def _download_single_file(self, config, file_path: str) -> Dict[str, Any]:
        """
        Descarga un archivo individual del repositorio.
        
        Args:
            config: Configuración del repositorio
            file_path: Ruta específica del archivo a descargar
            
        Returns:
            dict: Resultado de la descarga con contenido en base64
        """
        try:
            logger.debug(f"📄 Descargando archivo: {file_path}")
            
            # Construir payload para lambda de descarga
            payload = {
                "action": "DOWNLOAD_FILE",
                "repository_config": {
                    "provider": config.provider,
                    "token": config.token,
                    "owner": config.owner,
                    "repo": config.repo,
                    "branch": config.branch
                },
                "file_path": file_path
            }
            
            # Invocar lambda externa
            response = await self.invoke_lambda_async(Config.GET_REPO_STRUCTURE_LAMBDA, payload)
            
            if not response.get('success', False):
                raise Exception(f"Descarga falló: {response.get('error', 'Archivo no encontrado')}")
            
            file_data = response.get('file_data', {})
            if not file_data.get('content'):
                raise Exception(f"Contenido vacío para: {file_path}")
            
            # Registrar descarga exitosa
            self._record_repository_operation('file_downloaded', 1)
            
            logger.debug(f"✅ Archivo descargado: {file_path}")
            
            return {
                'success': True,
                'file_path': file_path,
                'file_data': file_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error descargando {file_path}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _process_file_content(self, file_data: Dict[str, Any], file_path: str) -> str:
        """
        Procesa el contenido de un archivo, aplicando conversiones si es necesario.
        
        Para archivos de oficina (PDF, DOCX, XLSX, etc.) usa lambda de conversión
        a Markdown. Para archivos de texto, decodifica directamente desde base64.
        
        Args:
            file_data: Datos del archivo con contenido en base64
            file_path: Ruta del archivo para determinar tipo
            
        Returns:
            str: Contenido procesado como texto plano o Markdown
        """
        try:
            content_b64 = file_data.get('content', '')
            if not content_b64:
                return ""
            
            # Verificar si el archivo requiere procesamiento especial
            if self._requires_special_processing(file_path):
                logger.debug(f"🔄 Convirtiendo archivo especial: {file_path}")
                
                file_name = file_path.split('/')[-1]
                conversion_result = await self._convert_file_to_markdown(file_name, content_b64)
                
                if conversion_result.get('success'):
                    return conversion_result['markdown_content']
                else:
                    logger.warning(f"⚠️ Conversión falló para {file_path}, usando decodificación directa")
            
            # Decodificación directa para archivos de texto
            import base64
            decoded_content = base64.b64decode(content_b64).decode('utf-8')
            return decoded_content
            
        except Exception as e:
            logger.error(f"❌ Error procesando {file_path}: {str(e)}")
            return f"[Error decodificando contenido del archivo: {str(e)}]"
    
    async def _convert_file_to_markdown(self, file_name: str, base64_content: str) -> Dict[str, Any]:
        """
        Convierte archivos de oficina (PDF, DOCX, etc.) a Markdown usando lambda externa.
        
        Args:
            file_name: Nombre del archivo con extensión
            base64_content: Contenido del archivo en base64
            
        Returns:
            dict: Resultado de conversión con contenido en Markdown
        """
        try:
            logger.debug(f"📝 Convirtiendo a Markdown: {file_name}")
            
            # Payload para lambda de conversión de archivos
            payload = {
                "file_name": file_name,
                "base64_content": base64_content,
                "output_format": "markdown",
                "optimize_for_ai": True  # Optimizar salida para análisis de IA
            }
            
            # Invocar lambda de conversión
            response = await self.invoke_lambda_async(Config.FILE_READER_LAMBDA, payload)
            
            if not response.get('success', False):
                raise Exception(f"Conversión falló: {response.get('error')}")
            
            markdown_content = response.get('markdown_content', '')
            logger.debug(f"✅ Archivo convertido: {file_name} ({len(markdown_content)} chars)")
            
            return {
                'success': True,
                'file_name': file_name,
                'markdown_content': markdown_content,
                'original_format': response.get('original_format', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo {file_name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _filter_files_by_patterns(self, all_files: List[str], patterns: List[str]) -> List[str]:
        """
        Filtra archivos que coinciden con patrones específicos (soporta wildcards).
        
        Args:
            all_files: Lista completa de archivos del repositorio
            patterns: Patrones a buscar (ej: "*.py", "README.md", "src/*.js")
            
        Returns:
            list: Archivos que coinciden con algún patrón
        """
        import fnmatch
        matching_files = []
        
        for pattern in patterns:
            for file_path in all_files:
                # Soporte para wildcards, coincidencia parcial, y sufijos
                if (fnmatch.fnmatch(file_path, pattern) or 
                    pattern in file_path or 
                    file_path.endswith(pattern)):
                    
                    # Evitar duplicados
                    if file_path not in matching_files:
                        matching_files.append(file_path)
        
        logger.debug(f"🔍 Filtrado: {len(matching_files)} archivos coinciden con {len(patterns)} patrones")
        return matching_files
    
    def _requires_special_processing(self, file_path: str) -> bool:
        """
        Determina si un archivo requiere conversión especial (no es texto plano).
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            bool: True si necesita conversión a Markdown
        """
        # Extensiones que requieren conversión vía lambda externa
        special_extensions = ['.docx', '.pdf', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']
        return any(file_path.lower().endswith(ext) for ext in special_extensions)
    
    # =============================================================================
    # HEALTH CHECK - Verificación de conectividad
    # =============================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realiza verificación de salud de todos los servicios AWS utilizados.
        
        Verifica conectividad con:
        - S3 (bucket de reglas y almacenamiento)
        - Lambda (funciones externas)
        - Bedrock (disponibilidad básica)
        
        Returns:
            dict: Estado de salud con detalles por componente
        """
        health_status = {
            'overall_status': 'healthy',
            'timestamp': time.time(),
            'components': {},
            'issues': []
        }
        
        try:
            logger.info("🏥 Iniciando verificación de salud del sistema")
            
            # VERIFICACIÓN S3: Conectividad básica con el bucket
            try:
                self.s3_client.list_objects_v2(Bucket=Config.S3_BUCKET, MaxKeys=1)
                health_status['components']['s3'] = 'healthy'
                logger.debug("✅ S3: Conectividad verificada")
            except Exception as e:
                health_status['components']['s3'] = 'error'
                health_status['issues'].append(f"Acceso S3 falló: {str(e)}")
                logger.error(f"❌ S3: Error de conectividad - {str(e)}")
            
            # VERIFICACIÓN LAMBDA: Existencia de funciones externas
            lambda_functions = [Config.GET_REPO_STRUCTURE_LAMBDA, Config.FILE_READER_LAMBDA]
            lambda_health = {}
            
            for function_name in lambda_functions:
                try:
                    # Verificar que la función existe (sin invocarla)
                    self.lambda_client.get_function(FunctionName=function_name)
                    lambda_health[function_name] = 'healthy'
                    logger.debug(f"✅ Lambda {function_name}: Función encontrada")
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'ResourceNotFoundException':
                        lambda_health[function_name] = 'not_found'
                        health_status['issues'].append(f"Lambda no encontrada: {function_name}")
                        logger.warning(f"⚠️ Lambda {function_name}: No encontrada")
                    else:
                        lambda_health[function_name] = 'error'
                        health_status['issues'].append(f"Error Lambda {function_name}: {error_code}")
                        logger.error(f"❌ Lambda {function_name}: Error - {error_code}")
                except Exception as e:
                    lambda_health[function_name] = 'error'
                    health_status['issues'].append(f"Verificación Lambda {function_name} falló: {str(e)}")
                    logger.error(f"💥 Lambda {function_name}: Error verificando - {str(e)}")
            
            health_status['components']['lambda_functions'] = lambda_health
            
            # VERIFICACIÓN BEDROCK: Asumimos saludable (verificación básica es costosa)
            health_status['components']['bedrock'] = 'healthy'
            logger.debug("✅ Bedrock: Asumido saludable (verificación básica)")
            
            # DETERMINACIÓN ESTADO GENERAL
            # Error si cualquier componente tiene error
            if any(status == 'error' for component in health_status['components'].values() 
                   for status in (component.values() if isinstance(component, dict) else [component])):
                health_status['overall_status'] = 'error'
            # Warning si algún componente no se encuentra o tiene advertencias
            elif any(status in ['warning', 'not_found'] for component in health_status['components'].values() 
                     for status in (component.values() if isinstance(component, dict) else [component])):
                health_status['overall_status'] = 'warning'
            
            logger.info(f"🏥 Verificación completada: {health_status['overall_status']}")
            
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['issues'].append(f"Verificación de salud falló: {str(e)}")
            logger.error(f"💥 Error en verificación de salud: {str(e)}")
        
        return health_status
    
    async def trigger_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara la generación de reportes usando lambda externa (opcional).
        
        Args:
            report_data: Datos del reporte a generar
            
        Returns:
            dict: Resultado del trigger del reporte
        """
        try:
            logger.info("📊 Disparando generación de reporte")
            
            # Preparar payload con timestamp
            payload = {
                'report_data': report_data, 
                'trigger_timestamp': time.time()
            }
            
            # Verificar si la lambda de reportes está configurada
            if hasattr(Config, 'REPORT_LAMBDA') and Config.REPORT_LAMBDA:
                response = await self.invoke_lambda_async(Config.REPORT_LAMBDA, payload)
                logger.info("✅ Reporte disparado exitosamente")
                return response
            else:
                logger.warning("⚠️ REPORT_LAMBDA no configurado, saltando generación de reporte")
                return {
                    'success': True, 
                    'message': 'Lambda de reportes no configurada'
                }
                
        except Exception as e:
            logger.error(f"❌ Error disparando reporte: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # =============================================================================
    # MÉTODOS DE ESTADÍSTICAS (THREAD-SAFE)
    # =============================================================================
    
    def _record_lambda_attempt(self, function_name: str):
        """Registra intento de invocación Lambda de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['total'] += 1
            self.access_stats['lambda_invocations']['by_function'][function_name] += 1
    
    def _record_lambda_success(self, function_name: str):
        """Registra invocación Lambda exitosa de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['successful'] += 1
    
    def _record_lambda_failure(self, function_name: str):
        """Registra invocación Lambda fallida de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['lambda_invocations']['failed'] += 1
    
    def _record_s3_operation(self, operation_type: str):
        """Registra operación S3 de manera thread-safe."""
        with self._stats_lock:
            if operation_type in ['read_attempt', 'read_success']:
                self.access_stats['s3_operations']['reads'] += 1
            elif operation_type in ['write_attempt', 'write_success']:
                self.access_stats['s3_operations']['writes'] += 1
            elif 'error' in operation_type:
                self.access_stats['s3_operations']['errors'] += 1
    
    def _record_bedrock_attempt(self, model_name: str):
        """Registra intento de invocación Bedrock de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['total'] += 1
            self.access_stats['bedrock_invocations']['by_model'][model_name] += 1
    
    def _record_bedrock_success(self, model_name: str):
        """Registra invocación Bedrock exitosa de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['successful'] += 1
    
    def _record_bedrock_failure(self, model_name: str):
        """Registra invocación Bedrock fallida de manera thread-safe."""
        with self._stats_lock:
            self.access_stats['bedrock_invocations']['failed'] += 1
    
    def _record_repository_operation(self, operation_type: str, count: int = 1):
        """Registra operación de repositorio de manera thread-safe."""
        with self._stats_lock:
            if operation_type == 'structure_loaded':
                self.access_stats['repository_operations']['structures_loaded'] += count
            elif operation_type == 'file_downloaded':
                self.access_stats['repository_operations']['files_downloaded'] += count
            elif operation_type in ['batch_download', 'content_loaded']:
                self.access_stats['repository_operations']['batch_operations'] += 1
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de acceso de manera thread-safe.
        
        Returns:
            dict: Estadísticas detalladas con métricas de éxito y uso
        """
        with self._stats_lock:
            return {
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
                'environment': 'Lambda' if self.is_lambda else 'Local'
            }

# =============================================================================
# CONFIGURACIÓN DE REPOSITORIO - Dataclass simple y eficiente
# =============================================================================

@dataclass
class RepositoryConfig:
    """
    Configuración simple para acceso a repositorios.
    
    Soporta múltiples proveedores (GitHub, GitLab, Bitbucket) con
    configuración unificada de credenciales y parámetros de acceso.
    """
    provider: str = "github"  # Proveedor del repositorio
    token: str = ""          # Token de acceso (opcional para repos públicos)
    owner: str = ""          # Propietario del repositorio
    repo: str = ""           # Nombre del repositorio
    branch: str = "main"     # Rama a analizar
    
    def __post_init__(self):
        """
        Validación post-inicialización para asegurar parámetros mínimos.
        
        Raises:
            ValueError: Si faltan owner o repo (obligatorios)
        """
        if not all([self.owner, self.repo]):
            raise ValueError("Los parámetros owner y repo son obligatorios")
    
    def get_repository_url(self) -> str:
        """
        Construye la URL completa del repositorio según el proveedor.
        
        Returns:
            str: URL del repositorio para mostrar al usuario
        """
        # Mapeo de proveedores a URLs base
        provider_urls = {
            "github": f"https://github.com/{self.owner}/{self.repo}",
            "gitlab": f"https://gitlab.com/{self.owner}/{self.repo}",
            "bitbucket": f"https://bitbucket.org/{self.owner}/{self.repo}"
        }
        
        # Retornar URL específica o genérica
        return provider_urls.get(self.provider, f"{self.provider}://{self.owner}/{self.repo}")