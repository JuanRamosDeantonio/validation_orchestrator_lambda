"""
lambda_function.py - ULTRA SIMPLE - Validador de Repositorios
¿Qué hace? Recibe una URL de repositorio y dice si cumple las reglas o no.
"""

import json
import logging
import asyncio
from app.shared import setup_logger
from app.orchestrator import ValidationOrchestrator

# 📝 Configurar logs para debug
logger = setup_logger(__name__)

# =============================================================================
# 🎯 FUNCIÓN PRINCIPAL - PUNTO DE ENTRADA
# =============================================================================

def lambda_handler(event, context):
    """
    🚪 PUNTO DE ENTRADA - Lo que AWS Lambda ejecuta
    
    Recibe: URL de repositorio + datos del usuario
    Devuelve: ✅ Aprobado o ❌ Rechazado + explicación
    """
    
    # 📋 Log básico
    logger.info(f"🚀 Nueva validación iniciada - ID: {context.aws_request_id}")
    
    try:
        # 📥 PASO 1: ¿Qué me están pidiendo?
        request_data = _extract_request_data(event)
        
        if request_data['error']:
            return _send_error_response(400, request_data['message'])
        
        # 🔍 PASO 2: ¿Es un health check?
        if request_data['is_health_check']:
            return _handle_health_check()
        
        # ✅ PASO 3: Validar el repositorio
        return _validate_repository(
            request_data['repository_url'],
            request_data['user_name'], 
            request_data['user_email'],
            context.aws_request_id
        )
        
    except Exception as error:
        logger.error(f"💥 Error inesperado: {error}")
        return _send_error_response(500, f"Error del sistema: {error}")

# =============================================================================
# 📥 EXTRACCIÓN DE DATOS - ¿Qué me está pidiendo el usuario?
# =============================================================================

def _extract_request_data(event):
    """
    📥 Extrae los datos del request de forma simple
    
    Retorna un diccionario con:
    - error: True/False
    - message: mensaje de error si hay
    - is_health_check: True si es health check
    - repository_url, user_name, user_email: datos del usuario
    """
    
    # 🔍 ¿Es un health check?
    if event.get('httpMethod') == 'GET' or 'health' in str(event).lower():
        return {
            'error': False,
            'is_health_check': True,
            'repository_url': None,
            'user_name': None,
            'user_email': None,
            'message': 'Health check request'
        }
    
    # 📦 Extraer datos del body
    try:
        # ¿El body es un string JSON?
        if isinstance(event.get('body'), str):
            data = json.loads(event['body'])
        # ¿O ya es un diccionario?
        elif isinstance(event.get('body'), dict):
            data = event['body']
        # ¿O viene directo en el event?
        elif 'repository_url' in event:
            data = event
        else:
            return {
                'error': True,
                'message': '❌ No encontré datos en el request',
                'is_health_check': False,
                'repository_url': None,
                'user_name': None,
                'user_email': None
            }
        
        # ✅ Verificar que tengo todo lo necesario
        required_fields = ['repository_url', 'user_name', 'user_email']
        missing_fields = []
        
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'error': True,
                'message': f'❌ Faltan estos datos: {", ".join(missing_fields)}',
                'is_health_check': False,
                'repository_url': None,
                'user_name': None,
                'user_email': None
            }
        
        # 🎉 ¡Todo bien!
        return {
            'error': False,
            'is_health_check': False,
            'repository_url': data['repository_url'].strip(),
            'user_name': data['user_name'].strip(),
            'user_email': data['user_email'].strip(),
            'message': 'Datos extraídos correctamente'
        }
        
    except json.JSONDecodeError:
        return {
            'error': True,
            'message': '❌ El JSON está mal formateado',
            'is_health_check': False,
            'repository_url': None,
            'user_name': None,
            'user_email': None
        }
    except Exception as error:
        return {
            'error': True,
            'message': f'❌ Error extrayendo datos: {error}',
            'is_health_check': False,
            'repository_url': None,
            'user_name': None,
            'user_email': None
        }

# =============================================================================
# 🏥 HEALTH CHECK - ¿Está funcionando el sistema?
# =============================================================================

