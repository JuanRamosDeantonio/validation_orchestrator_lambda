"""
result_processor.py - Procesador de resultados y consolidación final
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import asdict

from app.utils import setup_logger, Config, ErrorHandler  # CORREGIDO: Import consistente
from app.models import ValidationResult, ConsolidatedResult  # CORREGIDO: Import consistente
from app.integrations import IntegrationManager  # CORREGIDO: Import consistente

# Configurar logging
logger = setup_logger(__name__)

class ResultProcessor:
    """
    Procesador centralizado para consolidación, análisis y formateo de resultados.
    
    Se encarga de aplicar la lógica de negocio para determinar si un repositorio
    pasa o falla la validación, generar métricas y preparar datos para reportes.
    """
    
    def __init__(self, integration_manager: IntegrationManager):
        self.integration_manager = integration_manager
        self.processing_metadata = {}
        self.consolidation_rules = self._initialize_consolidation_rules()
        
    def _initialize_consolidation_rules(self) -> Dict[str, Any]:
        """
        Inicializa las reglas de consolidación para diferentes escenarios.
        
        Returns:
            dict: Configuración de reglas de consolidación
        """
        return {
            'critical_failure_threshold': 0,  # Cualquier falla crítica = rechazo
            'medium_failure_threshold': 2,    # Máximo 2 fallas medias permitidas
            'low_failure_threshold': 5,       # Máximo 5 fallas bajas permitidas
            'minimum_confidence_required': 'Media',  # Confianza mínima aceptable
            'partial_result_handling': 'conservative',  # Cómo manejar resultados parciales
            'chunk_consolidation_strategy': 'strict_for_critical'  # Estrategia para chunks
        }
    
    def process_and_consolidate_results(self, validation_results: List[ValidationResult], 
                                      processing_context: Dict[str, Any]) -> ConsolidatedResult:
        """
        Procesa y consolida todos los resultados de validación en una decisión final.
        
        Args:
            validation_results: Lista de resultados individuales de validación
            processing_context: Contexto del procesamiento (tiempos, estadísticas, etc.)
            
        Returns:
            ConsolidatedResult: Resultado final consolidado con decisión
            
        Raises:
            Exception: Si hay errores críticos en el procesamiento
        """
        start_time = time.time()
        
        try:
            logger.info("Iniciando procesamiento y consolidación de resultados")
            logger.info(f"Procesando {len(validation_results)} resultados de validación")
            
            # Análisis inicial de resultados
            analysis = self._analyze_validation_results(validation_results)
            
            # Aplicar lógica de consolidación
            consolidation_decision = self._apply_consolidation_logic(analysis)
            
            # Generar métricas detalladas
            detailed_metrics = self._generate_detailed_metrics(validation_results, analysis)
            
            # Crear resultado consolidado - CORREGIDO: Usar método actualizado
            consolidated_result = self._create_consolidated_result(
                consolidation_decision, analysis, detailed_metrics, processing_context
            )
            
            # Registrar estadísticas de procesamiento
            processing_time = time.time() - start_time
            self._record_processing_statistics(consolidated_result, processing_time)
            
            logger.info(f"Consolidación completada en {processing_time:.3f}s")
            logger.info(f"Decisión final: {'APROBADO' if consolidated_result.passed else 'RECHAZADO'}")
            
            return consolidated_result
            
        except Exception as e:
            logger.error(f"Error en procesamiento de resultados: {str(e)}")
            raise Exception(f"Falló el procesamiento de resultados: {str(e)}")
    
    def _analyze_validation_results(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza los resultados de validación para extraer patrones y estadísticas.
        
        Args:
            results: Lista de resultados a analizar
            
        Returns:
            dict: Análisis completo de los resultados
        """
        logger.debug("Analizando resultados de validación")
        
        if not results:
            logger.warning("No hay resultados para analizar")
            return {
                'total_rules': 0,
                'by_criticality': {},
                'by_type': {},
                'by_result': {},
                'confidence_analysis': {},
                'execution_analysis': {},
                'error_analysis': {}
            }
        
        # Análisis por criticidad
        by_criticality = self._analyze_by_criticality(results)
        
        # Análisis por tipo de regla
        by_type = self._analyze_by_rule_type(results)
        
        # Análisis por resultado
        by_result = self._analyze_by_result_status(results)
        
        # Análisis de confianza
        confidence_analysis = self._analyze_confidence_levels(results)
        
        # Análisis de ejecución
        execution_analysis = self._analyze_execution_metrics(results)
        
        # Análisis de errores y problemas
        error_analysis = self._analyze_error_patterns(results)
        
        analysis = {
            'total_rules': len(results),
            'by_criticality': by_criticality,
            'by_type': by_type,
            'by_result': by_result,
            'confidence_analysis': confidence_analysis,
            'execution_analysis': execution_analysis,
            'error_analysis': error_analysis
        }
        
        logger.debug(f"Análisis completado: {analysis['total_rules']} reglas analizadas")
        
        return analysis
    
    def _analyze_by_criticality(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza resultados agrupados por nivel de criticidad.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis por criticidad
        """
        by_criticality = defaultdict(lambda: {
            'total': 0,
            'cumple': 0,
            'no_cumple': 0,
            'parcial': 0,
            'rules': []
        })
        
        for result in results:
            criticality = result.rule_criticality.lower()
            by_criticality[criticality]['total'] += 1
            by_criticality[criticality]['rules'].append(result.rule_id)
            
            if result.resultado == 'CUMPLE':
                by_criticality[criticality]['cumple'] += 1
            elif result.resultado == 'NO_CUMPLE':
                by_criticality[criticality]['no_cumple'] += 1
            else:
                by_criticality[criticality]['parcial'] += 1
        
        # Calcular porcentajes de éxito por criticidad
        for criticality, data in by_criticality.items():
            if data['total'] > 0:
                data['success_rate'] = (data['cumple'] / data['total']) * 100
                data['failure_rate'] = (data['no_cumple'] / data['total']) * 100
        
        logger.debug(f"Análisis por criticidad: {dict(by_criticality)}")
        
        return dict(by_criticality)
    
    def _analyze_by_rule_type(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza resultados agrupados por tipo de regla.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis por tipo de regla
        """
        by_type = defaultdict(lambda: {
            'total': 0,
            'cumple': 0,
            'no_cumple': 0,
            'parcial': 0,
            'avg_confidence': 0,
            'models_used': Counter(),
            'avg_content_size': 0
        })
        
        for result in results:
            rule_type = result.rule_type.lower()
            by_type[rule_type]['total'] += 1
            
            # Contadores por resultado
            if result.resultado == 'CUMPLE':
                by_type[rule_type]['cumple'] += 1
            elif result.resultado == 'NO_CUMPLE':
                by_type[rule_type]['no_cumple'] += 1
            else:
                by_type[rule_type]['parcial'] += 1
            
            # Modelos utilizados
            if result.model_used:
                by_type[rule_type]['models_used'][result.model_used] += 1
            
            # Tamaño de contenido promedio
            by_type[rule_type]['avg_content_size'] += result.content_size_analyzed
        
        # Calcular promedios y estadísticas finales
        for rule_type, data in by_type.items():
            if data['total'] > 0:
                data['success_rate'] = (data['cumple'] / data['total']) * 100
                data['avg_content_size'] = data['avg_content_size'] // data['total']
                data['models_used'] = dict(data['models_used'])
        
        logger.debug(f"Análisis por tipo: {dict(by_type)}")
        
        return dict(by_type)
    
    def _analyze_by_result_status(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza la distribución de estados de resultado.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis de distribución de resultados
        """
        result_counts = Counter(result.resultado for result in results)
        confidence_by_result = defaultdict(list)
        
        for result in results:
            confidence_by_result[result.resultado].append(result.confianza)
        
        # Calcular confianza promedio por tipo de resultado
        avg_confidence = {}
        for resultado, confidences in confidence_by_result.items():
            confidence_scores = []
            for conf in confidences:
                if conf.lower() == 'alta':
                    confidence_scores.append(3)
                elif conf.lower() == 'media':
                    confidence_scores.append(2)
                else:
                    confidence_scores.append(1)
            
            avg_confidence[resultado] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        total_results = len(results)
        percentages = {
            resultado: (count / total_results) * 100 
            for resultado, count in result_counts.items()
        }
        
        return {
            'counts': dict(result_counts),
            'percentages': percentages,
            'average_confidence_by_result': avg_confidence,
            'total_results': total_results
        }
    
    def _analyze_confidence_levels(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza los niveles de confianza de las validaciones.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis de niveles de confianza
        """
        confidence_counts = Counter(result.confianza.lower() for result in results)
        
        # Identificar resultados con baja confianza
        low_confidence_results = [
            result for result in results 
            if result.confianza.lower() == 'baja'
        ]
        
        # Calcular score de confianza general
        confidence_scores = []
        for result in results:
            if result.confianza.lower() == 'alta':
                confidence_scores.append(3)
            elif result.confianza.lower() == 'media':
                confidence_scores.append(2)
            else:
                confidence_scores.append(1)
        
        avg_confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'distribution': dict(confidence_counts),
            'average_score': avg_confidence_score,
            'low_confidence_count': len(low_confidence_results),
            'low_confidence_rules': [r.rule_id for r in low_confidence_results],
            'confidence_threshold_met': avg_confidence_score >= 2.0  # Media o superior
        }
    
    def _analyze_execution_metrics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza métricas de ejecución y rendimiento.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis de métricas de ejecución
        """
        # Análisis de modelos utilizados
        model_usage = Counter(result.model_used for result in results if result.model_used)
        
        # Análisis de chunks procesados
        total_chunks = sum(result.chunks_processed for result in results)
        rules_with_chunks = [r for r in results if r.chunks_processed > 1]
        
        # Análisis de tamaño de contenido
        content_sizes = [result.content_size_analyzed for result in results]
        avg_content_size = sum(content_sizes) / len(content_sizes) if content_sizes else 0
        max_content_size = max(content_sizes) if content_sizes else 0
        
        # Análisis de tiempos de ejecución (si están disponibles)
        execution_times = [
            getattr(result, 'execution_time', 0) 
            for result in results 
            if hasattr(result, 'execution_time') and getattr(result, 'execution_time', 0) > 0
        ]
        
        return {
            'model_usage': dict(model_usage),
            'total_chunks_processed': total_chunks,
            'rules_requiring_chunking': len(rules_with_chunks),
            'chunking_rules': [r.rule_id for r in rules_with_chunks],
            'content_analysis': {
                'average_size': avg_content_size,
                'maximum_size': max_content_size,
                'total_content_analyzed': sum(content_sizes)
            },
            'execution_times': {
                'count': len(execution_times),
                'average': sum(execution_times) / len(execution_times) if execution_times else 0,
                'total': sum(execution_times)
            }
        }
    
    def _analyze_error_patterns(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Analiza patrones de errores y problemas en las validaciones.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Análisis de patrones de errores
        """
        # Identificar resultados problemáticos
        failed_results = [r for r in results if r.resultado == 'NO_CUMPLE']
        low_confidence_results = [r for r in results if r.confianza.lower() == 'baja']
        
        # Análisis de explicaciones para encontrar patrones
        failure_explanations = [r.explicacion for r in failed_results if r.explicacion]
        
        # Palabras clave comunes en fallas
        common_failure_keywords = self._extract_common_keywords(failure_explanations)
        
        # Análisis por criticidad de fallas
        critical_failures = [r for r in failed_results if r.rule_criticality.lower() == 'alta']
        
        return {
            'total_failures': len(failed_results),
            'critical_failures': len(critical_failures),
            'critical_failure_rules': [r.rule_id for r in critical_failures],
            'low_confidence_count': len(low_confidence_results),
            'common_failure_patterns': common_failure_keywords,
            'failure_rate_by_type': self._calculate_failure_rate_by_type(results),
            'problematic_rules': self._identify_problematic_rules(results)
        }
    
    def _extract_common_keywords(self, explanations: List[str]) -> List[str]:
        """
        Extrae palabras clave comunes de las explicaciones de fallas.
        
        Args:
            explanations: Lista de explicaciones de fallas
            
        Returns:
            list: Palabras clave más comunes
        """
        if not explanations:
            return []
        
        # Palabras comunes a ignorar
        stop_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'del', 'las', 'al', 'una', 'su', 'los', 'como', 'pero', 'sus', 'está', 'fue', 'tiene', 'muy', 'todo', 'hay', 'más', 'nos', 'si', 'ya', 'he', 'código', 'archivo', 'función'}
        
        # Extraer palabras de todas las explicaciones
        all_words = []
        for explanation in explanations:
            words = explanation.lower().split()
            filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
            all_words.extend(filtered_words)
        
        # Contar frecuencias y retornar las más comunes
        word_counts = Counter(all_words)
        return [word for word, count in word_counts.most_common(5)]
    
    def _calculate_failure_rate_by_type(self, results: List[ValidationResult]) -> Dict[str, float]:
        """
        Calcula tasa de fallas por tipo de regla.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            dict: Tasa de fallas por tipo
        """
        by_type = defaultdict(lambda: {'total': 0, 'failures': 0})
        
        for result in results:
            rule_type = result.rule_type.lower()
            by_type[rule_type]['total'] += 1
            if result.resultado == 'NO_CUMPLE':
                by_type[rule_type]['failures'] += 1
        
        failure_rates = {}
        for rule_type, data in by_type.items():
            failure_rates[rule_type] = (data['failures'] / data['total']) * 100 if data['total'] > 0 else 0
        
        return failure_rates
    
    def _identify_problematic_rules(self, results: List[ValidationResult]) -> List[str]:
        """
        Identifica reglas que consistentemente tienen problemas.
        
        Args:
            results: Resultados a analizar
            
        Returns:
            list: IDs de reglas problemáticas
        """
        problematic = []
        
        for result in results:
            # Regla problemática si:
            # 1. Falló y es crítica
            # 2. Tiene baja confianza
            # 3. Requirió muchos chunks (indicativo de contenido problemático)
            if ((result.resultado == 'NO_CUMPLE' and result.rule_criticality.lower() == 'alta') or
                result.confianza.lower() == 'baja' or
                result.chunks_processed > 3):
                problematic.append(result.rule_id)
        
        return problematic
    
    def _apply_consolidation_logic(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica la lógica de consolidación para determinar el resultado final.
        
        Args:
            analysis: Análisis completo de resultados
            
        Returns:
            dict: Decisión de consolidación con justificación
        """
        logger.debug("Aplicando lógica de consolidación")
        
        by_criticality = analysis['by_criticality']
        confidence_analysis = analysis['confidence_analysis']
        error_analysis = analysis['error_analysis']
        
        # Extraer contadores de fallas por criticidad
        critical_failures = by_criticality.get('alta', {}).get('no_cumple', 0)
        medium_failures = by_criticality.get('media', {}).get('no_cumple', 0)
        low_failures = by_criticality.get('baja', {}).get('no_cumple', 0)
        
        # Aplicar reglas de consolidación
        decision_factors = []
        
        # Factor 1: Fallas críticas (tienen prioridad absoluta)
        if critical_failures > self.consolidation_rules['critical_failure_threshold']:
            decision_factors.append({
                'factor': 'critical_failures',
                'value': critical_failures,
                'impact': 'reject',
                'priority': 1,
                'reason': f'{critical_failures} regla(s) crítica(s) fallaron'
            })
        
        # Factor 2: Fallas medias
        if medium_failures > self.consolidation_rules['medium_failure_threshold']:
            decision_factors.append({
                'factor': 'medium_failures',
                'value': medium_failures,
                'impact': 'reject',
                'priority': 2,
                'reason': f'{medium_failures} reglas de prioridad media fallaron (límite: {self.consolidation_rules["medium_failure_threshold"]})'
            })
        
        # Factor 3: Fallas bajas
        if low_failures > self.consolidation_rules['low_failure_threshold']:
            decision_factors.append({
                'factor': 'low_failures',
                'value': low_failures,
                'impact': 'reject',
                'priority': 3,
                'reason': f'{low_failures} reglas de baja prioridad fallaron (límite: {self.consolidation_rules["low_failure_threshold"]})'
            })
        
        # Factor 4: Confianza general
        if not confidence_analysis.get('confidence_threshold_met', True):
            decision_factors.append({
                'factor': 'low_confidence',
                'value': confidence_analysis['average_score'],
                'impact': 'concern',
                'priority': 4,
                'reason': f'Confianza promedio baja: {confidence_analysis["average_score"]:.2f}'
            })
        
        # Determinar decisión final
        rejection_factors = [f for f in decision_factors if f['impact'] == 'reject']
        
        if rejection_factors:
            # Ordenar por prioridad y tomar el más importante
            rejection_factors.sort(key=lambda x: x['priority'])
            primary_reason = rejection_factors[0]
            
            decision = {
                'passed': False,
                'primary_reason': primary_reason['reason'],
                'all_factors': decision_factors,
                'decision_confidence': 'Alta' if critical_failures > 0 else 'Media'
            }
        else:
            # No hay factores de rechazo - aprobado
            decision = {
                'passed': True,
                'primary_reason': 'Todas las validaciones pasaron los umbrales requeridos',
                'all_factors': decision_factors,
                'decision_confidence': 'Alta' if not decision_factors else 'Media'
            }
        
        logger.info(f"Decisión de consolidación: {'APROBADO' if decision['passed'] else 'RECHAZADO'}")
        logger.info(f"Razón principal: {decision['primary_reason']}")
        
        return decision
    
    def _generate_detailed_metrics(self, results: List[ValidationResult], 
                                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera métricas detalladas para reportes y análisis.
        
        Args:
            results: Resultados de validación
            analysis: Análisis previo de resultados
            
        Returns:
            dict: Métricas detalladas
        """
        logger.debug("Generando métricas detalladas")
        
        metrics = {
            'summary': {
                'total_rules_evaluated': len(results),
                'success_rate': analysis['by_result']['percentages'].get('CUMPLE', 0),
                'failure_rate': analysis['by_result']['percentages'].get('NO_CUMPLE', 0),
                'partial_rate': analysis['by_result']['percentages'].get('PARCIAL', 0)
            },
            'by_criticality': analysis['by_criticality'],
            'by_rule_type': analysis['by_type'],
            'confidence_metrics': analysis['confidence_analysis'],
            'execution_metrics': analysis['execution_analysis'],
            'quality_indicators': {
                'high_confidence_percentage': (
                    analysis['confidence_analysis']['distribution'].get('alta', 0) / len(results) * 100
                    if results else 0
                ),
                'successful_critical_rules': (
                    analysis['by_criticality'].get('alta', {}).get('cumple', 0)
                ),
                'problematic_rules_count': len(analysis['error_analysis']['problematic_rules'])
            },
            'cost_analysis': self._calculate_cost_analysis(analysis['execution_metrics']),
            'recommendations': self._generate_improvement_recommendations(analysis)
        }
        
        return metrics
    
    def _calculate_cost_analysis(self, execution_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula análisis de costos basado en uso de modelos.
        
        Args:
            execution_metrics: Métricas de ejecución
            
        Returns:
            dict: Análisis de costos
        """
        model_usage = execution_metrics.get('model_usage', {})
        
        # Costos aproximados por modelo (por 1M tokens)
        model_costs = {
            'claude-3-haiku': {'input': 0.25, 'output': 1.25},
            'claude-3-sonnet': {'input': 3.0, 'output': 15.0},
            'logica_estructural': {'input': 0, 'output': 0},  # Sin costo
            'no_content_check': {'input': 0, 'output': 0}
        }
        
        estimated_cost = 0
        cost_breakdown = {}
        
        for model, usage_count in model_usage.items():
            if model in model_costs:
                # Estimación aproximada: 10K tokens input, 200 tokens output por validación
                estimated_input_cost = (usage_count * 10000 / 1000000) * model_costs[model]['input']
                estimated_output_cost = (usage_count * 200 / 1000000) * model_costs[model]['output']
                
                model_total = estimated_input_cost + estimated_output_cost
                estimated_cost += model_total
                
                cost_breakdown[model] = {
                    'usage_count': usage_count,
                    'estimated_cost': model_total,
                    'input_cost': estimated_input_cost,
                    'output_cost': estimated_output_cost
                }
        
        return {
            'total_estimated_cost': round(estimated_cost, 4),
            'cost_breakdown': cost_breakdown,
            'cost_efficiency': 'high' if estimated_cost < 0.1 else 'medium' if estimated_cost < 0.5 else 'low'
        }
    
    def _generate_improvement_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones de mejora basadas en el análisis.
        
        Args:
            analysis: Análisis completo de resultados
            
        Returns:
            list: Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en confianza
        if analysis['confidence_analysis']['average_score'] < 2.5:
            recommendations.append(
                "Considerar revisar las reglas con baja confianza para mejorar la claridad de los criterios"
            )
        
        # Recomendaciones basadas en fallas críticas
        critical_failures = analysis['by_criticality'].get('alta', {}).get('no_cumple', 0)
        if critical_failures > 0:
            recommendations.append(
                f"Atender urgentemente las {critical_failures} regla(s) crítica(s) que fallaron"
            )
        
        # Recomendaciones basadas en uso de modelos
        model_usage = analysis['execution_analysis']['model_usage']
        if model_usage.get('claude-3-sonnet', 0) > model_usage.get('claude-3-haiku', 0) * 2:
            recommendations.append(
                "Considerar optimizar el uso de modelos IA para reducir costos"
            )
        
        # Recomendaciones basadas en chunking
        if analysis['execution_analysis']['rules_requiring_chunking'] > 5:
            recommendations.append(
                "Implementar estrategias de chunking más eficientes para documentos grandes"
            )
        
        # Recomendaciones basadas en patrones de falla
        failure_rate_by_type = analysis['error_analysis']['failure_rate_by_type']
        high_failure_types = [t for t, rate in failure_rate_by_type.items() if rate > 30]
        if high_failure_types:
            recommendations.append(
                f"Revisar reglas de tipo {', '.join(high_failure_types)} que tienen alta tasa de falla"
            )
        
        return recommendations
    
    def _create_consolidated_result(self, decision: Dict[str, Any], analysis: Dict[str, Any],
                                  metrics: Dict[str, Any], context: Dict[str, Any]) -> ConsolidatedResult:
        """
        Crea el resultado consolidado final usando el modelo corregido.
        
        Args:
            decision: Decisión de consolidación
            analysis: Análisis de resultados
            metrics: Métricas detalladas
            context: Contexto de procesamiento
            
        Returns:
            ConsolidatedResult: Resultado final consolidado
        """
        # Extraer contadores de fallas
        by_criticality = analysis['by_criticality']
        critical_failures = by_criticality.get('alta', {}).get('no_cumple', 0)
        medium_failures = by_criticality.get('media', {}).get('no_cumple', 0)
        low_failures = by_criticality.get('baja', {}).get('no_cumple', 0)
        
        # Crear mensaje descriptivo
        if decision['passed']:
            message = "Validación de repositorio aprobada exitosamente"
        else:
            message = f"Validación de repositorio rechazada: {decision['primary_reason']}"
        
        # CORREGIDO: Bug #2 - Usar modelo actualizado con todos los campos
        consolidated_result = ConsolidatedResult(
            passed=decision['passed'],
            message=message,
            total_rules_processed=analysis['total_rules'],
            critical_failures=critical_failures,
            medium_failures=medium_failures,
            low_failures=low_failures,
            system_errors=context.get('system_errors', 0),
            execution_time_ms=context.get('execution_time_ms'),
            # NUEVOS CAMPOS del modelo corregido - Ya no causan error
            detailed_metrics=metrics,
            decision_factors=decision['all_factors'],
            confidence_level=decision['decision_confidence']
        )
        
        return consolidated_result
    
    def _record_processing_statistics(self, result: ConsolidatedResult, processing_time: float):
        """
        Registra estadísticas del procesamiento para análisis futuro.
        
        Args:
            result: Resultado consolidado
            processing_time: Tiempo de procesamiento
        """
        self.processing_metadata = {
            'processing_time': processing_time,
            'timestamp': time.time(),
            'rules_processed': result.total_rules_processed,
            'decision': 'passed' if result.passed else 'failed',
            'critical_failures': result.critical_failures,
            'confidence_level': result.confidence_level  # Ahora es un campo válido
        }
        
        logger.debug(f"Estadísticas de procesamiento registradas: {self.processing_metadata}")
    
    async def prepare_for_post_processing(self, consolidated_result: ConsolidatedResult,
                                        repository_url: str, user_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Prepara los datos para el post-procesamiento (reportes, notificaciones).
        
        Args:
            consolidated_result: Resultado consolidado
            repository_url: URL del repositorio
            user_info: Información del usuario
            
        Returns:
            dict: Datos preparados para post-procesamiento
        """
        logger.info("Preparando datos para post-procesamiento")
        
        post_processing_data = {
            'validation_summary': {
                'repository_url': repository_url,
                'validation_result': consolidated_result.passed,
                'message': consolidated_result.message,
                'timestamp': time.time(),
                'processing_metadata': self.processing_metadata
            },
            'user_info': user_info,
            'detailed_results': {
                'total_rules': consolidated_result.total_rules_processed,
                'failures_by_criticality': {
                    'critical': consolidated_result.critical_failures,
                    'medium': consolidated_result.medium_failures,
                    'low': consolidated_result.low_failures
                },
                'execution_time': consolidated_result.execution_time_ms,
                # Usar campos del modelo corregido
                'detailed_metrics': consolidated_result.detailed_metrics,
                'decision_factors': consolidated_result.decision_factors
            },
            'recommendations': consolidated_result.detailed_metrics.get('recommendations', []) if consolidated_result.detailed_metrics else [],
            'notification_priority': self._determine_notification_priority(consolidated_result),
            'report_sections': self._determine_report_sections(consolidated_result)
        }
        
        logger.info("Datos de post-procesamiento preparados exitosamente")
        
        return post_processing_data
    
    def _determine_notification_priority(self, result: ConsolidatedResult) -> str:
        """
        Determina la prioridad de notificación basada en el resultado.
        
        Args:
            result: Resultado consolidado
            
        Returns:
            str: Prioridad de notificación
        """
        if result.critical_failures > 0:
            return 'high'
        elif not result.passed:
            return 'medium'
        else:
            return 'low'
    
    def _determine_report_sections(self, result: ConsolidatedResult) -> List[str]:
        """
        Determina qué secciones incluir en el reporte basado en el resultado.
        
        Args:
            result: Resultado consolidado
            
        Returns:
            list: Secciones a incluir en el reporte
        """
        sections = ['summary', 'metrics']
        
        if result.critical_failures > 0:
            sections.extend(['critical_failures_detail', 'remediation_steps'])
        
        if result.medium_failures > 0 or result.low_failures > 0:
            sections.append('improvement_recommendations')
        
        if result.detailed_metrics:  # Ahora es un campo válido
            sections.extend(['cost_analysis', 'performance_analysis'])
        
        return sections
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del procesamiento de resultados.
        
        Returns:
            dict: Estadísticas completas del procesador
        """
        return {
            'processing_metadata': self.processing_metadata,
            'consolidation_rules': self.consolidation_rules,
            'last_processing_time': self.processing_metadata.get('processing_time', 0),
            'total_rules_processed': self.processing_metadata.get('rules_processed', 0)
        }