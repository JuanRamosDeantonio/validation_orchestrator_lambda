"""
main.py - Local testing actualizado para LambdaGateway
"""

import json
import argparse
import sys
import asyncio
import signal
import time
from typing import Dict, Any

from lambda_function import lambda_handler
from app.utils import setup_logger, validate_repository_url, format_repository_name
from app.lambda_gateway import LambdaGateway, RepositoryConfig

# Configurar logging
logger = setup_logger(__name__)

# Flag para manejo de interrupción
interrupted = False

def signal_handler(signum, frame):
    """Maneja señales de interrupción."""
    global interrupted
    interrupted = True
    print("\n\n⚠️  Interrupción recibida. Cancelando operación...")
    sys.exit(1)

def create_mock_event(repository_url: str, user_name: str, user_email: str) -> Dict[str, Any]:
    """
    Crea un evento mock que simula el formato de API Gateway.
    Actualizado para incluir validación de URL de repositorio.
    
    Args:
        repository_url (str): URL del repositorio
        user_name (str): Nombre del usuario
        user_email (str): Email del usuario
        
    Returns:
        dict: Evento simulado
        
    Raises:
        ValueError: Si la URL del repositorio no es válida
    """
    # Validar URL del repositorio antes de crear el evento
    url_validation = validate_repository_url(repository_url)
    if not url_validation['valid']:
        raise ValueError(f"Invalid repository URL: {url_validation['error']}")
    
    print(f"✅ Repository URL validation passed:")
    print(f"   Provider: {url_validation['provider']}")
    print(f"   Owner: {url_validation['owner']}")
    print(f"   Repo: {url_validation['repo']}")
    
    return {
        'body': json.dumps({
            'repository_url': repository_url,
            'user_name': user_name,
            'user_email': user_email
        }),
        'headers': {
            'Content-Type': 'application/json'
        },
        'httpMethod': 'POST',
        'path': '/validate'
    }

def create_mock_context():
    """
    Crea un contexto mock para simular el Lambda context
    
    Returns:
        object: Contexto simulado
    """
    class MockContext:
        def __init__(self):
            self.function_name = 'repository-validator-local'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:local:123456789012:function:repository-validator-local'
            self.memory_limit_in_mb = 512
            self.aws_request_id = f'local-test-{int(time.time())}'
            self.log_group_name = '/aws/lambda/repository-validator-local'
            self.log_stream_name = f'local-test-stream-{int(time.time())}'
            self._remaining_time = 900000  # 15 minutos en ms
            
        def get_remaining_time_in_millis(self):
            return max(0, self._remaining_time)
    
    return MockContext()

def safe_input(prompt, timeout=300):
    """
    Input con timeout para evitar colgarse.
    
    Args:
        prompt: Mensaje a mostrar
        timeout: Timeout en segundos
        
    Returns:
        str: Input del usuario
    """
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except Exception as e:
        logger.error(f"Error en input: {str(e)}")
        return ""

async def interactive_mode():
    """
    Modo interactivo mejorado con validación de repositorio y LambdaGateway testing.
    """
    print("=== Modo Interactivo - Validador de Repositorios (LambdaGateway) ===\n")
    
    try:
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, signal_handler)
        
        # Entrada con validación mejorada
        repository_url = safe_input("Ingresa la URL del repositorio (ej: https://github.com/owner/repo): ")
        if not repository_url:
            print("❌ URL del repositorio es requerida")
            return
        
        # Validar URL inmediatamente
        url_validation = validate_repository_url(repository_url)
        if not url_validation['valid']:
            print(f"❌ URL inválida: {url_validation['error']}")
            return
        
        print(f"✅ Repositorio detectado: {url_validation['provider']} - {url_validation['owner']}/{url_validation['repo']}")
        
        user_name = safe_input("Ingresa el nombre del usuario: ")
        if not user_name:
            print("❌ Nombre del usuario es requerido")
            return
        
        user_email = safe_input("Ingresa el email del usuario: ")
        if not user_email:
            print("❌ Email del usuario es requerido")
            return
        
        # Preguntar si quiere probar solo el gateway
        test_gateway_only = safe_input("¿Probar solo LambdaGateway? (y/N): ").lower() == 'y'
        
        if test_gateway_only:
            await test_lambda_gateway_only(repository_url)
        else:
            await test_full_validation(repository_url, user_name, user_email)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error en modo interactivo: {str(e)}")

