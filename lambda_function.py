"""
lambda_function.py - Entry Point para AWS Lambda (CORREGIDO)
"""

import json
import logging
import asyncio
import sys
import os
from app.orchestrator import ValidationOrchestrator
from app.utils import setup_logger

# Configurar logging
logger = setup_logger(__name__)

def lambda_handler(event, context):
    """
    Entry point para AWS Lambda
    
    Args:
        event: Event de API Gateway con body JSON
        context: Lambda context
        
    Returns:
        dict: Response para API Gateway
    """
    try:
        logger.info(f"Lambda invoked. Request ID: {context.aws_request_id}")
        logger.info(f"Remaining time: {context.get_remaining_time_in_millis()}ms")
        
        # Parsear body del request
        body = _parse_request_body(event)
        
        # Extraer parámetros requeridos
        repository_url = body.get('repository_url')
        user_name = body.get('user_name')
        user_email = body.get('user_email')
        
        # Validar parámetros
        validation_error = _validate_parameters(repository_url, user_name, user_email)
        if validation_error:
            return validation_error
        
        # Ejecutar validación con manejo correcto de async
        try:
            orchestrator = ValidationOrchestrator()
            result = _run_async_validation(orchestrator, repository_url, user_name, user_email)
            
            logger.info(f"Validation completed. Result: {result['passed']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'validation_result': result['passed'],
                    'message': result['message'],
                    'metadata': {
                        'execution_id': result.get('metadata', {}).get('execution_id'),
                        'request_id': context.aws_request_id
                    }
                }, ensure_ascii=False)
            }
            
        except asyncio.TimeoutError:
            logger.error("Validation timed out")
            return _create_error_response(
                408, "Validation timed out. Repository too large or complex."
            )
            
        except Exception as validation_error:
            logger.error(f"Validation failed: {str(validation_error)}", exc_info=True)
            return _create_error_response(
                500, f"Validation failed: {str(validation_error)}"
            )
        
    except Exception as e:
        logger.error(f"Critical error in lambda_handler: {str(e)}", exc_info=True)
        return _create_error_response(
            500, f"System error during validation: {str(e)}"
        )

def _parse_request_body(event):
    """
    Parsea el body del request con manejo robusto de errores.
    
    Args:
        event: Event de Lambda
        
    Returns:
        dict: Body parseado
        
    Raises:
        Exception: Si el body no es válido
    """
    try:
        # Manejar diferentes formatos de event
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        elif 'repository_url' in event:  # Invocación directa
            body = event
        else:
            body = {}
        
        logger.debug(f"Parsed body: {json.dumps(body, default=str)}")
        return body
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        raise Exception("Invalid JSON format in request body")

def _validate_parameters(repository_url, user_name, user_email):
    """
    Valida parámetros requeridos.
    
    Args:
        repository_url: URL del repositorio
        user_name: Nombre del usuario  
        user_email: Email del usuario
        
    Returns:
        dict or None: Error response si hay problemas, None si todo OK
    """
    missing_params = []
    
    if not repository_url or not repository_url.strip():
        missing_params.append('repository_url')
    
    if not user_name or not user_name.strip():
        missing_params.append('user_name')
        
    if not user_email or not user_email.strip():
        missing_params.append('user_email')
    
    if missing_params:
        logger.warning(f"Missing required parameters: {missing_params}")
        return _create_error_response(
            400, f"Missing required parameters: {', '.join(missing_params)}"
        )
    
    # Validación adicional de formato
    if not _is_valid_url(repository_url):
        return _create_error_response(
            400, "Invalid repository URL format"
        )
    
    if not _is_valid_email(user_email):
        return _create_error_response(
            400, "Invalid email format"
        )
    
    return None

def _is_valid_url(url):
    """Validación básica de URL."""
    return (isinstance(url, str) and 
            (url.startswith('http://') or url.startswith('https://')) and
            len(url) > 10)

def _is_valid_email(email):
    """Validación básica de email."""
    return (isinstance(email, str) and 
            '@' in email and 
            '.' in email.split('@')[-1] and
            len(email) > 5)

def _run_async_validation(orchestrator, repository_url, user_name, user_email):
    """
    Ejecuta validación async con manejo correcto del event loop.
    
    Args:
        orchestrator: Instancia del orchestrator
        repository_url: URL del repositorio
        user_name: Nombre del usuario
        user_email: Email del usuario
        
    Returns:
        dict: Resultado de la validación
    """
    try:
        # Intentar obtener el loop actual
        loop = asyncio.get_event_loop()
        
        # Si hay un loop corriendo, usar run_coroutine_threadsafe
        if loop.is_running():
            logger.debug("Event loop is running, using threadsafe execution")
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        orchestrator.validate_repository(repository_url, user_name, user_email)
                    )
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                # Timeout de 14 minutos (Lambda tiene 15 min max)
                return future.result(timeout=840)
        else:
            # Si no hay loop corriendo, usar asyncio.run()
            logger.debug("No event loop running, using asyncio.run()")
            return asyncio.run(
                orchestrator.validate_repository(repository_url, user_name, user_email)
            )
            
    except AttributeError:
        # Python < 3.7 no tiene get_running_loop
        logger.debug("Using asyncio.run() fallback")
        return asyncio.run(
            orchestrator.validate_repository(repository_url, user_name, user_email)
        )

def _create_error_response(status_code, message):
    """
    Crea respuesta de error estandarizada.
    
    Args:
        status_code: Código HTTP
        message: Mensaje de error
        
    Returns:
        dict: Response para API Gateway
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({
            'validation_result': False,
            'message': message,
            'error': True
        }, ensure_ascii=False)
    }

# Función para health check
def health_check_handler(event, context):
    """
    Handler para health checks.
    
    Args:
        event: Event de Lambda
        context: Lambda context
        
    Returns:
        dict: Status del sistema
    """
    try:
        from app.orchestrator import ValidationOrchestrator
        
        orchestrator = ValidationOrchestrator()
        
        # Ejecutar health check async
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                def run_health_check():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(orchestrator.health_check())
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    health_status = executor.submit(run_health_check).result(timeout=30)
            else:
                health_status = asyncio.run(orchestrator.health_check())
        except:
            health_status = asyncio.run(orchestrator.health_check())
        
        status_code = 200 if health_status['overall_status'] == 'healthy' else 503
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': health_status['overall_status'],
                'timestamp': health_status['timestamp'],
                'components': health_status['components'],
                'issues': health_status.get('issues', [])
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': f"Health check failed: {str(e)}"
            })
        }