"""
lambda_invoker.py - Cliente para invocación de Lambdas AWS
"""

import json
from pathlib import Path
import time
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

import boto3
from app.models import LambdaResult, MarkdownResponse


from app.config import Config, setup_logger


class LambdaInvoker:
    """Cliente para invocar Lambdas de AWS."""
    
    def __init__(self, config=None):
        self.config = config or Config
        self.logger = setup_logger(self.__class__.__name__)
        self.lambda_client = boto3.client('lambda', region_name=self.config.AWS_REGION)
    
    # =============================================================================
    # MÉTODOS PRINCIPALES
    # =============================================================================
    
    def get_repository_structure(self, repository_url: str, branch: str = None) -> LambdaResult:
        """Obtiene la estructura de un repositorio."""
        branch = branch or self.config.GITHUB_BRANCH
        owner, repo = self._extract_owner_repo(repository_url)

        payload = {
            "operation": "GET_STRUCTURE",
            "provider": "github",
            "config": {
                "token": self.config.GITHUB_TOKEN,
                "owner": owner,
                "repo": repo,
                "branch": branch
            }
        }
        
        return self._invoke_lambda(self.config.GET_REPO_STRUCTURE_LAMBDA, payload)
    
    def read_files(self, file_path: str, repository_url: str, branch: str = None) -> MarkdownResponse:
        """
        Lee y procesa un archivo específico desde un repositorio GitHub y retorna su contenido en Markdown.

        Args:
            file_path: Ruta relativa del archivo dentro del repositorio
            repository_url: URL del repositorio GitHub
            branch: Rama del repositorio (opcional)

        Returns:
            MarkdownResponse: Resultado con el contenido Markdown procesado
        """
        start_time = time.time()

        branch = branch or self.config.GITHUB_BRANCH
        owner, repo = self._extract_owner_repo(repository_url)

        # 1. Descargar archivo en base64
        file_location = self._get_file_reference(file_path, owner, repo, branch)
        if not file_location:
            error_msg = f"No se pudo obtener el contenido del archivo '{file_path}'"
            self.logger.error(f"❌ {error_msg}")
            return MarkdownResponse(success=False, error=error_msg, source="get_file")

        # 2. Convertir a markdown
        markdown_content = self._convert_reference_to_markdown(file_path, file_location)
        if not markdown_content:
            error_msg = f"El archivo '{file_path}' no pudo ser convertido a Markdown"
            self.logger.error(f"❌ {error_msg}")
            return MarkdownResponse(success=False, error=error_msg, source="get_file")

        self.logger.info(f"✅ Archivo '{file_path}' procesado correctamente")

        execution_time = time.time() - start_time
        return MarkdownResponse(
            success=True,
            markdown_content=markdown_content,
            source="get_file",
            execution_time= execution_time
        )
    
    def generate_report(self, report: str, 
                       repo_url : str) -> LambdaResult:
        """Genera un reporte de validación."""
        payload = {
            'report': report,
            'commit_message': f'Analysis made on repository {repo_url}',
            'timestamp': time.time()
        }
        
        return self._invoke_lambda(self.config.REPORT_LAMBDA, payload)
    
    # =============================================================================
    # MÉTODOS DE PROCESAMIENTO DE ARCHIVOS
    # =============================================================================
    
    def _get_file_reference(self, file_path: str, owner: str, repo: str, branch: str) -> Optional[Dict[str,Any]]:
        """
        Descarga el archivo desde GitHub y extrae el contenido codificado en base64.

        Returns:
            Contenido base64 del archivo si fue exitoso, None en caso de error
            
        """
        
        clean_path = file_path.removeprefix(f"{repo}/")
        clean_path, ismarkdown = self._parse_wiki_marker(clean_path)
        payload = {
            "operation": "DOWNLOAD_FILE",
            "provider": "github",
            "config": {
                "token": self.config.GITHUB_TOKEN,
                "owner": owner,
                "repo": repo,
                "branch": branch
            },
            "path": clean_path,
            "ismarkdown": ismarkdown
        }

        result = self._invoke_lambda(self.config.GET_REPO_STRUCTURE_LAMBDA, payload)

        if not result.success:
            self.logger.error(f"❌ Error al descargar archivo desde GitHub: {result.error}")
            return None

        try:
            raw_content = self._get_file_s3_location(result.data)
            return raw_content
        except Exception as e:
            self.logger.error(f"❌ Error procesando respuesta de descarga: {e}")
            return None
        
    def _parse_wiki_marker(path: str) :
        """
        Devuelve el path limpio y si es de wiki usando prefijo '(wiki) '
        """
        path = path.strip()
        if path.lower().startswith("(wiki) "):
            clean_path = path[len("(wiki) "):].strip()
            return clean_path, True
        return path, False
    
    def _get_file_s3_location(self, lambda_data: dict) -> Dict[str, Any]:
        """
        Extrae el contenido de la respuesta de la lambda.
        
        Args:
            lambda_data: Datos retornados por la lambda
            
        Returns:
            Contenido como string
        """
        if not lambda_data:
            return ""
        
        # Buscar contenido en diferentes ubicaciones posibles
        obj_file_location = lambda_data["body"]
        
        return obj_file_location

    def _convert_reference_to_markdown(self, file_path: str, file_location: Dict[str,Any]) -> Optional[str]:
        """
        Convierte un archivo en base64 a formato Markdown utilizando una Lambda especializada.

        Returns:
            Contenido Markdown extraído, None si ocurre un error
        """

        print(f"file location -> {file_location}")
        print(f"tipe of file location -> {type(file_location)}")

        file_location = json.loads(file_location)

        
        file_name = Path(file_path).name
        payload = {
            "file_name": file_name,
            "s3_path": file_location['s3_path'],
            "bucket_name": file_location['bucket_name'],
            "region": Config.AWS_REGION,
            "output_format": "markdown",
            "ai_optimized": "true"
        }

        result = self._invoke_lambda(self.config.FILE_READER_LAMBDA, payload)

        if not result.success:
            self.logger.error(f"❌ Error al convertir archivo a Markdown: {result.error}")
            return None

        try:
            processed_content = self._extract_content_from_result(result.data)
            parsed_result = json.loads(processed_content)
            markdown = parsed_result.get("resultado", "").strip()
            return markdown if markdown else None
        except Exception as e:
            self.logger.error(f"❌ Error procesando respuesta del lector de archivos: {e}")
            return None
    
    # =============================================================================
    # MÉTODOS DE INFRAESTRUCTURA
    # =============================================================================
    
    def _invoke_lambda(self, function_name: str, payload: Dict[str, Any]) -> LambdaResult:
        """Invoca una Lambda y retorna el resultado procesado."""
        start_time = time.time()
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = response['Payload'].read()
            status_code = response.get('StatusCode', 0)
            
            result_data = json.loads(response_payload) if response_payload else None
            
            success = (200 <= status_code < 300 and 
                      result_data is not None and
                      'errorMessage' not in result_data)
            
            execution_time = time.time() - start_time
            
            if success:
                return LambdaResult(
                    success=True,
                    data=result_data,
                    execution_time=execution_time,
                    lambda_name=function_name
                )
            else:
                error_msg = result_data.get('errorMessage', 'Error desconocido') if result_data else 'No response'
                return LambdaResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time,
                    lambda_name=function_name
                )
                
        except Exception as e:
            error_msg = self._format_error_message(e)
            return LambdaResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time,
                lambda_name=function_name
            )
    
    # =============================================================================
    # MÉTODOS UTILITARIOS
    # =============================================================================
    
    def _extract_content_from_result(self, lambda_data: dict) -> str:
        """
        Extrae el contenido de la respuesta de la lambda.
        
        Args:
            lambda_data: Datos retornados por la lambda
            
        Returns:
            Contenido como string
        """
        if not lambda_data:
            return ""
        
        # Buscar contenido en diferentes ubicaciones posibles
        content_keys = ['markdown', 'content', 'structure_markdown', 'body']
        
        for key in content_keys:
            if key in lambda_data:
                return lambda_data[key]
        
        # Si es string directamente
        if isinstance(lambda_data, str):
            return lambda_data
        
        # Fallback
        return str(lambda_data)
    
    def _extract_owner_repo(self, github_url: str) -> Tuple[str, str]:
        """
        Extrae el owner y el nombre del repositorio desde una URL de GitHub.

        Args:
            github_url: URL del repositorio de GitHub

        Returns:
            Tupla con (owner, repo)
        
        Raises:
            ValueError: Si la URL no es válida
        """
        try:
            parsed = urlparse(github_url)
            parts = parsed.path.strip("/").split("/")
            
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                # Remover .git si está presente
                if repo.endswith('.git'):
                    repo = repo[:-4]
                return owner, repo
            else:
                raise ValueError(f"URL inválida de GitHub: {github_url}")
        except Exception as e:
            self.logger.error(f"❌ Error procesando URL de GitHub: {e}")
            raise ValueError(f"URL inválida de GitHub: {github_url}")
    
    def _format_error_message(self, error: Exception) -> str:
        """
        Formatea mensajes de error de manera consistente.
        
        Args:
            error: Excepción capturada
            
        Returns:
            Mensaje de error formateado
        """
        if hasattr(error, 'response') and 'Error' in error.response:
            return f"AWS Error: {error.response['Error']['Code']} - {error.response['Error']['Message']}"
        else:
            return f"Error: {str(error)}"


# =============================================================================
# FUNCIÓN FACTORY
# =============================================================================

def create_lambda_invoker(config=None) -> LambdaInvoker:
    """Crea una instancia de LambdaInvoker."""
    return LambdaInvoker(config)