async def test_lambda_gateway_only(repository_url: str):
    """
    NUEVO: Prueba solo el LambdaGateway sin ejecutar validación completa.
    
    Args:
        repository_url: URL del repositorio a probar
    """
    print(f"\n🔧 PROBANDO LAMBDA GATEWAY")
    print(f"🔍 Repositorio: {repository_url}")
    print("⏳ Inicializando gateway...\n")
    
    try:
        # Crear gateway y configuración
        gateway = LambdaGateway()
        
        # Crear configuración del repositorio
        url_validation = validate_repository_url(repository_url)
        config = RepositoryConfig(
            provider=url_validation['provider'],
            token="",  # Se puede configurar desde env vars
            owner=url_validation['owner'],
            repo=url_validation['repo'],
            branch="main"
        )
        
        print(f"📋 Configuración creada: {format_repository_name(config)}")
        
        # PASO 1: Health Check
        print("\n1️⃣ Health Check del Gateway...")
        health = gateway.health_check()
        display_health_check(health)
        
        if health['overall_status'] != 'healthy':
            print("⚠️  Gateway no está completamente saludable, pero continuando...")
        
        # PASO 2: Obtener estructura
        print("\n2️⃣ Obteniendo estructura del repositorio...")
        start_time = time.time()
        
        try:
            structure_result = gateway.get_structure(config)
            structure_time = time.time() - start_time
            
            if structure_result.get('success'):
                files = structure_result['structure'].get('files', [])
                print(f"✅ Estructura obtenida en {structure_time:.2f}s")
                print(f"   📁 Archivos encontrados: {len(files)}")
                
                # Mostrar algunos archivos de ejemplo
                if files:
                    print("   📄 Archivos de ejemplo:")
                    for file_path in files[:5]:
                        print(f"      - {file_path}")
                    if len(files) > 5:
                        print(f"      ... y {len(files) - 5} más")
            else:
                print(f"❌ Error obteniendo estructura: {structure_result.get('error')}")
                return
                
        except Exception as e:
            print(f"❌ Error en get_structure: {str(e)}")
            return
        
        # PASO 3: Probar descarga de archivo
        print("\n3️⃣ Probando descarga de archivo...")
        
        files = structure_result['structure'].get('files', [])
        test_file = None
        
        # Buscar un archivo README
        for file_path in files:
            if 'readme' in file_path.lower() or 'README' in file_path:
                test_file = file_path
                break
        
        # Si no hay README, tomar el primer archivo de texto
        if not test_file:
            for file_path in files:
                if any(file_path.lower().endswith(ext) for ext in ['.md', '.txt', '.py', '.js']):
                    test_file = file_path
                    break
        
        if test_file:
            try:
                start_time = time.time()
                download_result = gateway.download_file(config, test_file)
                download_time = time.time() - start_time
                
                if download_result.get('success'):
                    file_data = download_result['file_data']
                    content_size = len(file_data.get('content', ''))
                    print(f"✅ Archivo descargado en {download_time:.2f}s")
                    print(f"   📄 Archivo: {test_file}")
                    print(f"   💾 Tamaño base64: {content_size:,} caracteres")
                    
                    # Si es archivo de texto, intentar conversión
                    if any(test_file.lower().endswith(ext) for ext in ['.docx', '.pdf']):
                        print("\n4️⃣ Probando conversión de archivo...")
                        start_time = time.time()
                        
                        file_name = test_file.split('/')[-1]
                        conversion_result = gateway.read_file_base64(file_name, file_data['content'])
                        conversion_time = time.time() - start_time
                        
                        if conversion_result.get('success'):
                            markdown_size = len(conversion_result['markdown_content'])
                            print(f"✅ Conversión completada en {conversion_time:.2f}s")
                            print(f"   📝 Tamaño markdown: {markdown_size:,} caracteres")
                            print(f"   🔄 Formato original: {conversion_result.get('original_format', 'unknown')}")
                        else:
                            print(f"❌ Error en conversión: {conversion_result.get('error')}")
                    
                else:
                    print(f"❌ Error descargando archivo: {download_result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Error en download_file: {str(e)}")
        else:
            print("⚠️  No se encontraron archivos adecuados para probar descarga")
        
        # PASO 4: Estadísticas finales
        print("\n📊 ESTADÍSTICAS DEL GATEWAY")
        stats = gateway.get_invocation_statistics()
        display_gateway_statistics(stats)
        
    except Exception as e:
        print(f"💥 Error crítico probando gateway: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_full_validation(repository_url: str, user_name: str, user_email: str):
    """
    Prueba validación completa usando el sistema integrado.
    
    Args:
        repository_url: URL del repositorio
        user_name: Nombre del usuario
        user_email: Email del usuario
    """
    print(f"\n🔍 VALIDACIÓN COMPLETA")
    print(f"📁 Repositorio: {repository_url}")
    print(f"👤 Usuario: {user_name} ({user_email})")
    print("⏳ Procesando...\n")
    
    # Ejecutar validación con timeout
    start_time = time.time()
    
    try:
        # Crear evento mock (función sincrónica)
        event = create_mock_event(repository_url, user_name, user_email)
        context = create_mock_context()
        
        # Ejecutar lambda_handler en un executor para no bloquear
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(
                executor, 
                lambda_handler, 
                event, 
                context
            )
        
        execution_time = time.time() - start_time
        print(f"⌚ Tiempo de ejecución: {execution_time:.2f} segundos")
        
        # Mostrar resultados
        display_validation_results(response)
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error durante la validación: {str(e)}")
        print(f"⌚ Tiempo transcurrido: {execution_time:.2f} segundos")
        
        # Mostrar traceback en modo debug
        if '--debug' in sys.argv or '-d' in sys.argv:
            import traceback
            print("\n🔧 DEBUG - Traceback completo:")
            traceback.print_exc()

async def command_line_mode(args):
    """
    Modo de línea de comandos con manejo mejorado de errores y LambdaGateway.
    
    Args:
        args: Argumentos parseados
    """
    print("=== Validador de Repositorios - Modo CLI (LambdaGateway) ===\n")
    
    # Validar argumentos
    if args.test_gateway_only:
        print("🔧 Modo: Solo testing de LambdaGateway")
        print(f"🔍 Repositorio: {args.repository_url}")
    else:
        print("🔍 Modo: Validación completa")
        print(f"📁 Repositorio: {args.repository_url}")
        print(f"👤 Usuario: {args.user_name} ({args.user_email})")
    
    print("⏳ Procesando...\n")
    
    start_time = time.time()
    
    try:
        # Configurar timeout
        signal.signal(signal.SIGINT, signal_handler)
        
        if args.test_gateway_only:
            # Solo probar gateway
            await test_lambda_gateway_only(args.repository_url)
        else:
            # Validación completa
            await test_full_validation(args.repository_url, args.user_name, args.user_email)
        
        execution_time = time.time() - start_time
        print(f"\n⌚ Tiempo total de ejecución: {execution_time:.2f} segundos")
        
        # Exit code basado en resultado
        sys.exit(0)
        
    except KeyboardInterrupt:
        execution_time = time.time() - start_time
        print(f"\n⚠️  Operación cancelada por el usuario después de {execution_time:.2f}s")
        sys.exit(130)  # Exit code para SIGINT
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error durante la ejecución: {str(e)}")
        print(f"⌚ Tiempo transcurrido: {execution_time:.2f} segundos")
        
        if args.debug:
            import traceback
            print("\n🔧 DEBUG - Traceback completo:")
            traceback.print_exc()
        
        sys.exit(1)

def display_health_check(health: Dict[str, Any]):
    """
    NUEVO: Muestra resultados del health check de forma legible.
    
    Args:
        health: Resultado del health check
    """
    status_icons = {
        'healthy': '✅',
        'warning': '⚠️',
        'error': '❌',
        'not_found': '🚫'
    }
    
    print(f"   Estado general: {status_icons.get(health['overall_status'], '❓')} {health['overall_status']}")
    
    if 'lambda_functions' in health:
        print("   Funciones Lambda:")
        for function_name, status in health['lambda_functions'].items():
            icon = status_icons.get(status, '❓')
            print(f"      {icon} {function_name}: {status}")
    
    if health.get('issues'):
        print("   Issues encontrados:")
        for issue in health['issues']:
            print(f"      ⚠️  {issue}")

def display_gateway_statistics(stats: Dict[str, Any]):
    """
    NUEVO: Muestra estadísticas del gateway de forma legible.
    
    Args:
        stats: Estadísticas del gateway
    """
    print(f"   📊 Total invocaciones: {stats['total_invocations']}")
    print(f"   ✅ Exitosas: {stats['successful_invocations']}")
    print(f"   ❌ Fallidas: {stats['failed_invocations']}")
    print(f"   📈 Tasa de éxito: {stats['success_rate']:.1f}%")
    
    if stats['invocations_by_function']:
        print("   Por función:")
        for function_name, function_stats in stats['invocations_by_function'].items():
            print(f"      📋 {function_name}:")
            print(f"         Total: {function_stats['total']}")
            print(f"         Exitosas: {function_stats['successful']}")
            print(f"         Fallidas: {function_stats['failed']}")

def display_validation_results(response: Dict[str, Any]):
    """
    Muestra los resultados de la validación de forma legible.
    Actualizada para mostrar información del LambdaGateway.
    
    Args:
        response: Respuesta de la Lambda
    """
    status_code = response.get('statusCode', 500)
    
    try:
        body = json.loads(response.get('body', '{}'))
    except json.JSONDecodeError:
        body = {'message': 'Error parsing response body'}
    
    print("=" * 60)
    print("📋 RESULTADOS DE LA VALIDACIÓN")
    print("=" * 60)
    
    if status_code == 200:
        validation_result = body.get('validation_result', False)
        message = body.get('message', 'Sin mensaje')
        
        if validation_result:
            print("✅ VALIDACIÓN EXITOSA")
            print(f"📝 Mensaje: {message}")
        else:
            print("❌ VALIDACIÓN FALLIDA")
            print(f"📝 Mensaje: {message}")
            
        # Mostrar metadata si existe
        metadata = body.get('metadata', {})
        if metadata:
            print("\n📊 METADATA:")
            execution_id = metadata.get('execution_id')
            request_id = metadata.get('request_id')
            provider = metadata.get('repository_provider')
            
            if execution_id:
                print(f"   🆔 ID de Ejecución: {execution_id}")
            if request_id:
                print(f"   📞 ID de Request: {request_id}")
            if provider:
                print(f"   🏪 Proveedor: {provider}")
            
            # NUEVO: Mostrar estadísticas del gateway
            gateway_stats = metadata.get('lambda_gateway_stats')
            if gateway_stats:
                print("\n🔧 ESTADÍSTICAS DEL GATEWAY:")
                print(f"   📊 Invocaciones totales: {gateway_stats.get('total_invocations', 0)}")
                print(f"   ✅ Tasa de éxito: {gateway_stats.get('success_rate', 0):.1f}%")
    
    elif status_code == 400:
        print("⚠️  ERROR DE PARÁMETROS")
        print(f"📝 Mensaje: {body.get('message', 'Parámetros inválidos')}")
    
    elif status_code == 408:
        print("⏰ TIMEOUT")
        print(f"📝 Mensaje: {body.get('message', 'Operación timeout')}")
    
    elif status_code == 500:
        print("💥 ERROR DEL SISTEMA")
        print(f"📝 Mensaje: {body.get('message', 'Error interno del servidor')}")
    
    else:
        print(f"🤔 CÓDIGO DE ESTADO DESCONOCIDO: {status_code}")
        print(f"📝 Mensaje: {body.get('message', 'Respuesta inesperada')}")
    
    print("=" * 60)
    
    # Mostrar respuesta completa en modo debug
    if '--debug' in sys.argv or '-d' in sys.argv:
        print("\n🔧 DEBUG - Respuesta completa:")
        print(json.dumps(response, indent=2, ensure_ascii=False))

def validate_environment():
    """
    Valida que el entorno esté configurado correctamente para LambdaGateway.
    Actualizada para incluir validaciones específicas del gateway.
    
    Returns:
        bool: True si el entorno es válido
    """
    import os
    
    required_vars = ['AWS_REGION', 'S3_BUCKET', 'GET_REPO_STRUCTURE_LAMBDA', 'FILE_READER_LAMBDA']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # Variables opcionales pero recomendadas
    optional_vars = ['GITHUB_TOKEN', 'BEDROCK_REGION']
    missing_optional = []
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno requeridas faltantes: {', '.join(missing_vars)}")
        return False
    
    if missing_optional:
        print(f"⚠️  Variables opcionales faltantes: {', '.join(missing_optional)}")
        print("💡 Estas variables mejoran la funcionalidad pero no son críticas.")
    
    print("✅ Configuración del entorno validada correctamente")
    return True

def main():
    """
    Función principal actualizada con soporte para LambdaGateway.
    """
    parser = argparse.ArgumentParser(
        description='Local testing para el validador de repositorios con LambdaGateway',
        epilog='Ejemplos:\n'
               '  python main.py --interactive\n'
               '  python main.py -r https://github.com/user/repo -n "Juan Pérez" -e juan@example.com\n'
               '  python main.py -r https://github.com/user/repo --test-gateway-only\n'
               '  python main.py -r https://github.com/user/repo -n "Juan Pérez" -e juan@example.com --debug',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Grupo para modo interactivo
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Ejecutar en modo interactivo'
    )
    
    # Argumentos para modo CLI
    parser.add_argument(
        '--repository-url', '-r',
        type=str,
        help='URL del repositorio a validar'
    )
    
    parser.add_argument(
        '--user-name', '-n',
        type=str,
        help='Nombre del usuario'
    )
    
    parser.add_argument(
        '--user-email', '-e',
        type=str,
        help='Email del usuario'
    )
    
    # NUEVO: Opciones específicas para LambdaGateway
    parser.add_argument(
        '--test-gateway-only',
        action='store_true',
        help='Probar solo LambdaGateway sin validación completa'
    )
    
    # Opciones adicionales
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Mostrar información de debug'
    )
    
    parser.add_argument(
        '--validate-env',
        action='store_true',
        help='Solo validar configuración del entorno'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Repository Validator with LambdaGateway v2.0.0'
    )
    
    try:
        args = parser.parse_args()
        
        # Solo validar entorno si se solicita
        if args.validate_env:
            is_valid = validate_environment()
            sys.exit(0 if is_valid else 1)
        
        # Validar entorno antes de proceder
        if not validate_environment():
            print("🚨 Continuando con configuración por defecto...")
        
        # Determinar modo de ejecución
        if args.interactive:
            asyncio.run(interactive_mode())
        elif args.test_gateway_only and args.repository_url:
            # NUEVO: Modo solo gateway
            asyncio.run(command_line_mode(args))
        elif args.repository_url and args.user_name and args.user_email:
            # Modo CLI completo
            asyncio.run(command_line_mode(args))
        else:
            print("❌ Opciones insuficientes. Usa --interactive o proporciona todos los parámetros requeridos.")
            print("💡 Usa --help para ver todas las opciones disponibles.")
            print("\n🚀 Ejecutando en modo interactivo por defecto...\n")
            asyncio.run(interactive_mode())
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error crítico en main: {str(e)}")
        if '--debug' in sys.argv or '-d' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()