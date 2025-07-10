"""
main.py - SIMULACIÓN SIMPLE del flujo natural de la Lambda
🎯 Simula exactamente lo que pasa cuando llega un JSON a la lambda
"""

import json
import os
import time
from dataclasses import dataclass

# =============================================================================
# 🔧 CONFIGURACIÓN MÍNIMA
# =============================================================================

# Variables de entorno básicas (ajusta según tu setup)
os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('BEDROCK_REGION', 'us-east-1')
os.environ.setdefault('S3_BUCKET', 'lambda-temporal-documents-ia')
os.environ.setdefault('GET_REPO_STRUCTURE_LAMBDA', 'get_repository_info_lambda')
os.environ.setdefault('FILE_READER_LAMBDA', 'file_reader_lambda')
os.environ.setdefault('GITHUB_TOKEN', '')

# =============================================================================
# 🎭 SIMULACIÓN DEL CONTEXTO AWS LAMBDA
# =============================================================================

@dataclass
class LambdaContext:
    """Simula el contexto que AWS pasa a la lambda"""
    aws_request_id: str = f"test-{int(time.time())}"
    function_name: str = "repository-validator"
    memory_limit_in_mb: int = 1024
    
    def get_remaining_time_in_millis(self):
        return 14 * 60 * 1000  # 14 minutos

# =============================================================================
# 📥 JSON DE ENTRADA - El que recibiría la lambda real
# =============================================================================

# Este es el JSON que normalmente llegaría desde API Gateway
input_json = {
    "httpMethod": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": json.dumps({
        "repository_url": "https://github.com/JuanRamosDeantonio/SrvBillAgreementStandardPaymentREST",
        "user_name": "Juan Desarrollador",
        "user_email": "juan@empresa.com"
    })
}

# =============================================================================
# 🚀 EJECUCIÓN NATURAL
# =============================================================================

def main():
    """🚀 Simula la ejecución natural de la lambda"""
    
    print("🚀 SIMULANDO FLUJO NATURAL DE LA LAMBDA")
    print("=" * 60)
    
    # 📥 Mostrar el JSON de entrada
    print("📥 JSON DE ENTRADA:")
    print(json.dumps(input_json, indent=2, ensure_ascii=False))
    print()
    
    # 🎭 Crear contexto simulado
    context = LambdaContext()
    
    print(f"🎭 CONTEXTO SIMULADO:")
    print(f"   Request ID: {context.aws_request_id}")
    print(f"   Function: {context.function_name}")
    print(f"   Memory: {context.memory_limit_in_mb}MB")
    print()
    
    # ⏱️ Iniciar timing
    start_time = time.time()
    print("⏱️  EJECUTANDO LAMBDA...")
    print("-" * 60)
    
    try:
        # 🎯 AQUÍ PASA LA MAGIA - Importar y ejecutar la lambda
        from lambda_function import lambda_handler
        
        # 🚀 Ejecutar tal como lo haría AWS
        response = lambda_handler(input_json, context)
        
        # ⏱️ Calcular tiempo
        execution_time = time.time() - start_time
        
        print("-" * 60)
        print(f"✅ LAMBDA EJECUTADA EN {execution_time:.2f} SEGUNDOS")
        print()
        
        # 📤 Mostrar respuesta
        print("📤 RESPUESTA DE LA LAMBDA:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print()
        
        # 📊 Resumen simple
        status_code = response.get('statusCode', 'N/A')
        
        if status_code == 200:
            print("🎉 ÉXITO - Lambda ejecutada correctamente")
            
            # Extraer info del body si es JSON
            try:
                body = json.loads(response['body'])
                if 'aprobado' in body:
                    resultado = "✅ APROBADO" if body['aprobado'] else "❌ RECHAZADO"
                    print(f"📋 RESULTADO: {resultado}")
                    print(f"💬 MENSAJE: {body.get('mensaje', 'N/A')}")
            except:
                pass
                
        else:
            print(f"⚠️  STATUS CODE: {status_code}")
            
    except Exception as e:
        execution_time = time.time() - start_time
        print("-" * 60)
        print(f"💥 ERROR DESPUÉS DE {execution_time:.2f} SEGUNDOS")
        print(f"❌ Error: {e}")
        
        # Mostrar stack trace para debug
        import traceback
        print("\n🐛 STACK TRACE:")
        traceback.print_exc()

if __name__ == "__main__":
    main()

