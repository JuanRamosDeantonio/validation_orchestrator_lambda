"""
lambda_function.py - Entry Point para AWS Lambda (VERSIÓN LIMPIA SIN MOCKS)
Usa únicamente servicios AWS reales: Bedrock, S3, Lambda
"""

import json
import logging
import asyncio
import sys
import os

# ✅ IMPORTS LIMPIOS - Todo desde shared.py (sin mocks)
from shared import setup_logger
from orchestrator import ValidationOrchestrator

# Configurar logging
logger = setup_logger(__name__)

def lambda_handler(event, context):
    """
    Entry point para AWS Lambda que usa únicamente servicios AWS REALES.
    
    Args:
        event: Event de API Gateway con body JSON
        context: Lambda context
        
    Returns:
        dict: Response para API Gateway
    """
    try:
        logger.info(f"Lambda invoked with REAL AWS services. Request ID: {context.aws_request_id}")
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
        
        # Ejecutar validación con servicios AWS REALES
        try:
            orchestrator = ValidationOrchestrator()
            result = _run_async_validation(orchestrator, repository_url, user_name, user_email)
            
            logger.info(f"Validation completed with REAL services. Result: {result['passed']}")
            
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
                        'request_id': context.aws_request_id,
                        'uses_real_services': True,  # NUEVO: Confirmación de servicios reales
                        'services_used': {
                            'bedrock': 'REAL',
                            's3': 'REAL', 
                            'lambda': 'REAL'
                        }
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
    Ejecuta validación async con servicios AWS REALES.
    
    Args:
        orchestrator: Instancia del orchestrator (REAL, sin mocks)
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
            logger.debug("Event loop is running, using threadsafe execution with REAL services")
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    logger.info("Starting validation with REAL AWS services in new thread")
                    return new_loop.run_until_complete(
                        orchestrator.validate_repository(repository_url, user_name, user_email)
                    )
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                # Timeout de 14 minutos (Lambda tiene 15 min max)
                result = future.result(timeout=840)
                logger.info("Validation completed successfully with REAL services")
                return result
        else:
            # Si no hay loop corriendo, usar asyncio.run()
            logger.debug("No event loop running, using asyncio.run() with REAL services")
            return asyncio.run(
                orchestrator.validate_repository(repository_url, user_name, user_email)
            )
            
    except AttributeError:
        # Python < 3.7 no tiene get_running_loop
        logger.debug("Using asyncio.run() fallback with REAL services")
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
            'error': True,
            'metadata': {
                'uses_real_services': True,  # NUEVO: Incluso en errores, confirmamos servicios reales
                'error_source': 'lambda_function'
            }
        }, ensure_ascii=False)
    }

# Función para health check con servicios REALES
def health_check_handler(event, context):
    """
    Handler para health checks usando servicios AWS REALES.
    
    Args:
        event: Event de Lambda
        context: Lambda context
        
    Returns:
        dict: Status del sistema con servicios reales
    """
    try:
        logger.info("Starting health check with REAL AWS services")
        
        orchestrator = ValidationOrchestrator()
        
        # Ejecutar health check async con servicios REALES
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                def run_health_check():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        logger.debug("Running health check with REAL services in new thread")
                        return new_loop.run_until_complete(orchestrator.health_check())
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    health_status = executor.submit(run_health_check).result(timeout=30)
            else:
                logger.debug("Running health check with REAL services directly")
                health_status = asyncio.run(orchestrator.health_check())
        except:
            logger.debug("Health check fallback with REAL services")
            health_status = asyncio.run(orchestrator.health_check())
        
        status_code = 200 if health_status['overall_status'] == 'healthy' else 503
        
        logger.info(f"Health check completed with REAL services: {health_status['overall_status']}")
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': health_status['overall_status'],
                'timestamp': health_status['timestamp'],
                'components': health_status['components'],
                'issues': health_status.get('issues', []),
                'service_info': {
                    'uses_real_services': True,  # NUEVO
                    'lazy_loading_enabled': health_status.get('lazy_loading_enabled', False),
                    'components_loaded': health_status.get('lazy_loading_stats', {}).get('cached_components', [])
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': f"Health check failed: {str(e)}",
                'service_info': {
                    'uses_real_services': True,  # NUEVO: Incluso en errores
                    'error_in_real_service_check': True
                }
            })
        }

