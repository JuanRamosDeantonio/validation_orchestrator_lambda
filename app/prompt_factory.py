"""
prompt_factory.py - Fábrica de prompts especializados
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from utils import setup_logger, Config, estimate_tokens
from models import RuleData, ChunkData

# Configurar logging
logger = setup_logger(__name__)

class PromptType(Enum):
    """Tipos de prompts disponibles."""
    STRUCTURAL = "structural"
    CONTENT = "content"
    SEMANTIC = "semantic"
    CHUNK = "chunk"
    FALLBACK = "fallback"

class ModelOptimization(Enum):
    """Optimizaciones específicas por modelo."""
    HAIKU_CONCISE = "haiku_concise"
    SONNET_DETAILED = "sonnet_detailed"
    GENERIC = "generic"

@dataclass
class PromptTemplate:
    """Template de prompt con metadata."""
    template: str
    description: str
    optimal_for_models: List[str]
    estimated_tokens: int
    response_format: str
    validation_keywords: List[str]

@dataclass
class BuiltPrompt:
    """Prompt construido con metadata."""
    content: str
    prompt_type: PromptType
    model_optimization: ModelOptimization
    estimated_tokens: int
    rule_id: str
    contains_context: bool
    chunk_info: Optional[Dict[str, Any]] = None

class PromptFactory:
    """
    Fábrica especializada en construcción de prompts optimizados.
    
    Genera prompts específicos para cada tipo de regla, modelo de IA y contexto,
    optimizando para calidad de respuesta, límites de tokens y costos.
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.model_optimizations = self._initialize_model_optimizations()
        self.prompt_cache = {}
        self.prompt_statistics = {
            'prompts_generated': 0,
            'cache_hits': 0,
            'prompts_by_type': {},
            'average_prompt_size': 0
        }
        
    def _initialize_templates(self) -> Dict[PromptType, Dict[str, PromptTemplate]]:
        """
        Inicializa templates de prompts para cada tipo de validación.
        
        Returns:
            dict: Templates organizados por tipo de prompt
        """
        return {
            PromptType.STRUCTURAL: {
                'file_existence': PromptTemplate(
                    template="""Eres un validador de estructura de repositorios. Analiza si los archivos requeridos están presentes.

REGLA ESTRUCTURAL:
- ID: {rule_id}
- Descripción: {rule_description}
- Archivos requeridos: {required_files}

CONTENIDO DEL REPOSITORIO:
{content}

INSTRUCCIONES:
1. Verifica ÚNICAMENTE la presencia de los archivos especificados
2. Ignora la calidad o contenido de los archivos
3. Responde de forma directa y precisa

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Una línea indicando qué archivos están presentes o faltantes]

RESPUESTA:""",
                    description="Validación de existencia de archivos requeridos",
                    optimal_for_models=["claude-3-haiku", "claude-3-sonnet"],
                    estimated_tokens=250,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["archivos", "presencia", "estructura"]
                ),
                
                'directory_structure': PromptTemplate(
                    template="""Eres un validador de estructura de directorios. Analiza la organización del repositorio.

REGLA ESTRUCTURAL:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}

ESTRUCTURA DETECTADA:
{content}

INSTRUCCIONES:
1. Evalúa si la estructura de directorios cumple con: "{rule_description}"
2. Considera buenas prácticas de organización de proyectos
3. Ignora el contenido específico de los archivos

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Una línea sobre la estructura organizacional]

RESPUESTA:""",
                    description="Validación de estructura de directorios",
                    optimal_for_models=["claude-3-haiku", "claude-3-sonnet"],
                    estimated_tokens=280,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["estructura", "directorios", "organización"]
                )
            },
            
            PromptType.CONTENT: {
                'pattern_search': PromptTemplate(
                    template="""Eres un validador de contenido especializado en búsqueda de patrones. Analiza el contenido según la regla específica.

REGLA DE CONTENIDO:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}
- Contexto: {rule_explanation}

IMPORTANTE: Enfócate ÚNICAMENTE en esta regla. Ignora otros aspectos del código.

CONTENIDO A ANALIZAR:
{content}

INSTRUCCIONES:
1. Busca específicamente lo indicado en: "{rule_description}"
2. Considera el nivel de criticidad: {rule_criticality}
3. Proporciona evidencia específica si encuentras problemas
4. Sé preciso en tu análisis

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Máximo 2 líneas con evidencia específica]

RESPUESTA:""",
                    description="Búsqueda de patrones específicos en contenido",
                    optimal_for_models=["claude-3-haiku"],
                    estimated_tokens=320,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["patrones", "búsqueda", "contenido"]
                ),
                
                'security_check': PromptTemplate(
                    template="""Eres un validador de seguridad especializado. Analiza el código buscando vulnerabilidades específicas.

REGLA DE SEGURIDAD:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}

CÓDIGO A REVISAR:
{content}

INSTRUCCIONES DE SEGURIDAD:
1. Busca ÚNICAMENTE: "{rule_description}"
2. Identifica líneas específicas con problemas
3. Considera el contexto de seguridad
4. Proporciona ubicación exacta si encuentras issues

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Ubicación específica y tipo de problema encontrado]

RESPUESTA:""",
                    description="Validación de aspectos de seguridad",
                    optimal_for_models=["claude-3-sonnet"],
                    estimated_tokens=350,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["seguridad", "vulnerabilidades", "código"]
                )
            },
            
            PromptType.SEMANTIC: {
                'code_quality': PromptTemplate(
                    template="""Eres un experto en calidad de código y buenas prácticas de desarrollo. Realiza un análisis semántico profundo.

REGLA SEMÁNTICA:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}
- Contexto adicional: {rule_explanation}

ENFOQUE SEMÁNTICO: Analiza la intención, calidad, mantenibilidad y buenas prácticas del código.

CÓDIGO A ANALIZAR:
{content}

INSTRUCCIONES ESPECÍFICAS:
1. Evalúa semánticamente: "{rule_description}"
2. Considera patrones, claridad del código y buenas prácticas
3. Analiza la intención y diseño del código
4. El nivel de criticidad es: {rule_criticality}
5. Proporciona análisis constructivo y específico

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Máximo 2 líneas con análisis semántico específico]

RESPUESTA:""",
                    description="Análisis semántico de calidad de código",
                    optimal_for_models=["claude-3-sonnet"],
                    estimated_tokens=420,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["calidad", "semántica", "buenas prácticas"]
                ),
                
                'architecture_analysis': PromptTemplate(
                    template="""Eres un arquitecto de software experto. Analiza la arquitectura y patrones de diseño del código.

REGLA ARQUITECTURAL:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}
- Contexto: {rule_explanation}

ENFOQUE ARQUITECTURAL: Evalúa patrones, estructura, separación de responsabilidades y diseño general.

CÓDIGO Y ESTRUCTURA:
{content}

INSTRUCCIONES ARQUITECTURALES:
1. Analiza específicamente: "{rule_description}"
2. Evalúa patrones de diseño utilizados
3. Considera principios SOLID y buenas prácticas arquitecturales
4. Analiza la escalabilidad y mantenibilidad del diseño
5. Nivel de criticidad: {rule_criticality}

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Análisis arquitectural específico en máximo 2 líneas]

RESPUESTA:""",
                    description="Análisis de arquitectura y patrones de diseño",
                    optimal_for_models=["claude-3-sonnet"],
                    estimated_tokens=450,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["arquitectura", "patrones", "diseño"]
                ),
                
                'documentation_quality': PromptTemplate(
                    template="""Eres un experto en documentación técnica. Analiza la calidad y completitud de la documentación.

REGLA DE DOCUMENTACIÓN:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}
- Contexto: {rule_explanation}

ENFOQUE EN DOCUMENTACIÓN: Evalúa claridad, completitud, utilidad y mantenimiento de la documentación.

DOCUMENTACIÓN A REVISAR:
{content}

INSTRUCCIONES DE DOCUMENTACIÓN:
1. Evalúa específicamente: "{rule_description}"
2. Considera claridad, completitud y utilidad
3. Verifica que la documentación sea mantenible y actualizada
4. Analiza si facilita el entendimiento y uso del código
5. Criticidad del análisis: {rule_criticality}

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Evaluación específica de la documentación en máximo 2 líneas]

RESPUESTA:""",
                    description="Análisis de calidad de documentación",
                    optimal_for_models=["claude-3-sonnet"],
                    estimated_tokens=400,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["documentación", "claridad", "completitud"]
                )
            },
            
            PromptType.CHUNK: {
                'chunk_analysis': PromptTemplate(
                    template="""Eres un validador experto. Analiza este fragmento de código según la regla específica.

REGLA A VALIDAR:
- ID: {rule_id}
- Descripción: {rule_description}
- Criticidad: {rule_criticality}

CONTEXTO DEL ANÁLISIS:
- Fragmento {chunk_number} de {total_chunks}
- Tipo de contenido: {chunk_type}
- Análisis enfocado en la regla específica

FRAGMENTO DE CÓDIGO:
{content}

INSTRUCCIONES PARA FRAGMENTO:
1. Analiza SOLO este fragmento en relación a: "{rule_description}"
2. Si es fragmento parcial, evalúa lo que SÍ puedes determinar
3. Indica tu nivel de confianza basado en la completitud del fragmento
4. No hagas suposiciones sobre código no visible

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE/PARCIAL]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Evaluación específica de este fragmento]

RESPUESTA:""",
                    description="Análisis de fragmentos de código (chunking)",
                    optimal_for_models=["claude-3-sonnet", "claude-3-haiku"],
                    estimated_tokens=380,
                    response_format="RESULTADO/CONFIANZA/EXPLICACIÓN",
                    validation_keywords=["fragmento", "chunk", "parcial"]
                )
            }
        }
    
    def _initialize_model_optimizations(self) -> Dict[ModelOptimization, Dict[str, Any]]:
        """
        Inicializa optimizaciones específicas por modelo.
        
        Returns:
            dict: Configuraciones de optimización por modelo
        """
        return {
            ModelOptimization.HAIKU_CONCISE: {
                'max_prompt_tokens': 8000,
                'response_style': 'conciso',
                'instruction_style': 'directo',
                'context_reduction': 0.3,  # Reducir contexto 30%
                'template_modifiers': {
                    'remove_examples': True,
                    'simplify_instructions': True,
                    'reduce_context_explanation': True
                }
            },
            
            ModelOptimization.SONNET_DETAILED: {
                'max_prompt_tokens': 15000,
                'response_style': 'detallado',
                'instruction_style': 'explicativo',
                'context_reduction': 0.0,  # Sin reducción de contexto
                'template_modifiers': {
                    'add_examples': True,
                    'detailed_instructions': True,
                    'include_context_explanation': True
                }
            },
            
            ModelOptimization.GENERIC: {
                'max_prompt_tokens': 10000,
                'response_style': 'balanceado',
                'instruction_style': 'claro',
                'context_reduction': 0.1,
                'template_modifiers': {
                    'standard_format': True
                }
            }
        }
    
    def build_prompt(self, rule: RuleData, content: str, model_type: str = "claude-3-sonnet",
                    chunk_info: Optional[Dict[str, Any]] = None) -> BuiltPrompt:
        """
        Construye un prompt optimizado para una regla específica.
        
        Args:
            rule: Regla para la cual construir el prompt
            content: Contenido a incluir en el prompt
            model_type: Tipo de modelo de IA que usará el prompt
            chunk_info: Información de chunk si aplica
            
        Returns:
            BuiltPrompt: Prompt construido y optimizado
        """
        try:
            logger.debug(f"Construyendo prompt para regla {rule.id} ({rule.type}) con modelo {model_type}")
            
            # Determinar tipo de prompt y template
            prompt_type = self._determine_prompt_type(rule, chunk_info)
            template_key = self._select_template(rule, prompt_type)
            
            # Determinar optimización del modelo
            model_optimization = self._determine_model_optimization(model_type)
            
            # Construir prompt base
            base_prompt = self._build_base_prompt(rule, content, prompt_type, template_key, chunk_info)
            
            # Aplicar optimizaciones del modelo
            optimized_prompt = self._apply_model_optimizations(base_prompt, model_optimization, rule)
            
            # Validar y ajustar prompt
            final_prompt = self._validate_and_adjust_prompt(optimized_prompt, model_optimization)
            
            # Crear objeto BuiltPrompt
            built_prompt = BuiltPrompt(
                content=final_prompt,
                prompt_type=prompt_type,
                model_optimization=model_optimization,
                estimated_tokens=estimate_tokens(final_prompt),
                rule_id=rule.id,
                contains_context=bool(rule.explanation),
                chunk_info=chunk_info
            )
            
            # Registrar estadísticas
            self._record_prompt_statistics(built_prompt)
            
            logger.debug(f"Prompt construido exitosamente: {built_prompt.estimated_tokens} tokens estimados")
            
            return built_prompt
            
        except Exception as e:
            logger.error(f"Error construyendo prompt para regla {rule.id}: {str(e)}")
            return self._create_fallback_prompt(rule, content, model_type)
    
    def _determine_prompt_type(self, rule: RuleData, chunk_info: Optional[Dict[str, Any]]) -> PromptType:
        """
        Determina el tipo de prompt basado en la regla y contexto.
        
        Args:
            rule: Regla a analizar
            chunk_info: Información de chunk si aplica
            
        Returns:
            PromptType: Tipo de prompt determinado
        """
        # Si hay chunk info, es un prompt de chunk
        if chunk_info:
            return PromptType.CHUNK
        
        # Determinar por tipo de regla
        rule_type = rule.type.lower()
        
        if rule_type == 'estructura':
            return PromptType.STRUCTURAL
        elif rule_type == 'contenido':
            return PromptType.CONTENT
        elif rule_type == 'semántica':
            return PromptType.SEMANTIC
        else:
            logger.warning(f"Tipo de regla desconocido: {rule_type}, usando fallback")
            return PromptType.FALLBACK
    
    def _select_template(self, rule: RuleData, prompt_type: PromptType) -> str:
        """
        Selecciona el template más apropiado para la regla.
        
        Args:
            rule: Regla que guía la selección
            prompt_type: Tipo de prompt
            
        Returns:
            str: Clave del template seleccionado
        """
        if prompt_type == PromptType.CHUNK:
            return 'chunk_analysis'
        
        # Selección específica por tipo y descripción
        description_lower = rule.description.lower()
        
        if prompt_type == PromptType.STRUCTURAL:
            if any(keyword in description_lower for keyword in ['archivo', 'existe', 'presente']):
                return 'file_existence'
            else:
                return 'directory_structure'
        
        elif prompt_type == PromptType.CONTENT:
            if any(keyword in description_lower for keyword in ['seguridad', 'vulnerabilidad', 'secreto']):
                return 'security_check'
            else:
                return 'pattern_search'
        
        elif prompt_type == PromptType.SEMANTIC:
            if any(keyword in description_lower for keyword in ['arquitectura', 'diseño', 'patrón']):
                return 'architecture_analysis'
            elif any(keyword in description_lower for keyword in ['documentación', 'comentario', 'doc']):
                return 'documentation_quality'
            else:
                return 'code_quality'
        
        # Fallback
        logger.warning(f"No se pudo determinar template específico para regla {rule.id}")
        return list(self.templates[prompt_type].keys())[0]
    
    def _determine_model_optimization(self, model_type: str) -> ModelOptimization:
        """
        Determina la optimización apropiada para el modelo.
        
        Args:
            model_type: Tipo de modelo de IA
            
        Returns:
            ModelOptimization: Optimización del modelo
        """
        if 'haiku' in model_type.lower():
            return ModelOptimization.HAIKU_CONCISE
        elif 'sonnet' in model_type.lower():
            return ModelOptimization.SONNET_DETAILED
        else:
            return ModelOptimization.GENERIC
    
    def _build_base_prompt(self, rule: RuleData, content: str, prompt_type: PromptType,
                          template_key: str, chunk_info: Optional[Dict[str, Any]]) -> str:
        """
        Construye el prompt base usando el template seleccionado.
        
        Args:
            rule: Regla para el prompt
            content: Contenido a incluir
            prompt_type: Tipo de prompt
            template_key: Clave del template
            chunk_info: Información de chunk si aplica
            
        Returns:
            str: Prompt base construido
        """
        template = self.templates[prompt_type][template_key].template
        
        # Variables base para todos los templates
        template_vars = {
            'rule_id': rule.id,
            'rule_description': rule.description,
            'rule_criticality': rule.criticality,
            'rule_explanation': rule.explanation or 'No especificado',
            'content': content
        }
        
        # Variables específicas para chunks
        if chunk_info:
            template_vars.update({
                'chunk_number': chunk_info.get('chunk_number', 1),
                'total_chunks': chunk_info.get('total_chunks', 1),
                'chunk_type': chunk_info.get('chunk_type', 'general')
            })
        
        # Variables específicas para reglas estructurales
        if prompt_type == PromptType.STRUCTURAL:
            template_vars['required_files'] = ', '.join(rule.references)
        
        try:
            return template.format(**template_vars)
        except KeyError as e:
            logger.error(f"Error en template para regla {rule.id}: variable faltante {str(e)}")
            # Usar template genérico como fallback
            return self._build_generic_prompt(rule, content)
    
    def _apply_model_optimizations(self, prompt: str, optimization: ModelOptimization, 
                                 rule: RuleData) -> str:
        """
        Aplica optimizaciones específicas del modelo al prompt.
        
        Args:
            prompt: Prompt base
            optimization: Configuración de optimización
            rule: Regla original
            
        Returns:
            str: Prompt optimizado
        """
        config = self.model_optimizations[optimization]
        
        # Aplicar reducción de contexto si es necesario
        if config['context_reduction'] > 0:
            prompt = self._reduce_context(prompt, config['context_reduction'])
        
        # Aplicar modificadores de template
        modifiers = config.get('template_modifiers', {})
        
        if modifiers.get('simplify_instructions'):
            prompt = self._simplify_instructions(prompt)
        
        if modifiers.get('reduce_context_explanation'):
            prompt = self._reduce_context_explanation(prompt)
        
        # Verificar límite de tokens
        max_tokens = config['max_prompt_tokens']
        if estimate_tokens(prompt) > max_tokens:
            prompt = self._truncate_prompt_smartly(prompt, max_tokens)
        
        return prompt
    
    def _reduce_context(self, prompt: str, reduction_factor: float) -> str:
        """
        Reduce el contexto del prompt manteniendo información esencial.
        
        Args:
            prompt: Prompt original
            reduction_factor: Factor de reducción (0.0-1.0)
            
        Returns:
            str: Prompt con contexto reducido
        """
        if reduction_factor <= 0:
            return prompt
        
        # Identificar sección de contenido
        content_start = prompt.find("CONTENIDO")
        if content_start == -1:
            return prompt
        
        # Dividir prompt en partes
        header = prompt[:content_start]
        content_section = prompt[content_start:]
        
        # Reducir solo la sección de contenido
        lines = content_section.split('\n')
        keep_lines = int(len(lines) * (1 - reduction_factor))
        
        if keep_lines < len(lines):
            reduced_lines = lines[:keep_lines]
            reduced_lines.append("... [contenido reducido para optimización]")
            content_section = '\n'.join(reduced_lines)
        
        return header + content_section
    
    def _simplify_instructions(self, prompt: str) -> str:
        """
        Simplifica las instrucciones del prompt para modelos rápidos.
        
        Args:
            prompt: Prompt original
            
        Returns:
            str: Prompt con instrucciones simplificadas
        """
        # Simplificar sección de instrucciones
        prompt = prompt.replace("INSTRUCCIONES ESPECÍFICAS:", "INSTRUCCIONES:")
        prompt = prompt.replace("INSTRUCCIONES PARA FRAGMENTO:", "INSTRUCCIONES:")
        prompt = prompt.replace("INSTRUCCIONES ARQUITECTURALES:", "INSTRUCCIONES:")
        prompt = prompt.replace("INSTRUCCIONES DE DOCUMENTACIÓN:", "INSTRUCCIONES:")
        prompt = prompt.replace("INSTRUCCIONES DE SEGURIDAD:", "INSTRUCCIONES:")
        
        return prompt
    
    def _reduce_context_explanation(self, prompt: str) -> str:
        """
        Reduce explicaciones contextuales para optimizar velocidad.
        
        Args:
            prompt: Prompt original
            
        Returns:
            str: Prompt con contexto reducido
        """
        # Remover líneas explicativas opcionales
        lines = prompt.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Mantener líneas esenciales
            if any(essential in line for essential in [
                'REGLA', 'RESULTADO:', 'CONFIANZA:', 'EXPLICACIÓN:', 
                'RESPUESTA:', 'INSTRUCCIONES:', 'CONTENIDO', 'CÓDIGO'
            ]):
                filtered_lines.append(line)
            # Remover líneas muy explicativas
            elif not any(skip in line for skip in [
                'Considera', 'Recuerda', 'Ten en cuenta', 'Es importante'
            ]):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _truncate_prompt_smartly(self, prompt: str, max_tokens: int) -> str:
        """
        Trunca el prompt de manera inteligente preservando estructura esencial.
        
        Args:
            prompt: Prompt a truncar
            max_tokens: Máximo de tokens permitidos
            
        Returns:
            str: Prompt truncado inteligentemente
        """
        # Calcular tokens objetivo (dejar margen para respuesta)
        target_tokens = max_tokens - 500  # Reservar 500 tokens para respuesta
        
        if estimate_tokens(prompt) <= target_tokens:
            return prompt
        
        # Dividir en secciones
        sections = prompt.split('\n\n')
        essential_sections = []
        content_sections = []
        
        for section in sections:
            if any(essential in section for essential in [
                'REGLA', 'FORMATO DE RESPUESTA', 'RESPUESTA:', 'INSTRUCCIONES'
            ]):
                essential_sections.append(section)
            else:
                content_sections.append(section)
        
        # Reconstruir manteniendo esenciales y truncando contenido
        truncated_prompt = '\n\n'.join(essential_sections)
        remaining_tokens = target_tokens - estimate_tokens(truncated_prompt)
        
        # Agregar contenido hasta el límite
        for section in content_sections:
            section_tokens = estimate_tokens(section)
            if remaining_tokens >= section_tokens:
                truncated_prompt += '\n\n' + section
                remaining_tokens -= section_tokens
            else:
                # Truncar la sección parcialmente
                max_chars = remaining_tokens * 4  # Aproximación tokens->chars
                if max_chars > 100:  # Solo si vale la pena
                    truncated_section = section[:max_chars] + "\n... [contenido truncado]"
                    truncated_prompt += '\n\n' + truncated_section
                break
        
        return truncated_prompt
    
    def _validate_and_adjust_prompt(self, prompt: str, optimization: ModelOptimization) -> str:
        """
        Valida y ajusta el prompt final.
        
        Args:
            prompt: Prompt a validar
            optimization: Configuración de optimización
            
        Returns:
            str: Prompt validado y ajustado
        """
        # Verificar que tenga elementos esenciales
        required_elements = ['REGLA', 'RESULTADO:', 'RESPUESTA:']
        for element in required_elements:
            if element not in prompt:
                logger.warning(f"Prompt carece de elemento esencial: {element}")
        
        # Verificar formato de respuesta
        if 'FORMATO DE RESPUESTA' not in prompt:
            prompt += "\n\nFORMATO DE RESPUESTA:\nRESULTADO: [CUMPLE/NO_CUMPLE]\nCONFIANZA: [Alta/Media/Baja]\nEXPLICACIÓN: [Análisis específico]\n"
        
        # Asegurar que termine con RESPUESTA:
        if not prompt.rstrip().endswith('RESPUESTA:'):
            prompt += '\n\nRESPUESTA:'
        
        return prompt
    
    def _build_generic_prompt(self, rule: RuleData, content: str) -> str:
        """
        Construye un prompt genérico como fallback.
        
        Args:
            rule: Regla a validar
            content: Contenido a incluir
            
        Returns:
            str: Prompt genérico
        """
        return f"""Eres un validador experto. Analiza el contenido según la regla específica.

REGLA A VALIDAR:
- ID: {rule.id}
- Descripción: {rule.description}
- Criticidad: {rule.criticality}

CONTENIDO:
{content}

INSTRUCCIONES:
1. Evalúa si cumple con: "{rule.description}"
2. Considera la criticidad: {rule.criticality}
3. Proporciona análisis específico

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Análisis específico]

RESPUESTA:"""
    
    def _create_fallback_prompt(self, rule: RuleData, content: str, model_type: str) -> BuiltPrompt:
        """
        Crea un prompt de fallback en caso de error.
        
        Args:
            rule: Regla original
            content: Contenido original
            model_type: Tipo de modelo
            
        Returns:
            BuiltPrompt: Prompt de fallback
        """
        logger.warning(f"Creando prompt de fallback para regla {rule.id}")
        
        fallback_content = self._build_generic_prompt(rule, content)
        
        return BuiltPrompt(
            content=fallback_content,
            prompt_type=PromptType.FALLBACK,
            model_optimization=ModelOptimization.GENERIC,
            estimated_tokens=estimate_tokens(fallback_content),
            rule_id=rule.id,
            contains_context=bool(rule.explanation)
        )
    
    def _record_prompt_statistics(self, built_prompt: BuiltPrompt):
        """
        Registra estadísticas del prompt generado.
        
        Args:
            built_prompt: Prompt construido
        """
        self.prompt_statistics['prompts_generated'] += 1
        
        prompt_type = built_prompt.prompt_type.value
        if prompt_type not in self.prompt_statistics['prompts_by_type']:
            self.prompt_statistics['prompts_by_type'][prompt_type] = 0
        self.prompt_statistics['prompts_by_type'][prompt_type] += 1
        
        # Actualizar tamaño promedio
        total_prompts = self.prompt_statistics['prompts_generated']
        current_avg = self.prompt_statistics['average_prompt_size']
        new_avg = ((current_avg * (total_prompts - 1)) + built_prompt.estimated_tokens) / total_prompts
        self.prompt_statistics['average_prompt_size'] = new_avg
    
    def build_batch_prompts(self, rules_content_pairs: List[Tuple[RuleData, str]], 
                          model_type: str = "claude-3-sonnet") -> List[BuiltPrompt]:
        """
        Construye múltiples prompts de manera optimizada.
        
        Args:
            rules_content_pairs: Lista de tuplas (regla, contenido)
            model_type: Tipo de modelo a usar
            
        Returns:
            list: Lista de prompts construidos
        """
        logger.info(f"Construyendo lote de {len(rules_content_pairs)} prompts")
        
        built_prompts = []
        
        for rule, content in rules_content_pairs:
            try:
                built_prompt = self.build_prompt(rule, content, model_type)
                built_prompts.append(built_prompt)
                
            except Exception as e:
                logger.error(f"Error en lote para regla {rule.id}: {str(e)}")
                fallback_prompt = self._create_fallback_prompt(rule, content, model_type)
                built_prompts.append(fallback_prompt)
        
        logger.info(f"Lote completado: {len(built_prompts)} prompts generados")
        
        return built_prompts
    
    def optimize_prompts_for_cost(self, built_prompts: List[BuiltPrompt]) -> List[BuiltPrompt]:
        """
        Optimiza prompts existentes para reducir costos.
        
        Args:
            built_prompts: Lista de prompts a optimizar
            
        Returns:
            list: Prompts optimizados para costo
        """
        logger.info("Optimizando prompts para reducción de costos")
        
        optimized_prompts = []
        
        for prompt in built_prompts:
            # Solo optimizar prompts grandes
            if prompt.estimated_tokens > 5000:
                # Aplicar optimización Haiku
                optimized_content = self._apply_model_optimizations(
                    prompt.content, 
                    ModelOptimization.HAIKU_CONCISE,
                    None  # No necesitamos regla para optimización
                )
                
                optimized_prompt = BuiltPrompt(
                    content=optimized_content,
                    prompt_type=prompt.prompt_type,
                    model_optimization=ModelOptimization.HAIKU_CONCISE,
                    estimated_tokens=estimate_tokens(optimized_content),
                    rule_id=prompt.rule_id,
                    contains_context=prompt.contains_context,
                    chunk_info=prompt.chunk_info
                )
                
                optimized_prompts.append(optimized_prompt)
                
                logger.debug(f"Prompt {prompt.rule_id} optimizado: "
                           f"{prompt.estimated_tokens} → {optimized_prompt.estimated_tokens} tokens")
            else:
                optimized_prompts.append(prompt)
        
        return optimized_prompts
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la fábrica de prompts.
        
        Returns:
            dict: Estadísticas detalladas
        """
        return {
            'total_prompts_generated': self.prompt_statistics['prompts_generated'],
            'cache_hits': self.prompt_statistics['cache_hits'],
            'cache_hit_rate': (
                self.prompt_statistics['cache_hits'] / self.prompt_statistics['prompts_generated'] * 100
                if self.prompt_statistics['prompts_generated'] > 0 else 0
            ),
            'prompts_by_type': self.prompt_statistics['prompts_by_type'],
            'average_prompt_size': round(self.prompt_statistics['average_prompt_size']),
            'available_templates': {
                prompt_type.value: list(templates.keys())
                for prompt_type, templates in self.templates.items()
            },
            'model_optimizations': list(self.model_optimizations.keys())
        }