"""
model_selector.py - Selector inteligente de modelos de IA
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.utils import setup_logger, Config, estimate_tokens  # CORREGIDO: Import consistente
from app.models import RuleData  # CORREGIDO: Import consistente

# Configurar logging
logger = setup_logger(__name__)

class ModelType(Enum):
    """Tipos de modelos disponibles."""
    HAIKU = "claude-3-haiku"
    SONNET = "claude-3-sonnet"
    STRUCTURAL_LOGIC = "structural_logic"  # Sin IA, lógica programada

@dataclass
class ModelRecommendation:
    """Recomendación de modelo con justificación."""
    model_type: ModelType
    confidence: float  # 0.0 - 1.0
    reasoning: str
    estimated_cost: float
    estimated_time: float
    fallback_model: Optional[ModelType] = None
    cost_optimization_applied: bool = False

@dataclass
class ModelCapabilities:
    """Capacidades y características de un modelo."""
    max_tokens: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    avg_response_time: float  # segundos
    quality_score: float  # 0.0 - 1.0
    best_for_rule_types: List[str]
    complexity_handling: str  # 'low', 'medium', 'high'

class ModelSelector:
    """
    Selector inteligente que determina el modelo óptimo para cada validación.
    
    Considera factores como tipo de regla, criticidad, tamaño de contenido,
    costos, tiempo de respuesta y calidad requerida para tomar decisiones óptimas.
    """
    
    def __init__(self):
        self.model_capabilities = self._initialize_model_capabilities()
        self.selection_history = []
        self.cost_tracking = {
            'total_estimated_cost': 0.0,
            'model_usage_count': {},
            'cost_by_model': {}
        }
        self.selection_strategies = {
            'cost_optimized': self._select_cost_optimized,
            'quality_optimized': self._select_quality_optimized,
            'balanced': self._select_balanced,
            'speed_optimized': self._select_speed_optimized
        }
        
    def _initialize_model_capabilities(self) -> Dict[ModelType, ModelCapabilities]:
        """
        Inicializa las capacidades y características de cada modelo.
        
        Returns:
            dict: Capacidades de cada modelo disponible
        """
        return {
            ModelType.HAIKU: ModelCapabilities(
                max_tokens=200000,
                cost_per_1k_input_tokens=0.00025,  # $0.25 por 1M tokens
                cost_per_1k_output_tokens=0.00125,  # $1.25 por 1M tokens
                avg_response_time=2.5,
                quality_score=0.75,
                best_for_rule_types=['estructura', 'contenido'],
                complexity_handling='low'
            ),
            ModelType.SONNET: ModelCapabilities(
                max_tokens=200000,
                cost_per_1k_input_tokens=0.003,     # $3.00 por 1M tokens
                cost_per_1k_output_tokens=0.015,    # $15.00 por 1M tokens
                avg_response_time=5.0,
                quality_score=0.95,
                best_for_rule_types=['semántica'],
                complexity_handling='high'
            ),
            ModelType.STRUCTURAL_LOGIC: ModelCapabilities(
                max_tokens=float('inf'),  # Sin límite, es lógica programada
                cost_per_1k_input_tokens=0.0,
                cost_per_1k_output_tokens=0.0,
                avg_response_time=0.1,
                quality_score=0.90,  # Alta para validaciones estructurales específicas
                best_for_rule_types=['estructura'],
                complexity_handling='medium'
            )
        }
    
    def select_optimal_model(self, rule: RuleData, content_size: int, 
                           strategy: str = 'balanced', context: Dict[str, Any] = None) -> ModelRecommendation:
        """
        Selecciona el modelo óptimo para una regla específica.
        
        Args:
            rule: Regla que se va a validar
            content_size: Tamaño del contenido en caracteres
            strategy: Estrategia de selección ('cost_optimized', 'quality_optimized', 'balanced', 'speed_optimized')
            context: Contexto adicional para la decisión
            
        Returns:
            ModelRecommendation: Recomendación de modelo con justificación
        """
        try:
            logger.debug(f"Seleccionando modelo para regla {rule.id} ({rule.type}, {rule.criticality})")
            logger.debug(f"Tamaño de contenido: {content_size:,} caracteres, estrategia: {strategy}")
            
            # Aplicar estrategia de selección
            strategy_function = self.selection_strategies.get(strategy, self._select_balanced)
            recommendation = strategy_function(rule, content_size, context or {})
            
            # Validar y ajustar recomendación
            validated_recommendation = self._validate_and_adjust_recommendation(
                recommendation, rule, content_size
            )
            
            # Registrar selección para análisis futuro
            self._record_selection(validated_recommendation, rule, content_size, strategy)
            
            logger.info(f"Modelo seleccionado para regla {rule.id}: {validated_recommendation.model_type.value}")
            logger.debug(f"Justificación: {validated_recommendation.reasoning}")
            
            return validated_recommendation
            
        except Exception as e:
            logger.error(f"Error seleccionando modelo para regla {rule.id}: {str(e)}")
            # Fallback seguro
            return self._create_fallback_recommendation(rule, content_size)
    
    def _select_cost_optimized(self, rule: RuleData, content_size: int, 
                             context: Dict[str, Any]) -> ModelRecommendation:
        """
        Selección optimizada para minimizar costos.
        
        Args:
            rule: Regla a validar
            content_size: Tamaño del contenido
            context: Contexto adicional
            
        Returns:
            ModelRecommendation: Recomendación optimizada por costo
        """
        # Para reglas estructurales: usar lógica programada (costo cero)
        if rule.type.lower() == 'estructura':
            return ModelRecommendation(
                model_type=ModelType.STRUCTURAL_LOGIC,
                confidence=0.95,
                reasoning="Regla estructural: usando lógica programada sin costo de IA",
                estimated_cost=0.0,
                estimated_time=0.1,
                cost_optimization_applied=True
            )
        
        # Para reglas de contenido: usar Haiku (más económico)
        if rule.type.lower() == 'contenido':
            estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
            return ModelRecommendation(
                model_type=ModelType.HAIKU,
                confidence=0.85,
                reasoning="Regla de contenido: Claude Haiku para optimización de costos",
                estimated_cost=estimated_cost,
                estimated_time=2.5,
                fallback_model=ModelType.SONNET,
                cost_optimization_applied=True
            )
        
        # Para reglas semánticas: evaluar criticidad vs costo
        if rule.type.lower() == 'semántica':
            if rule.criticality.lower() == 'baja' and content_size < 50000:
                # Criticidad baja + contenido pequeño = Haiku
                estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
                return ModelRecommendation(
                    model_type=ModelType.HAIKU,
                    confidence=0.70,
                    reasoning="Regla semántica de baja criticidad: Claude Haiku para ahorro de costos",
                    estimated_cost=estimated_cost,
                    estimated_time=2.5,
                    fallback_model=ModelType.SONNET,
                    cost_optimization_applied=True
                )
            else:
                # Criticidad alta o contenido grande = Sonnet necesario
                estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.90,
                    reasoning="Regla semántica crítica: Claude Sonnet requerido pese a mayor costo",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0,
                    cost_optimization_applied=False
                )
        
        # Fallback
        return self._create_fallback_recommendation(rule, content_size)
    
    def _select_quality_optimized(self, rule: RuleData, content_size: int, 
                                context: Dict[str, Any]) -> ModelRecommendation:
        """
        Selección optimizada para maximizar calidad de resultados.
        
        Args:
            rule: Regla a validar
            content_size: Tamaño del contenido
            context: Contexto adicional
            
        Returns:
            ModelRecommendation: Recomendación optimizada por calidad
        """
        # Para reglas estructurales: lógica programada tiene alta calidad
        if rule.type.lower() == 'estructura':
            return ModelRecommendation(
                model_type=ModelType.STRUCTURAL_LOGIC,
                confidence=0.98,
                reasoning="Regla estructural: lógica programada ofrece máxima precisión",
                estimated_cost=0.0,
                estimated_time=0.1
            )
        
        # Para reglas de contenido y semánticas: priorizar Sonnet
        if rule.type.lower() in ['contenido', 'semántica']:
            estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
            
            # Solo usar Haiku si el contenido es muy simple
            if (rule.type.lower() == 'contenido' and 
                content_size < 10000 and 
                rule.criticality.lower() == 'baja'):
                estimated_cost_haiku = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
                return ModelRecommendation(
                    model_type=ModelType.HAIKU,
                    confidence=0.80,
                    reasoning="Contenido simple de baja criticidad: Haiku suficiente para calidad requerida",
                    estimated_cost=estimated_cost_haiku,
                    estimated_time=2.5,
                    fallback_model=ModelType.SONNET
                )
            else:
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.95,
                    reasoning="Priorizando máxima calidad: Claude Sonnet para análisis superior",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0
                )
        
        return self._create_fallback_recommendation(rule, content_size)
    
    def _select_balanced(self, rule: RuleData, content_size: int, 
                       context: Dict[str, Any]) -> ModelRecommendation:
        """
        Selección balanceada que considera costo, calidad y velocidad.
        
        Args:
            rule: Regla a validar
            content_size: Tamaño del contenido
            context: Contexto adicional
            
        Returns:
            ModelRecommendation: Recomendación balanceada
        """
        # Para reglas estructurales: siempre lógica programada (óptimo en todo)
        if rule.type.lower() == 'estructura':
            return ModelRecommendation(
                model_type=ModelType.STRUCTURAL_LOGIC,
                confidence=0.95,
                reasoning="Regla estructural: lógica programada es óptima en costo, calidad y velocidad",
                estimated_cost=0.0,
                estimated_time=0.1
            )
        
        # Para reglas de contenido: evaluar complejidad
        if rule.type.lower() == 'contenido':
            complexity_score = self._calculate_content_complexity(rule, content_size)
            
            if complexity_score < 0.5:  # Contenido simple
                estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
                return ModelRecommendation(
                    model_type=ModelType.HAIKU,
                    confidence=0.85,
                    reasoning="Contenido simple: Claude Haiku ofrece buen balance costo-calidad",
                    estimated_cost=estimated_cost,
                    estimated_time=2.5,
                    fallback_model=ModelType.SONNET
                )
            else:  # Contenido complejo
                estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.90,
                    reasoning="Contenido complejo: Claude Sonnet necesario para calidad adecuada",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0
                )
        
        # Para reglas semánticas: evaluar criticidad y complejidad
        if rule.type.lower() == 'semántica':
            complexity_score = self._calculate_semantic_complexity(rule, content_size)
            
            # Matriz de decisión criticidad vs complejidad
            if rule.criticality.lower() == 'alta' or complexity_score > 0.7:
                estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.95,
                    reasoning="Alta criticidad/complejidad semántica: Claude Sonnet requerido",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0
                )
            
            elif rule.criticality.lower() == 'media' and complexity_score > 0.4:
                estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.85,
                    reasoning="Criticidad media con complejidad: Claude Sonnet para balance óptimo",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0,
                    fallback_model=ModelType.HAIKU
                )
            
            else:  # Baja criticidad y baja complejidad
                estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
                return ModelRecommendation(
                    model_type=ModelType.HAIKU,
                    confidence=0.75,
                    reasoning="Baja criticidad semántica: Claude Haiku adecuado para balance",
                    estimated_cost=estimated_cost,
                    estimated_time=2.5,
                    fallback_model=ModelType.SONNET
                )
        
        return self._create_fallback_recommendation(rule, content_size)
    
    def _select_speed_optimized(self, rule: RuleData, content_size: int, 
                              context: Dict[str, Any]) -> ModelRecommendation:
        """
        Selección optimizada para maximizar velocidad de respuesta.
        
        Args:
            rule: Regla a validar
            content_size: Tamaño del contenido
            context: Contexto adicional
            
        Returns:
            ModelRecommendation: Recomendación optimizada por velocidad
        """
        # Para reglas estructurales: lógica programada (instantánea)
        if rule.type.lower() == 'estructura':
            return ModelRecommendation(
                model_type=ModelType.STRUCTURAL_LOGIC,
                confidence=0.95,
                reasoning="Regla estructural: lógica programada es instantánea",
                estimated_cost=0.0,
                estimated_time=0.1
            )
        
        # Para todas las demás: priorizar Haiku (más rápido)
        # Solo usar Sonnet si es absolutamente crítico
        if rule.criticality.lower() == 'alta' and rule.type.lower() == 'semántica':
            # Evaluar si podemos arriesgar velocidad por calidad
            complexity = self._calculate_semantic_complexity(rule, content_size)
            if complexity > 0.8:  # Muy complejo, necesita Sonnet
                estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                return ModelRecommendation(
                    model_type=ModelType.SONNET,
                    confidence=0.85,
                    reasoning="Semántica crítica muy compleja: Sonnet necesario pese a menor velocidad",
                    estimated_cost=estimated_cost,
                    estimated_time=5.0
                )
        
        # Default: usar Haiku para máxima velocidad
        estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
        return ModelRecommendation(
            model_type=ModelType.HAIKU,
            confidence=0.80,
            reasoning="Optimización de velocidad: Claude Haiku para respuesta rápida",
            estimated_cost=estimated_cost,
            estimated_time=2.5,
            fallback_model=ModelType.SONNET
        )
    
    def _calculate_content_complexity(self, rule: RuleData, content_size: int) -> float:
        """
        Calcula la complejidad del contenido para reglas de contenido.
        
        Args:
            rule: Regla de contenido
            content_size: Tamaño del contenido
            
        Returns:
            float: Score de complejidad entre 0.0 y 1.0
        """
        complexity_factors = []
        
        # Factor 1: Tamaño del contenido
        size_factor = min(content_size / 100000, 1.0)  # Normalizar a 100KB
        complexity_factors.append(size_factor * 0.4)
        
        # Factor 2: Palabras clave complejas en la descripción
        complex_keywords = ['patrón', 'regex', 'algoritmo', 'estructura', 'formato', 'validación']
        description_lower = rule.description.lower()
        keyword_matches = sum(1 for keyword in complex_keywords if keyword in description_lower)
        keyword_factor = min(keyword_matches / len(complex_keywords), 1.0)
        complexity_factors.append(keyword_factor * 0.3)
        
        # Factor 3: Explicación detallada indica complejidad
        explanation_factor = 0.0
        if rule.explanation:
            explanation_factor = min(len(rule.explanation) / 500, 1.0)  # Normalizar a 500 chars
        complexity_factors.append(explanation_factor * 0.3)
        
        return sum(complexity_factors)
    
    def _calculate_semantic_complexity(self, rule: RuleData, content_size: int) -> float:
        """
        Calcula la complejidad semántica de una regla.
        
        Args:
            rule: Regla semántica
            content_size: Tamaño del contenido
            
        Returns:
            float: Score de complejidad semántica entre 0.0 y 1.0
        """
        complexity_factors = []
        
        # Factor 1: Tamaño del contenido
        size_factor = min(content_size / 150000, 1.0)  # Normalizar a 150KB para semántica
        complexity_factors.append(size_factor * 0.3)
        
        # Factor 2: Palabras clave de alta complejidad semántica
        complex_semantic_keywords = [
            'arquitectura', 'patrones', 'diseño', 'calidad', 'buenas prácticas',
            'mantenibilidad', 'escalabilidad', 'performance', 'seguridad',
            'documentación', 'estilo', 'convenciones', 'estructura'
        ]
        description_lower = rule.description.lower()
        keyword_matches = sum(1 for keyword in complex_semantic_keywords if keyword in description_lower)
        keyword_factor = min(keyword_matches / 3, 1.0)  # Normalizar a 3 matches
        complexity_factors.append(keyword_factor * 0.4)
        
        # Factor 3: Criticidad implica complejidad
        criticality_factor = {
            'alta': 0.8,
            'media': 0.5,
            'baja': 0.2
        }.get(rule.criticality.lower(), 0.5)
        complexity_factors.append(criticality_factor * 0.3)
        
        return sum(complexity_factors)
    
    def _calculate_estimated_cost(self, model_type: ModelType, content_size: int) -> float:
        """
        Calcula el costo estimado para un modelo y tamaño de contenido.
        
        Args:
            model_type: Tipo de modelo
            content_size: Tamaño del contenido en caracteres
            
        Returns:
            float: Costo estimado en USD
        """
        if model_type == ModelType.STRUCTURAL_LOGIC:
            return 0.0
        
        capabilities = self.model_capabilities[model_type]
        
        # Estimar tokens (aproximación: 4 caracteres = 1 token)
        estimated_input_tokens = content_size // 4
        estimated_output_tokens = 200  # Promedio de respuesta
        
        # Calcular costo
        input_cost = (estimated_input_tokens / 1000) * capabilities.cost_per_1k_input_tokens
        output_cost = (estimated_output_tokens / 1000) * capabilities.cost_per_1k_output_tokens
        
        return input_cost + output_cost
    
    def _validate_and_adjust_recommendation(self, recommendation: ModelRecommendation, 
                                          rule: RuleData, content_size: int) -> ModelRecommendation:
        """
        Valida y ajusta la recomendación según restricciones del sistema.
        
        Args:
            recommendation: Recomendación inicial
            rule: Regla a validar
            content_size: Tamaño del contenido
            
        Returns:
            ModelRecommendation: Recomendación validada y ajustada
        """
        # Verificar límites de tokens
        if recommendation.model_type in [ModelType.HAIKU, ModelType.SONNET]:
            capabilities = self.model_capabilities[recommendation.model_type]
            estimated_tokens = content_size // 4
            
            if estimated_tokens > capabilities.max_tokens:
                logger.warning(f"Contenido excede límite de tokens para {recommendation.model_type.value}")
                
                # Ajustar recomendación
                if recommendation.model_type == ModelType.HAIKU:
                    # Upgrade a Sonnet si hay overflow
                    recommendation.model_type = ModelType.SONNET
                    recommendation.reasoning += " (actualizado a Sonnet por límite de tokens)"
                    recommendation.estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
                    recommendation.estimated_time = 5.0
                else:
                    # Si Sonnet también excede, necesitamos chunking
                    recommendation.reasoning += " (requiere chunking por límite de tokens)"
        
        # CORREGIDO: Bug #3 - Usar configuración centralizada sin hasattr
        if recommendation.estimated_cost > Config.MAX_COST_PER_VALIDATION:
            logger.warning(f"Costo estimado excede límite: ${recommendation.estimated_cost:.4f}")
            
            # Intentar downgrade si es posible
            if recommendation.model_type == ModelType.SONNET and rule.criticality.lower() != 'alta':
                recommendation.model_type = ModelType.HAIKU
                recommendation.reasoning = "Downgrade a Haiku por límite de costo"
                recommendation.estimated_cost = self._calculate_estimated_cost(ModelType.HAIKU, content_size)
                recommendation.estimated_time = 2.5
                recommendation.cost_optimization_applied = True
        
        return recommendation
    
    def _create_fallback_recommendation(self, rule: RuleData, content_size: int) -> ModelRecommendation:
        """
        Crea una recomendación de fallback segura.
        
        Args:
            rule: Regla a validar
            content_size: Tamaño del contenido
            
        Returns:
            ModelRecommendation: Recomendación de fallback
        """
        # Fallback conservador: usar Sonnet para máxima confiabilidad
        estimated_cost = self._calculate_estimated_cost(ModelType.SONNET, content_size)
        
        return ModelRecommendation(
            model_type=ModelType.SONNET,
            confidence=0.70,
            reasoning="Fallback de seguridad: Claude Sonnet para máxima confiabilidad",
            estimated_cost=estimated_cost,
            estimated_time=5.0,
            fallback_model=ModelType.HAIKU
        )
    
    def _record_selection(self, recommendation: ModelRecommendation, rule: RuleData, 
                        content_size: int, strategy: str):
        """
        Registra la selección para análisis y optimización futura.
        
        Args:
            recommendation: Recomendación seleccionada
            rule: Regla validada
            content_size: Tamaño del contenido
            strategy: Estrategia utilizada
        """
        selection_record = {
            'rule_id': rule.id,
            'rule_type': rule.type,
            'rule_criticality': rule.criticality,
            'content_size': content_size,
            'strategy': strategy,
            'selected_model': recommendation.model_type.value,
            'confidence': recommendation.confidence,
            'estimated_cost': recommendation.estimated_cost,
            'estimated_time': recommendation.estimated_time,
            'reasoning': recommendation.reasoning,
            'cost_optimization_applied': recommendation.cost_optimization_applied
        }
        
        self.selection_history.append(selection_record)
        
        # Actualizar estadísticas de costo
        self.cost_tracking['total_estimated_cost'] += recommendation.estimated_cost
        
        model_name = recommendation.model_type.value
        self.cost_tracking['model_usage_count'][model_name] = (
            self.cost_tracking['model_usage_count'].get(model_name, 0) + 1
        )
        self.cost_tracking['cost_by_model'][model_name] = (
            self.cost_tracking['cost_by_model'].get(model_name, 0.0) + recommendation.estimated_cost
        )
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        """
        Obtiene análisis de costos de las selecciones realizadas.
        
        Returns:
            dict: Análisis detallado de costos
        """
        total_selections = len(self.selection_history)
        
        if total_selections == 0:
            return {
                'total_selections': 0,
                'total_estimated_cost': 0.0,
                'average_cost_per_selection': 0.0,
                'model_usage': {},
                'cost_efficiency': 'unknown'
            }
        
        # Calcular costo promedio
        avg_cost = self.cost_tracking['total_estimated_cost'] / total_selections
        
        # Calcular eficiencia de costo
        cost_efficiency = 'high'
        if avg_cost > 0.1:
            cost_efficiency = 'low'
        elif avg_cost > 0.05:
            cost_efficiency = 'medium'
        
        # Análisis por modelo
        model_analysis = {}
        for model, usage_count in self.cost_tracking['model_usage_count'].items():
            model_cost = self.cost_tracking['cost_by_model'].get(model, 0.0)
            model_analysis[model] = {
                'usage_count': usage_count,
                'total_cost': model_cost,
                'average_cost': model_cost / usage_count if usage_count > 0 else 0.0,
                'usage_percentage': (usage_count / total_selections) * 100
            }
        
        return {
            'total_selections': total_selections,
            'total_estimated_cost': self.cost_tracking['total_estimated_cost'],
            'average_cost_per_selection': avg_cost,
            'model_usage': model_analysis,
            'cost_efficiency': cost_efficiency,
            'optimization_applied_count': sum(
                1 for record in self.selection_history 
                if record.get('cost_optimization_applied', False)
            )
        }
    
    def get_selection_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las selecciones realizadas.
        
        Returns:
            dict: Estadísticas detalladas de selecciones
        """
        if not self.selection_history:
            return {'message': 'No hay selecciones registradas'}
        
        # Estadísticas por estrategia
        strategy_stats = {}
        for record in self.selection_history:
            strategy = record['strategy']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'count': 0, 'avg_confidence': 0.0}
            
            strategy_stats[strategy]['count'] += 1
            strategy_stats[strategy]['avg_confidence'] += record['confidence']
        
        # Calcular promedios
        for strategy, stats in strategy_stats.items():
            stats['avg_confidence'] /= stats['count']
        
        # Estadísticas por tipo de regla
        rule_type_stats = {}
        for record in self.selection_history:
            rule_type = record['rule_type']
            if rule_type not in rule_type_stats:
                rule_type_stats[rule_type] = {
                    'count': 0,
                    'preferred_models': {},
                    'avg_cost': 0.0
                }
            
            rule_type_stats[rule_type]['count'] += 1
            rule_type_stats[rule_type]['avg_cost'] += record['estimated_cost']
            
            model = record['selected_model']
            rule_type_stats[rule_type]['preferred_models'][model] = (
                rule_type_stats[rule_type]['preferred_models'].get(model, 0) + 1
            )
        
        # Calcular promedios y modelos preferidos
        for rule_type, stats in rule_type_stats.items():
            stats['avg_cost'] /= stats['count']
            stats['most_used_model'] = max(
                stats['preferred_models'].items(), 
                key=lambda x: x[1]
            )[0] if stats['preferred_models'] else 'none'
        
        return {
            'total_selections': len(self.selection_history),
            'strategy_statistics': strategy_stats,
            'rule_type_statistics': rule_type_stats,
            'average_confidence': sum(r['confidence'] for r in self.selection_history) / len(self.selection_history),
            'cost_analysis': self.get_cost_analysis()
        }
    
    def optimize_for_batch(self, rules: List[RuleData], content_sizes: List[int]) -> Dict[str, Any]:
        """
        Optimiza selección de modelos para un lote de reglas.
        
        Args:
            rules: Lista de reglas a procesar
            content_sizes: Tamaños de contenido correspondientes
            
        Returns:
            dict: Optimización para el lote completo
        """
        batch_recommendations = []
        total_estimated_cost = 0.0
        total_estimated_time = 0.0
        
        # Generar recomendaciones individuales
        for rule, content_size in zip(rules, content_sizes):
            recommendation = self.select_optimal_model(rule, content_size, strategy='balanced')
            batch_recommendations.append(recommendation)
            total_estimated_cost += recommendation.estimated_cost
            total_estimated_time += recommendation.estimated_time
        
        # Análisis del lote
        model_distribution = {}
        for recommendation in batch_recommendations:
            model = recommendation.model_type.value
            model_distribution[model] = model_distribution.get(model, 0) + 1
        
        # Identificar oportunidades de optimización
        optimization_opportunities = []
        expensive_validations = [
            r for r in batch_recommendations 
            if r.estimated_cost > 0.1
        ]
        
        if expensive_validations:
            optimization_opportunities.append(
                f"Considerar revisar {len(expensive_validations)} validaciones costosas"
            )
        
        # Estimación de tiempo de ejecución paralela
        max_estimated_time = max(r.estimated_time for r in batch_recommendations)
        
        return {
            'batch_size': len(rules),
            'recommendations': batch_recommendations,
            'total_estimated_cost': total_estimated_cost,
            'total_estimated_time_sequential': total_estimated_time,
            'estimated_time_parallel': max_estimated_time,
            'model_distribution': model_distribution,
            'optimization_opportunities': optimization_opportunities,
            'cost_efficiency': 'high' if total_estimated_cost < 0.5 else 'medium' if total_estimated_cost < 1.0 else 'low'
        }