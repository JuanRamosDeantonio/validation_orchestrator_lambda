"""
s3_reader.py - Lector simple de JSON desde S3
"""

import json
import time
import os
import boto3
from app.models import S3Result
from app.config import Config, setup_logger



class S3JsonReader:
    """Lector simple de archivos JSON desde S3."""
    
    def __init__(self, config=None):
        self.config = config or Config
        self.logger = setup_logger(self.__class__.__name__)
        self.s3_client = self._create_s3_client()
    
    def _create_s3_client(self):
        """Crea cliente S3 apropiado según el ambiente."""
        # Detectar si estamos en Lambda
        is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
        
        if is_lambda:
            # En Lambda: usar credenciales del rol automáticamente
            self.logger.info("🔧 Cliente S3 para ambiente Lambda (rol IAM)")
            return boto3.client('s3', region_name=self.config.AWS_REGION)
        else:
            # En local: usar variables de entorno AWS estándar
            self.logger.info("🔧 Cliente S3 para ambiente local (variables de entorno)")
            
            # Verificar que las credenciales estén configuradas
            access_key = self.config.AWS_ACCESS_KEY_ID
            secret_key = self.config.AWS_SECRET_ACCESS_KEY
            
            if access_key and secret_key:
                self.logger.info(f"📋 Usando credenciales AWS para región {self.config.AWS_REGION}")
            else:
                self.logger.warning("⚠️ Variables AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY no encontradas")
            
            # boto3 automáticamente usa las variables de entorno, nosotros solo pasamos la región
            return boto3.client(
                's3',
                region_name=self.config.AWS_REGION,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
            )
    
    def read_rules(self) -> S3Result:
        """Lee el archivo de reglas desde S3."""
        return self.read_json(self.config.S3_BUCKET, self.config.RULES_S3_PATH)
    
    def read_template(self) -> str:
        """Lee el archivo de reglas desde S3."""
        return self.read_content(self.config.S3_BUCKET, self.config.TEMPLATE_PROMPT_S3_PATH)
    
    def read_template_structure(self) -> str:
        """Lee el archivo de reglas desde S3."""
        return self.read_content(self.config.S3_BUCKET, self.config.TEMPLATE_PROMPT_S3_PATH_STRUCTURE)
    
    def read_template_report(self) -> str:
        """Lee el archivo de reglas desde S3."""
        return self.read_content(self.config.S3_BUCKET, self.config.TEMPLATE_PROMPT_S3_PATH_REPORT)
    
    def delete_temporal_data(self) -> S3Result:
        """Elimina data temporal de los archivos en el s3"""
        return self.delete_folder_data_temporal(self.config.S3_BUCKET, 'temporal_data/base64_data')

    def delete_folder_data_temporal(self, bucket: str, folder: str) -> S3Result:

        start_time = time.time()

        try:
            response_objects = self.s3_client.list_objects(Bucket=bucket, Prefix=folder)
            content_response_objects = response_objects['Contents']
            objects_list = list(map(lambda obj : {'Key': obj['Key']}, 
                                    content_response_objects))
            request_obj_delete = {'Objects': objects_list}
            print(f'request para eliminar -> {request_obj_delete}')
            response_delete = self.s3_client.delete_objects(Bucket=bucket, Delete=request_obj_delete)

            execution_time = time.time() - start_time

            return S3Result(
                success=True,
                data=response_delete,
                execution_time=execution_time
            )
        except Exception as e:
            error_msg = self._format_error(e, bucket, key='several')
            self.logger.error(f"❌ {error_msg}")
            
            return S3Result(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time
            )

    
    def read_content(self, bucket: str, key: str) -> S3Result:
        """
        Lee un archivo JSON desde S3.
        
        Args:
            bucket: Nombre del bucket S3
            key: Ruta del archivo en S3
            
        Returns:
            S3Result: Resultado con los datos JSON o error
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"📥 Leyendo s3://{bucket}/{key}")
            
            # Descargar y parsear JSON
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ JSON leído en {execution_time:.2f}s")
            
            return S3Result(
                success=True,
                data=content,
                execution_time=execution_time
            )
            
        except Exception as e:
            error_msg = self._format_error(e, bucket, key)
            self.logger.error(f"❌ {error_msg}")
            
            return S3Result(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time
            )
    
    def read_json(self, bucket: str, key: str) -> S3Result:
        """
        Lee un archivo JSON desde S3.
        
        Args:
            bucket: Nombre del bucket S3
            key: Ruta del archivo en S3
            
        Returns:
            S3Result: Resultado con los datos JSON o error
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"📥 Leyendo s3://{bucket}/{key}")
            
            # Descargar y parsear JSON
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            json_data = json.loads(content)
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ JSON leído en {execution_time:.2f}s")
            
            return S3Result(
                success=True,
                data=json_data,
                execution_time=execution_time
            )
            
        except Exception as e:
            error_msg = self._format_error(e, bucket, key)
            self.logger.error(f"❌ {error_msg}")
            
            return S3Result(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time
            )
    
    def _format_error(self, error: Exception, bucket: str, key: str) -> str:
        """Formatea errores de S3."""
        if hasattr(error, 'response'):
            error_code = error.response['Error']['Code']
            if error_code == 'NoSuchKey':
                return f"Archivo no encontrado: s3://{bucket}/{key}"
            elif error_code == 'NoSuchBucket':
                return f"Bucket no encontrado: {bucket}"
            elif error_code == 'AccessDenied':
                return f"Acceso denegado a s3://{bucket}/{key}"
        
        return f"Error leyendo s3://{bucket}/{key}: {str(error)}"


def create_s3_reader(config=None) -> S3JsonReader:
    """Crea una instancia de S3JsonReader."""
    return S3JsonReader(config)