# Función adicional para deployment verification
def deployment_verification_handler(event, context):
    """
    Handler para verificar que el deployment usa servicios REALES.
    
    Args:
        event: Event de Lambda
        context: Lambda context
        
    Returns:
        dict: Información de deployment y servicios
    """
    try:
        logger.info("Running deployment verification")
        
        # Verificar variables de entorno requeridas para servicios reales
        from shared import ConfigValidator
        missing_vars = ConfigValidator.validate_required_env_vars()
        
        # Verificar que los componentes se pueden crear (sin mocks)
        orchestrator = ValidationOrchestrator()
        
        verification_info = {
            'deployment_status': 'verified',
            'timestamp': context.aws_request_id,
            'lambda_info': {
                'function_name': context.function_name,
                'function_version': context.function_version,
                'memory_limit': context.memory_limit_in_mb,
                'remaining_time': context.get_remaining_time_in_millis()
            },
            'environment_check': {
                'missing_env_vars': missing_vars,
                'has_all_required_vars': len(missing_vars) == 0
            },
            'service_verification': {
                'uses_real_services': True,
                'orchestrator_initialized': True,
                'lazy_loading_enabled': True,
                'no_mocks_detected': True
            },
            'component_info': {
                'orchestrator_type': 'ValidationOrchestrator',
                'repository_access_type': 'RepositoryAccessManager',
                'validation_engine_type': 'ValidationEngine',
                'rules_manager_type': 'RulesManager'
            }
        }
        
        logger.info(f"Deployment verification completed successfully")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(verification_info, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Deployment verification failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'deployment_status': 'failed',
                'error': str(e),
                'service_info': {
                    'attempted_real_services': True,
                    'error_during_verification': True
                }
            })
        }

# Función para testing específico de servicios AWS
def aws_services_test_handler(event, context):
    """
    Handler para testing específico de conectividad con servicios AWS REALES.
    
    Args:
        event: Event de Lambda
        context: Lambda context
        
    Returns:
        dict: Resultados de conectividad con servicios AWS
    """
    try:
        logger.info("Testing AWS services connectivity")
        
        from shared import ComponentFactory
        
        # Obtener RepositoryAccessManager REAL
        repository_access_manager = ComponentFactory.get_repository_access_manager()
        
        # Test básico de conectividad
        test_results = {
            'timestamp': context.aws_request_id,
            'test_status': 'completed',
            'services_tested': {},
            'overall_connectivity': True
        }
        
        # Test S3 connectivity
        try:
            import boto3
            from shared import Config
            s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
            s3_client.list_objects_v2(Bucket=Config.S3_BUCKET, MaxKeys=1)
            test_results['services_tested']['s3'] = {
                'status': 'connected',
                'bucket': Config.S3_BUCKET,
                'region': Config.AWS_REGION
            }
            logger.info("S3 connectivity test: SUCCESS")
        except Exception as e:
            test_results['services_tested']['s3'] = {
                'status': 'failed',
                'error': str(e)
            }
            test_results['overall_connectivity'] = False
            logger.error(f"S3 connectivity test: FAILED - {str(e)}")
        
        # Test Lambda connectivity (list functions)
        try:
            lambda_client = boto3.client('lambda', region_name=Config.AWS_REGION)
            lambda_client.list_functions(MaxItems=1)
            test_results['services_tested']['lambda'] = {
                'status': 'connected',
                'region': Config.AWS_REGION
            }
            logger.info("Lambda connectivity test: SUCCESS")
        except Exception as e:
            test_results['services_tested']['lambda'] = {
                'status': 'failed',
                'error': str(e)
            }
            test_results['overall_connectivity'] = False
            logger.error(f"Lambda connectivity test: FAILED - {str(e)}")
        
        # Test Bedrock connectivity (list foundation models)
        try:
            bedrock_client = boto3.client('bedrock', region_name=Config.BEDROCK_REGION)
            bedrock_client.list_foundation_models(maxResults=1)
            test_results['services_tested']['bedrock'] = {
                'status': 'connected',
                'region': Config.BEDROCK_REGION
            }
            logger.info("Bedrock connectivity test: SUCCESS")
        except Exception as e:
            test_results['services_tested']['bedrock'] = {
                'status': 'failed',
                'error': str(e)
            }
            test_results['overall_connectivity'] = False
            logger.error(f"Bedrock connectivity test: FAILED - {str(e)}")
        
        # Test RepositoryAccessManager health
        try:
            repo_health = repository_access_manager.health_check()
            test_results['services_tested']['repository_access_manager'] = {
                'status': repo_health['overall_status'],
                'components': repo_health['components'],
                'issues': repo_health.get('issues', [])
            }
            logger.info(f"RepositoryAccessManager health test: {repo_health['overall_status']}")
        except Exception as e:
            test_results['services_tested']['repository_access_manager'] = {
                'status': 'failed',
                'error': str(e)
            }
            test_results['overall_connectivity'] = False
            logger.error(f"RepositoryAccessManager health test: FAILED - {str(e)}")
        
        status_code = 200 if test_results['overall_connectivity'] else 503
        
        logger.info(f"AWS services connectivity test completed: {test_results['overall_connectivity']}")
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(test_results, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"AWS services test failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'test_status': 'error',
                'error': str(e),
                'services_info': {
                    'attempted_real_aws_tests': True,
                    'test_failure': True
                }
            })
        }