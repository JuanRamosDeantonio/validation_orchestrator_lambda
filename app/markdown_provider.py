"""
markdown_consumer.py - Consumidor de markdown desde lambdas AWS
"""

import json
from typing import Optional
from dataclasses import dataclass

from app.config import Config, setup_logger
from app.lambda_invoker import create_lambda_invoker, LambdaResult
from app.models import FileEntry, MarkdownResponse



class MarkdownConsumer:
    """
    Consumidor de markdown desde lambdas AWS.
    
    Las lambdas ya generan y retornan el markdown listo.
    Esta clase solo las invoca y retorna el resultado.
    """
    
    def __init__(self, config=None):
        """
        Inicializa el consumidor.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or Config
        self.logger = setup_logger(self.__class__.__name__)
        self.lambda_invoker = create_lambda_invoker(config)
        
        self.logger.info("🚀 MarkdownConsumer inicializado")
    
    def get_repository_structure_markdown(self, repository_url: str) -> MarkdownResponse:
        """
        Obtiene el markdown de la estructura del repositorio.
        
        La lambda GET_REPO_STRUCTURE_LAMBDA retorna directamente el markdown
        de la estructura de archivos y directorios.
        
        Args:
            repository_url: URL del repositorio
            branch: Rama a analizar (opcional)
            
        Returns:
            MarkdownResponse: Respuesta con el markdown de la estructura
        """

        
        self.logger.info(f"📂 Obteniendo estructura markdown de {repository_url}")
        
        # Invocar lambda que retorna markdown de estructura
        lambda_result = self.lambda_invoker.get_repository_structure(
            repository_url=repository_url
        )
        
        if lambda_result.success:
            # Extraer markdown del resultado
            content = self._extract_markdown_from_result(lambda_result.data)
            lambda_data = json.loads(content)


            self.logger.info(f"✅ Estructura markdown obtenida en {lambda_result.execution_time:.2f}s")
            
            markdown_content = lambda_data.get("markdown", {})
            files = lambda_data.get("archivos", [])


            return MarkdownResponse(
                success=True,
                markdown_content=markdown_content,
                files=files,
                execution_time=lambda_result.execution_time,
                source="structure"
            )
        else:
            self.logger.error(f"❌ Error obteniendo estructura: {lambda_result.error}")
            
            return MarkdownResponse(
                success=False,
                error=lambda_result.error,
                execution_time=lambda_result.execution_time,
                source="structure"
            )
    
    def get_file_markdown(self, file_path: FileEntry, repository_url: str) -> MarkdownResponse:
        """
        Obtiene el markdown de un archivo específico.
        
        La lambda FILE_READER_LAMBDA retorna directamente el markdown
        del contenido del archivo.
        
        Args:
            file_path: Ruta del archivo en el repositorio
            repository_url: URL del repositorio
            branch: Rama a analizar (opcional)
            
        Returns:
            MarkdownResponse: Respuesta con el markdown del archivo
        """
    
        
        self.logger.info(f"📄 Obteniendo markdown del archivo {file_path}")
        
        # Invocar lambda que retorna markdown del archivo
        result = self.lambda_invoker.read_files(
            file_path,  # Lista con un solo archivo
            repository_url=repository_url,
        )
        
        if result.success:
            
            
            return MarkdownResponse(
                success=True,
                markdown_content= result.markdown_content,
                execution_time=result.execution_time,
                source="file"
            )
        else:
            self.logger.error(f"❌ Error obteniendo archivo {file_path}: {result.error}")
            
            return MarkdownResponse(
                success=False,
                error=result.error,
                execution_time=result.execution_time,
                source="file"
            )
    
    def _extract_markdown_from_result(self, lambda_data: dict) -> str:
        """
        Extrae el contenido markdown de la respuesta de la lambda de estructura.
        
        Args:
            lambda_data: Datos retornados por la lambda
            
        Returns:
            Contenido markdown como string
        """
        if not lambda_data:
            return ""
        
        # Posibles ubicaciones del markdown en la respuesta
        if 'markdown' in lambda_data:
            return lambda_data['markdown']
        elif 'content' in lambda_data:
            return lambda_data['content']
        elif 'structure_markdown' in lambda_data:
            return lambda_data['structure_markdown']
        elif 'body' in lambda_data:
            return lambda_data['body']
        elif isinstance(lambda_data, str):
            # Si la lambda retorna directamente el markdown como string
            return lambda_data
        else:
            # Fallback: convertir a string si no encuentra formato conocido
            return str(lambda_data)
    
    def _extract_file_markdown_from_result(self, lambda_data: dict, 
                                         file_path: str) -> str:
        """
        Extrae el contenido markdown de la respuesta de la lambda de archivos.
        
        Args:
            lambda_data: Datos retornados por la lambda
            file_path: Ruta del archivo solicitado
            
        Returns:
            Contenido markdown del archivo como string
        """
        if not lambda_data:
            return ""
        
        # Si la lambda retorna múltiples archivos
        if 'files' in lambda_data and isinstance(lambda_data['files'], dict):
            file_data = lambda_data['files'].get(file_path, {})
            
            # Buscar markdown en diferentes ubicaciones
            if 'markdown' in file_data:
                return file_data['markdown']
            elif 'content' in file_data:
                return file_data['content']
            elif 'body' in file_data:
                return file_data['body']
        
        # Si retorna directamente el contenido
        elif 'markdown' in lambda_data:
            return lambda_data['markdown']
        elif 'content' in lambda_data:
            return lambda_data['content']
        elif 'body' in lambda_data:
            return lambda_data['body']
        elif isinstance(lambda_data, str):
            # Si la lambda retorna directamente el markdown
            return lambda_data
        
        # Fallback
        return str(lambda_data)


def create_markdown_consumer(config=None) -> MarkdownConsumer:
    """
    Crea una instancia de MarkdownConsumer.
    
    Args:
        config: Configuración opcional
        
    Returns:
        MarkdownConsumer: Instancia lista para usar
    """
    return MarkdownConsumer(config)