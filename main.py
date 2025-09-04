#!/usr/bin/env python3
"""
Script simple para probar la función Lambda localmente.
"""

import json
import os
import time

# Importar la función Lambda
from lambda_function import lambda_handler


class MockContext:
    """Contexto simple para Lambda"""
    aws_request_id = f"test-{int(time.time())}"
    function_name = "validation-pipeline-test"


def test_lambda():
    """Prueba la Lambda con diferentes eventos"""
    
    # Eventos de prueba
    events = {
        'complete': {
            'repository_url': 'https://github.com/BancoPopular/iib-fcd-SrvPruebasRevCruSoap_Fcd-middleware-esql',
            'branch': 'feature/test',
            'report_title': 'Reporte de Validación de Estructura y Contenido'
        },
        # 'complete': {
        #     'repository_url': 'https://github.com/JuanRamosDeantonio/int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql',
        #     'branch': 'main',
        #     'report_title': 'Reporte de Validación de Estructura y Contenido'
        # },
        # 'minimal': {
        #     'repository_url': 'https://github.com/JuanRamosDeantonio/SrvBillAgreementStandardPaymentREST'
        # },
        # 'error': {
        #     'branch': 'dev'  # Sin repository_url
        # }
    }
    
    # Ejecutar cada prueba
    for name, event in events.items():
        print(f"\n{'='*50}")
        print(f"🧪 PRUEBA: {name}")
        print(f"Event: {json.dumps(event, indent=2)}")
        print(f"{'='*50}")
        
        try:
            start = time.time()
            result = lambda_handler(event, MockContext())
            duration = time.time() - start
            
            status = result['statusCode']
            body = json.loads(result['body'])
            
            print(f"⏱️ Tiempo: {duration:.1f}s")
            print(f"📊 Status: {status}")
            
            if status == 200:
                print("✅ ÉXITO")
                summary = body.get('pipeline_summary', {})
                print(f"Prompts: {summary.get('prompts_count', 0)}")
                print(f"Reglas: {summary.get('rules_count', 0)}")
            else:
                print("❌ ERROR")
                print(f"Mensaje: {body.get('error_message', 'N/A')}")
                
        except Exception as e:
            print(f"💥 EXCEPCIÓN: {e}")


def main():
    print("🚀 PRUEBAS LAMBDA LOCAL")
    # load_env()
    test_lambda()
    print(f"\n🏁 TERMINADO")


if __name__ == "__main__":
    main()