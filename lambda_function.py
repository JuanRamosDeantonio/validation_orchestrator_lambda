import json
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.markdown_rule_binder import MarkdownRuleBinder
from app.markdown_provider import MarkdownConsumer
from app.models import RuleData
from app.s3_reader import S3JsonReader, create_s3_reader
from app.final_rule_grouping import group_rules
from app.prompt_formatter import format_prompts
from app.bedrock_validator import process_prompts_hybrid_optimized as validate_prompts_lambda, generate_report_sync
from app.bedrock_client import run_bedrock_prompt
from app.lambda_invoker import create_lambda_invoker
from app.report_producer import produce_report, report_to_lambda, gather_prompt_results
from app.config import Config

# Configurar logging para Lambda (CloudWatch)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class PipelineConfig:
    """Configuración del pipeline de validación"""
    repository_url: str
    branch: str
    report_title: str = "Reporte de Validación"


class ValidationPipeline:
    """
    Pipeline principal para validación de repositorios usando IA.
    
    Este pipeline procesa un repositorio, aplica reglas de validación,
    genera prompts y obtiene validaciones usando AWS Bedrock.
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.s3_reader = S3JsonReader()
        self.markdown_provider = MarkdownConsumer()
        self.rules: List[RuleData] = []
        self.groups = []
        self.prompts = []
        self.lambda_invoker  = create_lambda_invoker()
        self.bedrock_region = os.environ.get('BEDROCK_REGION', '')
    
    def execute(self) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de validación.
        
        Returns:
            Dict con el resultado de la validación y reporte generado
        """
        try:
            logger.info("🚀 Iniciando pipeline de validación")
            
            # 1. Cargar configuración y reglas
            self._load_validation_rules()
            
            # 2. Procesar estructura del repositorio
            repository_structure = self._process_repository_structure()
            
            # 3. Vincular reglas con archivos
            self._bind_rules_to_files(repository_structure)
            
            # 4. Agrupar reglas y generar prompts
            self._generate_validation_prompts(repository_structure)
            
            # 5. Ejecutar validación con IA
            validation_result = self._execute_ai_validation()

            #produce_report(validation_result)
            #template_report = self.s3_reader.read_template_report()
            prompt_results = gather_prompt_results(validation_result)
            #report_prompt = str(template_report) + prompt_results
            #print(report_prompt)
            #report = run_bedrock_prompt(report_prompt)

            report_to_lambda(prompt_results, self.config.repository_url)

            #print(f'RESULTADOS DE PROMPTS >>>> {validation_result['results']}')
            
            # 6. Generar reporte final
            #report = self._generate_final_report(validation_result)

            #response_report = self.lambda_invoker.generate_report(report, self.config.repository_url)

            #logger.info("Se ejecuta lambda de reporte con respuesta: %s", response_report)
            
            #run_bedrock_prompt("prompt")

            delete_temporal_data = Config.DELETE_TEMPORAL_DATA_FOLDER

            if delete_temporal_data:
                create_s3_reader().delete_temporal_data()

            logger.info("✅ Pipeline ejecutado exitosamente")
            
            return {
                'validation_result': validation_result,
                'report': prompt_results,
                'prompts_count': len(self.prompts),
                'rules_count': len(self.rules)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline: {str(e)}")
            raise
    
    def _load_validation_rules(self) -> None:
        """Carga las reglas de validación desde S3"""
        logger.info("📋 Cargando reglas de validación desde S3")
        
        try:
            s3_response = self.s3_reader.read_rules()
            self.rules = [RuleData(**item) for item in s3_response.data]
            project_type = self._extract_project_type_from_url(self.config.repository_url)

            if project_type:
                self.rules = [rule for rule in self.rules if project_type in rule.projects.split(',')]
            
            logger.info(f"✅ Cargadas {len(self.rules)} reglas de validación")
            
        except Exception as e:
            logger.error(f"❌ Error cargando reglas: {str(e)}")
            raise
    
    def _extract_project_type_from_url(self, url: str) -> str:
    # Ejemplo, se asume que el nombre del repo está al final después del último slash
        repo_name = url.rstrip('/').split('/')[-1]
        parts = repo_name.split('-')
        if len(parts) > 2:
            return parts[2]  # tercer fragmento
        return ''
    
    def _process_repository_structure(self) -> Any:
        """Procesa la estructura del repositorio objetivo"""
        logger.info(f"📁 Procesando estructura del repositorio: {self.config.repository_url}")
        
        try:
            structure = self.markdown_provider.get_repository_structure_markdown(
                self.config.repository_url
            )
            
            logger.info(f"✅ Estructura procesada - {len(structure.files)} archivos encontrados")
            return structure
            
        except Exception as e:
            logger.error(f"❌ Error procesando estructura: {str(e)}")
            raise
    
    def _bind_rules_to_files(self, repository_structure: Any) -> None:
        """Vincula las reglas de validación con los archivos del repositorio"""
        logger.info("🔗 Vinculando reglas con archivos del repositorio")
        
        try:
            runner = MarkdownRuleBinder(self.markdown_provider)
            runner.run(self.rules, repository_structure.files, self.config.repository_url)
            
            # Contar reglas vinculadas
            bound_rules = sum(1 for rule in self.rules if hasattr(rule, 'references') and rule.references)
            runner.get_unique_markdown_paths(self.rules)
            logger.info(f"✅ {bound_rules} reglas vinculadas con archivos")
            
        except Exception as e:
            logger.error(f"❌ Error vinculando reglas: {str(e)}")
            raise
    
    def _generate_validation_prompts(self, repository_structure: Any) -> None:
        """Genera los prompts de validación basados en las reglas agrupadas"""
        logger.info("📝 Generando prompts de validación")
        
        try:
            # Agrupar reglas
            self.groups = group_rules(self.rules)
            logger.info(f"📊 Reglas agrupadas en {len(self.groups)} grupos")
            
            # Cargar plantillas
            template = self.s3_reader.read_template().data
            template_structure = self.s3_reader.read_template_structure().data
            
            # Definir reemplazos para las plantillas
            replacements = self._create_template_replacements(repository_structure)
            
            # Generar prompts
            self.prompts = format_prompts(self.groups, template, replacements, template_structure)
            
            logger.info(f"✅ {len(self.prompts)} prompts generados")
            
        except Exception as e:
            logger.error(f"❌ Error generando prompts: {str(e)}")
            raise
    
    def     _create_template_replacements(self, repository_structure: Any) -> Dict[str, Any]:
        """Crea los reemplazos para las plantillas de prompts"""
        return {
            'ESTRUCTURA': repository_structure.markdown_content,
            'REGLAS_ESTRUCTURA': lambda g: "\n".join([
                f"📄 {r.description}" for r in g.rules if not r.references
            ]),
            'REGLAS_CONTENIDO': lambda g: "\n".join([
                f"📄 {r.description}" for r in g.rules if r.references
            ]),
            'CONTENIDO_ARCHIVOS': lambda g: "\n".join([
                f"\n\nTITULO: {mf.path}\n\nCONTENIDO: {mf.content}" 
                for mf in g.markdownfile if mf
            ]),
        }
    
    def _execute_ai_validation(self) -> Dict[str, Any]:
        """Ejecuta la validación usando IA (AWS Bedrock)"""
        logger.info("🤖 Ejecutando validación con IA")
        
        try:
            # Preparar prompts en formato requerido
            formatted_prompts = self._prepare_prompts_for_validation()
            
            # Ejecutar validación
            if Config.TEMPORAL_BEDROCK_CONFIG:
                result_id = validate_prompts_lambda(formatted_prompts, aws_region=self.bedrock_region,
                                                aws_access_key=Config.BEDROCK_ACCESS_KEY_ID,
                                                aws_secret_key=Config.BEDROCK_SECRET_ACCESS_KEY)
            else:
                result_id = validate_prompts_lambda(formatted_prompts, aws_region=Config.AWS_REGION)
            
            logger.info(f"✅ Validación ejecutada - ID: {result_id.get('job_id', 'N/A')}")
            return result_id
            
        except Exception as e:
            logger.error(f"❌ Error en validación IA: {str(e)}")
            raise
    
    def _prepare_prompts_for_validation(self) -> List[Dict[str, str]]:
        """
        Convierte los prompts al formato requerido por validate_prompts_lambda
        
        Returns:
            Lista de prompts en formato: [{"id": "prompt_001", "prompt": "..."}]
        """
        return [
            {"id": f"prompt_{i+1:03d}", "prompt": prompt.strip()} 
            for i, prompt in enumerate(self.prompts) 
            if prompt and prompt.strip()
        ]
    
    def _generate_final_report(self, validation_result: Dict[str, Any]) -> str:
        """Genera el reporte final de validación"""
        logger.info("📊 Generando reporte final")
        
        try:
            report = generate_report_sync(validation_result, self.config.report_title)
            logger.info("✅ Reporte generado exitosamente")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {str(e)}")
            raise


class ValidationResultAnalyzer:
    """
    Analizador de resultados de validación.
    
    Proporciona métodos para inspeccionar y mostrar los resultados
    de manera estructurada y comprensible.
    """
    
    def analyze_results(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza y muestra los resultados de validación de forma estructurada
        
        Args:
            validation_result: Resultado de la validación desde AWS Bedrock
            
        Returns:
            Resumen estructurado de los resultados
        """
        logger.info("🔍 Analizando resultados de validación")
        
        analysis = {
            'basic_info': self._extract_basic_info(validation_result),
            'performance_metrics': self._extract_performance_metrics(validation_result),
            'detailed_summary': self._extract_detailed_summary(validation_result),
            'ai_responses': self.get_ai_responses(validation_result),
            'error_info': self._extract_error_info(validation_result)
        }
        
        self._log_analysis_summary(analysis)
        return analysis
    
    def _extract_basic_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información básica del resultado"""
        basic_info = {
            'job_id': result.get('job_id', 'N/A'),
            'status': result.get('status', 'N/A'),
            'processing_mode': result.get('processing_mode', 'N/A'),
            'processing_strategy': result.get('processing_strategy', 'N/A'),
            'used_s3': 's3_info' in result
        }
        
        if 's3_info' in result:
            s3_info = result['s3_info']
            basic_info['s3_bucket'] = s3_info.get('bucket', 'N/A')
            basic_info['s3_input_key'] = s3_info.get('input_key', 'N/A')
        
        return basic_info
    
    def _extract_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae métricas de rendimiento"""
        metrics = {}
        
        if 'performance_metrics' in result:
            perf = result['performance_metrics']
            metrics.update({
                'prompts_per_second': perf.get('prompts_per_second', 0),
                'total_time_minutes': perf.get('total_time_minutes', 0)
            })
        
        if 'summary' in result:
            metrics['summary'] = result['summary']
        
        return metrics
    
    def _extract_detailed_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae resumen detallado de resultados"""
        if 'results' not in result:
            return {'total_prompts': 0, 'successful_executions': 0, 'failed_executions': 0}
        
        total_prompts = len(result['results'])
        successful = 0
        failed = 0
        
        for prompt_result in result['results']:
            if 'execution' in prompt_result:
                execution = prompt_result['execution']
                if execution.get('execution_successful', False):
                    successful += 1
                else:
                    failed += 1
        
        return {
            'total_prompts': total_prompts,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': (successful / total_prompts * 100) if total_prompts > 0 else 0
        }
    
    def _extract_error_info(self, result: Dict[str, Any]) -> Optional[str]:
        """Extrae información de errores si existe"""
        return result.get('error')
    
    def _log_analysis_summary(self, analysis: Dict[str, Any]) -> None:
        """Registra un resumen del análisis en los logs"""
        basic = analysis['basic_info']
        summary = analysis['detailed_summary']
        
        logger.info("=" * 60)
        logger.info(f"Job ID: {basic['job_id']}")
        logger.info(f"Estado: {basic['status']}")
        logger.info(f"🚀 Estrategia: {basic['processing_strategy']}")
        logger.info(f"☁️ Usó S3: {'Sí' if basic['used_s3'] else 'No'}")
        logger.info(f"📊 Prompts procesados: {summary['total_prompts']}")
        logger.info(f"✅ Ejecuciones exitosas: {summary['successful_executions']}")
        logger.info(f"❌ Ejecuciones fallidas: {summary['failed_executions']}")
        logger.info(f"📈 Tasa de éxito: {summary['success_rate']:.1f}%")
        
        if analysis['error_info']:
            logger.error(f"❌ Error: {analysis['error_info']}")
        
        logger.info("=" * 60)
    
    def get_ai_responses(self, validation_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extrae todas las respuestas de IA de los resultados
        
        Returns:
            Lista de respuestas con su ID correspondiente
        """
        responses = []
        
        if 'results' not in validation_result:
            return responses
        
        for prompt_result in validation_result['results']:
            prompt_id = prompt_result.get('prompt_id', 'unknown')
            
            if 'execution' in prompt_result:
                execution = prompt_result['execution']
                response = execution.get('response', '')
                
                if response:
                    responses.append({
                        'prompt_id': prompt_id,
                        'response': response,
                        'tokens_used': execution.get('tokens_used', 0),
                        'successful': execution.get('execution_successful', False)
                    })
        
        return responses


def _extract_config_from_event(event: Dict[str, Any]) -> PipelineConfig:
    """
    Extrae la configuración del pipeline desde el evento de Lambda
    
    Args:
        event: Evento de Lambda conteniendo los parámetros
        
    Returns:
        PipelineConfig configurado
        
    Raises:
        ValueError: Si faltan parámetros requeridos
    """
    # Intentar obtener configuración del evento
    repository_url = event.get('repository_url')
    branch = event.get('branch', 'main')
    report_title = event.get('report_title', 'Reporte de Validación')
    
    # Si no está en el evento, intentar variables de entorno
    if not repository_url:
        repository_url = os.environ.get('REPOSITORY_URL')
        branch = os.environ.get('BRANCH', branch)
        report_title = os.environ.get('REPORT_TITLE', report_title)
    
    # Validar parámetros requeridos
    if not repository_url:
        raise ValueError("repository_url es requerido en el evento o variable de entorno REPOSITORY_URL")
    
    return PipelineConfig(
        repository_url=repository_url,
        branch=branch,
        report_title=report_title
    )


def _create_lambda_response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Crea una respuesta HTTP estándar para Lambda
    
    Args:
        status_code: Código de estado HTTP
        body: Cuerpo de la respuesta
        headers: Headers opcionales
        
    Returns:
        Respuesta formateada para Lambda
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, ensure_ascii=False, indent=2, default=_json_fallback)

    }


def lambda_handler(event, context):
    """
    Handler principal de la función Lambda
    
    Args:
        event: Evento de Lambda con parámetros de configuración
        context: Contexto de ejecución de Lambda
        
    Returns:
        Respuesta HTTP con los resultados del pipeline
    """
    # Información del contexto de Lambda
    request_id = context.aws_request_id
    function_name = context.function_name
    
    logger.info(f"🚀 Iniciando Lambda {function_name} - Request ID: {request_id}")
    logger.info(f"📋 Evento recibido: {json.dumps(event, ensure_ascii=False)}")
    
    try:
        # 1. Extraer configuración del evento
        config = _extract_config_from_event(event)
        logger.info(f"⚙️ Configuración: {config}")
        
        # 2. Ejecutar pipeline de validación
        pipeline = ValidationPipeline(config)
        pipeline_result = pipeline.execute()
        
        # 3. Analizar resultados
        analyzer = ValidationResultAnalyzer()
        analysis = analyzer.analyze_results(pipeline_result['validation_result'])
        
        # 4. Preparar respuesta exitosa
        response_body = {
            'success': True,
            'request_id': request_id,
            'message': 'Pipeline de validación ejecutado exitosamente',
            'pipeline_summary': {
                'prompts_count': pipeline_result['prompts_count'],
                'rules_count': pipeline_result['rules_count'],
                'job_id': analysis['basic_info']['job_id'],
                'success_rate': analysis['detailed_summary']['success_rate']
            },
            'validation_result': pipeline_result['validation_result'],
            'report': pipeline_result['report'],
            'analysis': analysis,
            'config_used': {
                'repository_url': config.repository_url,
                'branch': config.branch,
                'report_title': config.report_title
            }
        }
        
        logger.info(f"✅ Pipeline completado exitosamente:")
        logger.info(f"   - {pipeline_result['prompts_count']} prompts procesados")
        logger.info(f"   - {pipeline_result['rules_count']} reglas aplicadas")
        logger.info(f"   - {len(analysis['ai_responses'])} respuestas de IA generadas")
        logger.info(f"   - Tasa de éxito: {analysis['detailed_summary']['success_rate']:.1f}%")
        
        return _create_lambda_response(200, response_body)
        
    except ValueError as ve:
        # Error de configuración/parámetros
        error_message = f"Error de configuración: {str(ve)}"
        logger.error(f"⚙️ {error_message}")
        
        return _create_lambda_response(400, {
            'success': False,
            'request_id': request_id,
            'error_type': 'ConfigurationError',
            'error_message': error_message,
            'help': 'Verifica que repository_url esté presente en el evento o variable de entorno'
        })
        
    except Exception as e:
        # Error general del pipeline
        error_message = f"Error en pipeline: {str(e)}"
        logger.error(f"💥 {error_message}")
        logger.exception("Detalles del error:")
        
        return _create_lambda_response(500, {
            'success': False,
            'request_id': request_id,
            'error_type': 'PipelineError',
            'error_message': error_message,
            'function_name': function_name
        })
    
def _json_fallback(obj):
    if hasattr(obj, "model_dump"):  # Si es Pydantic
        return obj.model_dump()
    elif hasattr(obj, "__dict__"):  # Si es clase normal
        return obj.__dict__
    else:
        return str(obj)