def _handle_health_check():
    """
    🏥 Verifica que el sistema esté funcionando
    
    Retorna: Status del sistema (healthy/unhealthy)
    """
    logger.info("🏥 Ejecutando health check")
    
    try:
        # Crear el orquestador y verificar que funciona
        orchestrator = ValidationOrchestrator()
        
        # Ejecutar health check de forma simple
        health_result = _run_simple_async(orchestrator.health_check())
        
        # ¿Está todo bien?
        if health_result['overall_status'] == 'healthy':
            status_code = 200
            message = "✅ Sistema funcionando correctamente"
        else:
            status_code = 503
            message = f"⚠️ Sistema con problemas: {health_result.get('issues', [])}"
        
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': health_result['overall_status'],
                'message': message,
                'timestamp': health_result['timestamp'],
                'details': health_result
            }, ensure_ascii=False)
        }
        
    except Exception as error:
        logger.error(f"💥 Error en health check: {error}")
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': f'❌ Health check falló: {error}'
            })
        }

# =============================================================================
# 🔍 VALIDACIÓN PRINCIPAL - El corazón del sistema
# =============================================================================

def _validate_repository(repository_url, user_name, user_email, request_id):
    """
    🔍 VALIDACIÓN PRINCIPAL - Aquí pasa la magia
    
    Pasos:
    1. 📥 Descarga el repositorio
    2. 📋 Carga las reglas de validación
    3. 🤖 Usa IA para verificar las reglas
    4. ✅ Decide: ¿Aprueba o rechaza?
    
    Retorna: Respuesta final para el usuario
    """
    logger.info(f"🔍 Validando repositorio: {repository_url}")
    logger.info(f"👤 Usuario: {user_name} ({user_email})")
    
    try:
        # 🎯 Crear el orquestador (el cerebro del sistema)
        orchestrator = ValidationOrchestrator()
        
        # 🚀 Ejecutar la validación completa
        logger.info("🚀 Iniciando proceso de validación...")
        
        validation_result = _run_simple_async(
            orchestrator.validate_repository(repository_url, user_name, user_email)
        )
        
        # 📊 ¿Qué decidió el sistema?
        if validation_result['passed']:
            logger.info("✅ REPOSITORIO APROBADO")
            status_message = "🎉 ¡Repositorio aprobado! Cumple con todas las reglas"
        else:
            logger.info("❌ REPOSITORIO RECHAZADO")
            status_message = f"❌ Repositorio rechazado: {validation_result['message']}"
        
        # 📤 Enviar respuesta al usuario
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Para que funcione desde web
            },
            'body': json.dumps({
                # 🎯 Lo más importante primero
                'aprobado': validation_result['passed'],
                'mensaje': status_message,
                
                # 📊 Resumen de resultados
                'resumen': {
                    'reglas_totales': validation_result['summary']['total_rules'],
                    'reglas_criticas_fallidas': validation_result['summary']['critical_failures'],
                    'reglas_medias_fallidas': validation_result['summary']['medium_failures'],
                    'reglas_bajas_fallidas': validation_result['summary']['low_failures'],
                    'tiempo_ejecucion_ms': validation_result['summary']['execution_time_ms']
                },
                
                # 🔧 Información técnica (para desarrolladores)
                'info_tecnica': {
                    'request_id': request_id,
                    'repositorio': repository_url,
                    'usuario': user_name,
                    'usa_servicios_reales': True,
                    'detalles': validation_result['metadata']
                }
            }, ensure_ascii=False)
        }
        
    except asyncio.TimeoutError:
        logger.error("⏰ Validación tomó demasiado tiempo")
        return _send_error_response(408, "⏰ La validación tomó demasiado tiempo. Intenta con un repositorio más pequeño.")
        
    except Exception as error:
        logger.error(f"💥 Error durante validación: {error}")
        return _send_error_response(500, f"💥 Error durante la validación: {error}")

# =============================================================================
# 🔧 UTILIDADES SIMPLES - Funciones de apoyo
# =============================================================================

def _run_simple_async(coroutine):
    """
    🔧 Ejecuta código async de forma simple
    
    ¿Por qué esta función?
    AWS Lambda a veces tiene problemas con async/await.
    Esta función los resuelve automáticamente.
    """
    try:
        # ¿Hay un loop corriendo?
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Sí, crear uno nuevo en un thread separado
            import concurrent.futures
            
            def run_in_new_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coroutine)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_thread)
                return future.result(timeout=840)  # 14 minutos máximo
        else:
            # No, usar el loop actual
            return asyncio.run(coroutine)
            
    except AttributeError:
        # Python viejo, usar método simple
        return asyncio.run(coroutine)

def _send_error_response(status_code, message):
    """
    📤 Envía una respuesta de error al usuario
    
    Formato simple y consistente para todos los errores.
    """
    logger.error(f"📤 Enviando error {status_code}: {message}")
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'aprobado': False,
            'mensaje': message,
            'error': True,
            'codigo_error': status_code
        }, ensure_ascii=False)
    }

