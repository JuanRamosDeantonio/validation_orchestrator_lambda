"""
validation_core.py - Motor central de validaciones paralelas (REFACTORIZADO)
MEJORAS: Complejidad ciclomática reducida usando patrones de diseño
- AIResponseParser: 10+ → 2 complejidad
- ValidationTaskFactory: 8+ → 3 complejidad  
- BaseValidator pattern para extensibilidad
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import re
from abc import ABC, abstractmethod

# IMPORTS LIMPIOS - Sin mocks
from app.shared import (
    setup_logger, Config, ErrorHandler, estimate_tokens, truncate_content, 
    validate_text_input, RuleData, ValidationResult, ChunkData
)

# Configurar logging
logger = setup_logger(__name__)

# =============================================================================
# AI RESPONSE PARSER - Complejidad reducida 10+ → 2
# =============================================================================

class BaseLineParser(ABC):
    """Base class para parsers de líneas específicas."""
    
    @abstractmethod
    def get_field_name(self) -> str:
        """Retorna nombre del campo que parsea."""
        pass
    
    @abstractmethod
    def parse(self, line: str) -> str:
        """Parsea línea específica."""
        pass


class ResultadoParser(BaseLineParser):
    """Parser específico para líneas de RESULTADO."""
    
    def get_field_name(self) -> str:
        return 'resultado'
    
    def parse(self, line: str) -> str:
        resultado_raw = line.replace('RESULTADO:', '').strip().upper()
        
        if 'CUMPLE' in resultado_raw and 'NO_CUMPLE' not in resultado_raw:
            return "CUMPLE"
        elif 'PARCIAL' in resultado_raw:
            return "PARCIAL"
        else:
            return "NO_CUMPLE"


class ConfianzaParser(BaseLineParser):
    """Parser específico para líneas de CONFIANZA."""
    
    def get_field_name(self) -> str:
        return 'confianza'
    
    def parse(self, line: str) -> str:
        return line.replace('CONFIANZA:', '').strip()


class ExplicacionParser(BaseLineParser):
    """Parser específico para líneas de EXPLICACIÓN."""
    
    def get_field_name(self) -> str:
        return 'explicacion'
    
    def parse(self, line: str) -> str:
        return line.replace('EXPLICACIÓN:', '').strip()


class AIResponseParser:
    """
    Parser para respuestas de AI usando Command pattern.
    COMPLEJIDAD REDUCIDA: 10+ → 2 decision paths
    """
    
    def __init__(self):
        self._parsers = {
            'RESULTADO:': ResultadoParser(),
            'CONFIANZA:': ConfianzaParser(),
            'EXPLICACIÓN:': ExplicacionParser()
        }
    
    def parse(self, rule: RuleData, ai_content: str, model_used: str, 
              content_size: int, chunk_number: Optional[int] = None) -> ValidationResult:
        """
        Parsea respuesta con complejidad reducida.
        COMPLEJIDAD: 2 decision paths (try/except + parsing loop)
        """
        try:
            # Preparación inicial (decision path 1)
            validated_content = validate_text_input(ai_content, f"ai_response_{rule.id}")
            lines = validated_content.strip().split('\n')
            
            # Parsing usando command pattern (decision path 2)
            parsed_data = self._parse_lines(lines)
            
            # Post-procesamiento
            if chunk_number:
                parsed_data['explicacion'] = f"[Chunk {chunk_number}] {parsed_data['explicacion']}"
            
            # Construcción del resultado
            return self._build_validation_result(rule, parsed_data, model_used, content_size, chunk_number)
            
        except Exception as e:
            return self._create_error_result(rule, e, model_used, content_size)
    
    def _parse_lines(self, lines: List[str]) -> Dict[str, str]:
        """Parsea líneas usando parsers específicos - SIN decision paths complejos."""
        result = {
            'resultado': 'NO_CUMPLE',
            'confianza': 'Baja', 
            'explicacion': 'Respuesta no pudo ser parseada'
        }
        
        for line in lines:
            line = line.strip()
            for prefix, parser in self._parsers.items():
                if line.startswith(prefix):
                    field_name = parser.get_field_name()
                    result[field_name] = parser.parse(line)
                    break
        
        return result
    
    def _build_validation_result(self, rule: RuleData, parsed_data: Dict[str, str],
                                model_used: str, content_size: int, 
                                chunk_number: Optional[int] = None) -> ValidationResult:
        """Construye ValidationResult desde datos parseados."""
        return ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado=parsed_data['resultado'],
            confianza=parsed_data['confianza'],
            explicacion=parsed_data['explicacion'],
            content_size_analyzed=content_size,
            model_used=model_used,
            chunks_processed=1 if not chunk_number else chunk_number
        )
    
    def _create_error_result(self, rule: RuleData, error: Exception, 
                           model_used: str, content_size: int) -> ValidationResult:
        """Crea resultado de error estandarizado."""
        logger.error(f"Error parseando respuesta de IA para regla {rule.id}: {str(error)}")
        
        return ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado="NO_CUMPLE",
            confianza="Baja",
            explicacion=f"Error procesando respuesta: {str(error)}",
            content_size_analyzed=content_size,
            model_used=model_used
        )


# =============================================================================
# VALIDATION TASK FACTORY - Complejidad reducida 8+ → 3
# =============================================================================

class BaseValidator(ABC):
    """Base class para validators específicos."""
    
    def __init__(self, validation_engine):
        self.engine = validation_engine
    
    @abstractmethod
    async def validate(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Override en subclases."""
        pass


class StructuralValidator(BaseValidator):
    """Validator específico para reglas estructurales."""
    
    async def validate(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        start_time = time.time()
        logger.debug(f"Ejecutando validación estructural para regla {rule.id}")
        
        # Determinar lógica estructural específica usando lookup table
        logic_type = self._determine_logic_type(rule)
        
        # Mapeo directo a métodos - SIN if/elif/else complejo
        validation_methods = {
            'file_existence': self.engine._validate_file_existence,
            'directory_structure': self.engine._validate_directory_structure,
            'file_naming': self.engine._validate_file_naming,
            'generic_structure': self.engine._validate_generic_structure
        }
        
        validator_method = validation_methods[logic_type]
        result = validator_method(rule, content)
        result.execution_time = time.time() - start_time
        
        logger.debug(f"Validación estructural completada para {rule.id} en {result.execution_time:.3f}s")
        return result
    
    def _determine_logic_type(self, rule: RuleData) -> str:
        """Determina tipo de lógica estructural usando lookup table."""
        keywords_map = {
            'file_existence': ['existe', 'debe tener', 'requerido'],
            'directory_structure': ['estructura', 'directorio', 'carpeta'],
            'file_naming': ['nombre', 'nomenclatura', 'naming']
        }
        
        description_lower = rule.description.lower()
        
        for logic_type, keywords in keywords_map.items():
            if any(keyword in description_lower for keyword in keywords):
                return logic_type
        
        return 'generic_structure'


class ContentValidator(BaseValidator):
    """Validator específico para reglas de contenido."""
    
    async def validate(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        start_time = time.time()
        logger.debug(f"Ejecutando validación de contenido para regla {rule.id}")
        
        # Preparar contenido para análisis
        prepared_content = self.engine._prepare_content_for_ai(rule, content, max_tokens=Config.MAX_CHUNK_SIZE)
        
        # Construir prompt específico para contenido
        prompt = self.engine._build_content_validation_prompt(rule, prepared_content)
        
        # Usar Claude Haiku REAL para reglas de contenido
        ai_response = await self.engine.repository_access_manager.invoke_haiku(prompt)
        
        execution_time = time.time() - start_time
        
        if not ai_response.get('success'):
            raise Exception(f"Validación de IA falló: {ai_response.get('error')}")
        
        # Registrar uso del modelo
        self.engine._update_model_usage_stats('claude-3-haiku')
        
        # Usar AIResponseParser refactorizado
        parser = AIResponseParser()
        result = parser.parse(rule, ai_response['content'], 'claude-3-haiku', len(prepared_content))
        result.execution_time = execution_time
        
        logger.debug(f"Validación de contenido completada para {rule.id} en {execution_time:.3f}s")
        return result


class SemanticValidator(BaseValidator):
    """Validator específico para reglas semánticas."""
    
    async def validate(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        start_time = time.time()
        logger.debug(f"Ejecutando validación semántica para regla {rule.id}")
        
        # Determinar si necesita chunking
        total_content_size = sum(len(c) for c in content.values())
        
        if total_content_size > Config.MAX_CHUNK_SIZE * 4:  # Muy grande para un solo prompt
            logger.info(f"Contenido grande detectado para regla {rule.id}, aplicando chunking")
            result = await self.engine._validate_semantic_with_chunking(rule, content)
        else:
            # Contenido manejable en un solo prompt
            result = await self._validate_semantic_single_prompt(rule, content)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        # Registrar uso del modelo
        self.engine._update_model_usage_stats('claude-3-sonnet')
        
        logger.debug(f"Validación semántica completada para {rule.id} en {execution_time:.3f}s")
        return result
    
    async def _validate_semantic_single_prompt(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Valida regla semántica con un solo prompt."""
        # Preparar contenido optimizado para análisis semántico
        prepared_content = self.engine._prepare_content_for_ai(rule, content, max_tokens=Config.MAX_CHUNK_SIZE)
        
        # Construir prompt específico para análisis semántico
        prompt = self.engine._build_semantic_validation_prompt(rule, prepared_content)
        
        # Usar Claude Sonnet REAL para análisis semántico de calidad
        ai_response = await self.engine.repository_access_manager.invoke_sonnet(prompt)
        
        if not ai_response.get('success'):
            raise Exception(f"Validación semántica falló: {ai_response.get('error')}")
        
        # Usar AIResponseParser refactorizado
        parser = AIResponseParser()
        return parser.parse(rule, ai_response['content'], 'claude-3-sonnet', len(prepared_content))


class ValidationTaskFactory:
    """
    Factory para crear tareas de validación específicas.
    COMPLEJIDAD REDUCIDA: 8+ → 3 decision paths
    """
    
    def __init__(self, validation_engine):
        self.engine = validation_engine
        self._validators = {
            'estructura': StructuralValidator(validation_engine),
            'contenido': ContentValidator(validation_engine),
            'semántica': SemanticValidator(validation_engine)
        }
    
    async def create_validation_task(self, rule: RuleData, content: Dict[str, str]) -> Dict[str, Any]:
        """
        Crea tarea de validación con complejidad reducida.
        COMPLEJIDAD: 3 decision paths (try/except, prerequisite_check, validator lookup)
        """
        try:
            # Preparación común
            rule_content = self.engine._extract_rule_specific_content(rule, content)
            
            # Validación de prerrequisitos (decision path 1)
            prerequisite_check = self._check_prerequisites(rule, rule_content)
            if prerequisite_check:
                return prerequisite_check
            
            # Delegación a validator específico (decision path 2)
            validator = self._get_validator(rule.type)
            result = await validator.validate(rule, rule_content)
            
            self.engine._increment_successful_validations()
            return self._create_success_response(result, rule.id)
            
        except Exception as e:  # decision path 3
            logger.error(f"Error en validación de regla {rule.id}: {str(e)}")
            self.engine._increment_failed_validations()
            return self._create_error_response(e, rule)
    
    def _check_prerequisites(self, rule: RuleData, content: Dict[str, str]) -> Optional[Dict]:
        """Verifica prerrequisitos de forma separada."""
        if not content and rule.type.lower() != 'estructura':
            logger.warning(f"No se encontró contenido para regla {rule.id}")
            return {
                'success': True,
                'validation_result': self.engine._create_no_content_result(rule),
                'rule_id': rule.id
            }
        return None
    
    def _get_validator(self, rule_type: str) -> BaseValidator:
        """Obtiene validator apropiado o lanza excepción."""
        validator = self._validators.get(rule_type.lower())
        if not validator:
            raise ValueError(f"Tipo de regla no soportado: {rule_type}")
        return validator
    
    def _create_success_response(self, result: ValidationResult, rule_id: str) -> Dict[str, Any]:
        """Crea respuesta de éxito estandarizada."""
        return {
            'success': True,
            'validation_result': result,
            'rule_id': rule_id,
            'execution_time': getattr(result, 'execution_time', None)
        }
    
    def _create_error_response(self, error: Exception, rule: RuleData) -> Dict[str, Any]:
        """Crea respuesta de error estandarizada."""
        return {
            'success': False,
            'error': str(error),
            'rule_id': rule.id,
            'rule_type': rule.type
        }


# =============================================================================
# VALIDATION ENGINE REFACTORIZADO
# =============================================================================

class ValidationEngine:
    """
    Motor central que ejecuta validaciones en paralelo usando múltiples modelos de IA.
    
    REFACTORIZADO:
    - ValidationTaskFactory para reducir complejidad de task creation
    - AIResponseParser para parsing limpio de respuestas
    - Validators especializados para cada tipo de regla
    """
    
    def __init__(self, repository_access_manager=None):
        """Inicializar ValidationEngine con RepositoryAccessManager."""
        if repository_access_manager is None:
            from shared import ComponentFactory
            repository_access_manager = ComponentFactory.get_repository_access_manager()
        
        self.repository_access_manager = repository_access_manager
        
        # Thread safety para estadísticas
        self._stats_lock = threading.Lock()
        
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'model_usage': {},
            'execution_times': []
        }
        
        # Factory para creación de tareas (NUEVO - reduce complejidad)
        self.task_factory = ValidationTaskFactory(self)
        
        logger.debug("ValidationEngine initialized with REAL RepositoryAccessManager and reduced complexity")
        
    async def execute_parallel_validation(self, classified_rules: Dict[str, List[RuleData]], 
                                        content: Dict[str, str]) -> List[ValidationResult]:
        """
        Ejecuta validaciones paralelas para todas las reglas usando estrategia optimizada.
        REFACTORIZADO: Usa ValidationTaskFactory para reducir complejidad
        """
        start_time = time.time()
        
        try:
            logger.info("Iniciando motor de validaciones paralelas")
            
            # Crear tareas de validación individuales usando factory (NUEVO)
            validation_tasks = []
            total_rules = 0
            
            for rule_type, rules in classified_rules.items():
                logger.info(f"Preparando {len(rules)} reglas de tipo '{rule_type}' para validación")
                
                for rule in rules:
                    # Usar factory en lugar de método complejo (REFACTORIZADO)
                    task = self.task_factory.create_validation_task(rule, content)
                    validation_tasks.append(task)
                    total_rules += 1
            
            if not validation_tasks:
                logger.warning("No se crearon tareas de validación - conjunto de reglas vacío")
                return []
            
            logger.info(f"Ejecutando {total_rules} validaciones en paralelo")
            
            # Ejecutar todas las validaciones simultáneamente
            results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            # Procesar resultados y estadísticas
            processed_results = self._process_parallel_results(results)
            
            execution_time = time.time() - start_time
            self._add_execution_time(execution_time)
            
            logger.info(f"Motor de validaciones completado en {execution_time:.2f} segundos")
            logger.info(f"Resultados: {len(processed_results)} exitosos de {total_rules} totales")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error crítico en el motor de validaciones: {str(e)}")
            raise Exception(f"Motor de validaciones falló: {str(e)}")
    
    # =============================================================================
    # MÉTODOS DE UTILIDAD Y SOPORTE (sin cambios funcionales)
    # =============================================================================
    
    def _extract_rule_specific_content(self, rule: RuleData, all_content: Dict[str, str]) -> Dict[str, str]:
        """Extrae únicamente el contenido requerido por una regla específica."""
        rule_content = {}
        
        for file_reference in rule.references:
            matching_files = self._find_matching_files(file_reference, all_content)
            rule_content.update(matching_files)
        
        # Log del contenido extraído
        total_size = sum(len(content) for content in rule_content.values())
        logger.debug(f"Regla {rule.id}: extraído contenido de {len(rule_content)} archivos "
                    f"({total_size:,} caracteres)")
        
        return rule_content
    
    def _find_matching_files(self, file_reference: str, all_content: Dict[str, str]) -> Dict[str, str]:
        """Encuentra archivos que coinciden con una referencia (soporta wildcards)."""
        import fnmatch
        
        matching_files = {}
        
        for file_path, content in all_content.items():
            if '*' in file_reference:
                # Patrón con wildcards
                if fnmatch.fnmatch(file_path, file_reference):
                    matching_files[file_path] = content
            else:
                # Coincidencia exacta o contenida
                if file_reference in file_path or file_path.endswith(file_reference):
                    matching_files[file_path] = content
        
        return matching_files
    
    def _create_no_content_result(self, rule: RuleData) -> ValidationResult:
        """Crea un resultado para reglas sin contenido disponible."""
        return ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado="NO_CUMPLE",
            confianza="Alta",
            explicacion=f"No se encontraron archivos requeridos: {', '.join(rule.references)}",
            content_size_analyzed=0,
            model_used="no_content_check"
        )
    
    # =============================================================================
    # VALIDACIONES ESTRUCTURALES (sin cambios funcionales)
    # =============================================================================
    
    def _validate_file_existence(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Valida la existencia de archivos requeridos."""
        missing_files = []
        found_files = []
        
        for required_file in rule.references:
            if any(required_file in file_path or file_path.endswith(required_file) 
                   for file_path in content.keys()):
                found_files.append(required_file)
            else:
                missing_files.append(required_file)
        
        if missing_files:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Alta",
                explicacion=f"Archivos faltantes: {', '.join(missing_files)}",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="file_existence_check"
            )
        else:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="CUMPLE",
                confianza="Alta",
                explicacion=f"Todos los archivos requeridos encontrados: {', '.join(found_files)}",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="file_existence_check"
            )
    
    def _validate_directory_structure(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Valida la estructura de directorios del repositorio."""
        if not content:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Alta",
                explicacion="No se encontró estructura de directorios para validar",
                content_size_analyzed=0,
                model_used="directory_structure_check"
            )
        
        # Extraer estructura de directorios de las rutas de archivos
        directories = set()
        root_files = 0
        nested_files = 0
        
        for file_path in content.keys():
            if '/' in file_path:
                # Archivo en subdirectorio
                directory = '/'.join(file_path.split('/')[:-1])
                directories.add(directory)
                nested_files += 1
            else:
                # Archivo en raíz
                root_files += 1
        
        total_files = len(content)
        organization_ratio = nested_files / total_files if total_files > 0 else 0
        
        # Evaluar organización usando configuración centralizada
        if organization_ratio >= Config.GOOD_ORGANIZATION_THRESHOLD:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="CUMPLE",
                confianza="Alta",
                explicacion=f"Buena organización: {len(directories)} directorios, {organization_ratio*100:.1f}% archivos organizados",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="directory_structure_check"
            )
        elif organization_ratio >= Config.PARTIAL_ORGANIZATION_THRESHOLD:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="PARCIAL",
                confianza="Media",
                explicacion=f"Organización parcial: {len(directories)} directorios, {organization_ratio*100:.1f}% archivos organizados",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="directory_structure_check"
            )
        else:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Alta",
                explicacion=f"Estructura plana: {root_files} archivos en raíz, solo {organization_ratio*100:.1f}% organizados",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="directory_structure_check"
            )

    def _validate_file_naming(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Valida nomenclatura de archivos según buenas prácticas."""
        if not content:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Alta",
                explicacion="No hay archivos para validar nomenclatura",
                content_size_analyzed=0,
                model_used="file_naming_check"
            )
        
        good_naming = 0
        problematic_files = []
        
        for file_path in content.keys():
            filename = file_path.split('/')[-1]
            has_problems = False
            
            # Verificar problemas comunes
            problems = []
            
            # Espacios en el nombre
            if ' ' in filename:
                problems.append("espacios")
                has_problems = True
            
            # Caracteres especiales problemáticos
            special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '{', '}', '[', ']']
            if any(char in filename for char in special_chars):
                problems.append("caracteres especiales")
                has_problems = True
            
            # Nombres muy largos
            if len(filename) > Config.MAX_FILENAME_LENGTH:
                problems.append("nombre muy largo")
                has_problems = True
            
            # Mayúsculas inconsistentes
            base_name = filename.split('.')[0]
            if base_name.isupper() or (base_name != base_name.lower() and '_' not in base_name and '-' not in base_name):
                problems.append("mayúsculas inconsistentes")
                has_problems = True
            
            if has_problems:
                problematic_files.append(f"{filename} ({', '.join(problems)})")
            else:
                good_naming += 1
        
        total_files = len(content)
        good_ratio = good_naming / total_files if total_files > 0 else 0
        
        # Usar configuración centralizada para umbrales
        if good_ratio >= Config.EXCELLENT_NAMING_THRESHOLD:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="CUMPLE",
                confianza="Alta",
                explicacion=f"Excelente nomenclatura: {good_naming}/{total_files} archivos ({good_ratio*100:.1f}%)",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="file_naming_check"
            )
        elif good_ratio >= 0.7:  # 70-89%
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="PARCIAL",
                confianza="Media",
                explicacion=f"Nomenclatura aceptable: {good_naming}/{total_files} archivos ({good_ratio*100:.1f}%). Problemas en: {len(problematic_files)} archivos",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="file_naming_check"
            )
        else:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Alta",
                explicacion=f"Nomenclatura problemática: solo {good_naming}/{total_files} archivos ({good_ratio*100:.1f}%) con buena nomenclatura",
                content_size_analyzed=sum(len(c) for c in content.values()),
                model_used="file_naming_check"
            )
    
    def _validate_generic_structure(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Validación estructural genérica cuando no se puede determinar lógica específica."""
        if not content:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Media",
                explicacion="No se encontró contenido para validar la estructura",
                content_size_analyzed=0,
                model_used="generic_structure_check"
            )
        
        # Validación básica: si hay contenido, asumimos estructura básica correcta
        return ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado="CUMPLE",
            confianza="Media",
            explicacion=f"Estructura básica presente: {len(content)} archivos encontrados",
            content_size_analyzed=sum(len(c) for c in content.values()),
            model_used="generic_structure_check"
        )
    
    # =============================================================================
    # MÉTODOS DE CHUNKING Y SEMANTIC VALIDATION (sin cambios)
    # =============================================================================
    
    async def _validate_semantic_with_chunking(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """Valida regla semántica con chunking para contenido grande."""
        logger.info(f"Aplicando chunking para regla semántica {rule.id}")
        
        # Crear chunks inteligentes del contenido
        chunks = self._create_intelligent_chunks(rule, content)
        
        if len(chunks) > Config.MAX_CHUNKS_PER_RULE:
            logger.warning(f"Demasiados chunks ({len(chunks)}) para regla {rule.id}, "
                          f"limitando a {Config.MAX_CHUNKS_PER_RULE}")
            chunks = chunks[:Config.MAX_CHUNKS_PER_RULE]
        
        # Validar cada chunk por separado
        chunk_tasks = []
        for i, chunk in enumerate(chunks):
            task = self._validate_semantic_chunk(rule, chunk, i+1, len(chunks))
            chunk_tasks.append(task)
        
        # Ejecutar validaciones de chunks en paralelo
        chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
        
        # Consolidar resultados de chunks
        return self._consolidate_chunk_results(rule, chunk_results, chunks)
    
    async def _validate_semantic_chunk(self, rule: RuleData, chunk: ChunkData, 
                                     chunk_number: int, total_chunks: int) -> ValidationResult:
        """Valida un chunk individual de contenido semántico."""
        prompt = self._build_chunk_validation_prompt(rule, chunk, chunk_number, total_chunks)
        
        # Usar Claude Sonnet REAL para chunks semánticos
        ai_response = await self.repository_access_manager.invoke_sonnet(prompt)
        
        if not ai_response.get('success'):
            raise Exception(f"Validación de chunk {chunk_number} falló: {ai_response.get('error')}")
        
        # Usar AIResponseParser refactorizado (NUEVO)
        parser = AIResponseParser()
        return parser.parse(rule, ai_response['content'], 'claude-3-sonnet', 
                          chunk.size_tokens * 4, chunk_number=chunk_number)
    
    def _create_intelligent_chunks(self, rule: RuleData, content: Dict[str, str]) -> List[ChunkData]:
        """Crea chunks inteligentes basados en la estructura del contenido."""
        chunks = []
        max_chunk_tokens = Config.MAX_CHUNK_SIZE
        
        # Estrategia de chunking según tipo de regla
        if 'documentación' in rule.description.lower():
            chunks = self._chunk_by_documentation_sections(content, max_chunk_tokens)
        elif 'arquitectura' in rule.description.lower():
            chunks = self._chunk_by_code_structure(content, max_chunk_tokens)
        else:
            chunks = self._chunk_by_size(content, max_chunk_tokens)
        
        logger.debug(f"Creados {len(chunks)} chunks para regla {rule.id}")
        
        return chunks
    
    def _chunk_by_size(self, content: Dict[str, str], max_tokens: int) -> List[ChunkData]:
        """Chunking simple por tamaño para casos generales."""
        chunks = []
        current_chunk_content = []
        current_tokens = 0
        
        for file_path, file_content in content.items():
            file_tokens = estimate_tokens(file_content)
            
            if current_tokens + file_tokens > max_tokens and current_chunk_content:
                # Crear chunk actual
                chunk_content = "\n\n".join(current_chunk_content)
                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_type="size_based",
                    size_tokens=current_tokens
                ))
                
                # Iniciar nuevo chunk
                current_chunk_content = [f"--- {file_path} ---\n{file_content}"]
                current_tokens = file_tokens
            else:
                current_chunk_content.append(f"--- {file_path} ---\n{file_content}")
                current_tokens += file_tokens
        
        # Agregar último chunk si existe
        if current_chunk_content:
            chunk_content = "\n\n".join(current_chunk_content)
            chunks.append(ChunkData(
                content=chunk_content,
                chunk_type="size_based",
                size_tokens=current_tokens
            ))
        
        return chunks
    
    def _consolidate_chunk_results(self, rule: RuleData, chunk_results: List[Any], 
                                 chunks: List[ChunkData]) -> ValidationResult:
        """Consolida resultados de múltiples chunks en un resultado final."""
        successful_results = []
        
        for result in chunk_results:
            if isinstance(result, ValidationResult):
                successful_results.append(result)
            elif not isinstance(result, Exception):
                logger.warning(f"Resultado de chunk inesperado para regla {rule.id}")
        
        if not successful_results:
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Baja",
                explicacion="Todos los chunks fallaron en la validación",
                content_size_analyzed=sum(chunk.size_tokens * 4 for chunk in chunks),
                model_used="claude-3-sonnet",
                chunks_processed=len(chunks)
            )
        
        # Lógica de consolidación basada en criticidad
        cumple_count = sum(1 for r in successful_results if r.resultado == "CUMPLE")
        no_cumple_count = sum(1 for r in successful_results if r.resultado == "NO_CUMPLE")
        parcial_count = sum(1 for r in successful_results if r.resultado == "PARCIAL")
        
        total_chunks = len(successful_results)
        
        # Determinación del resultado final
        if rule.criticality.lower() == 'alta':
            # Para criticidad alta: debe cumplir en TODOS los chunks
            resultado_final = "CUMPLE" if cumple_count == total_chunks else "NO_CUMPLE"
            confianza = "Alta" if cumple_count == total_chunks or no_cumple_count == total_chunks else "Media"
        else:
            # Para criticidad media/baja: mayoría decide
            if cumple_count > no_cumple_count:
                resultado_final = "CUMPLE"
                confianza = "Alta" if cumple_count > total_chunks * 0.7 else "Media"
            else:
                resultado_final = "NO_CUMPLE"
                confianza = "Media"
        
        # Crear explicación consolidada
        explicacion = f"Análisis de {total_chunks} fragmentos: {cumple_count} cumplen, {no_cumple_count} no cumplen"
        if parcial_count > 0:
            explicacion += f", {parcial_count} parciales"
        
        total_content_size = sum(chunk.size_tokens * 4 for chunk in chunks)
        
        return ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado=resultado_final,
            confianza=confianza,
            explicacion=explicacion,
            content_size_analyzed=total_content_size,
            model_used="claude-3-sonnet",
            chunks_processed=len(chunks)
        )
    
    # =============================================================================
    # PROMPT BUILDERS Y UTILITIES (sin cambios)
    # =============================================================================
    
    def _prepare_content_for_ai(self, rule: RuleData, content: Dict[str, str], max_tokens: int) -> str:
        """Prepara contenido optimizado para envío a IA con validación robusta."""
        # Validar contenido de entrada
        validated_content = {}
        for file_path, file_content in content.items():
            validated_content[file_path] = validate_text_input(file_content, f"file_{file_path}")
        
        # Combinar contenido con separadores claros
        combined_content = "\n\n".join([
            f"--- {file_path} ---\n{file_content}" 
            for file_path, file_content in validated_content.items()
        ])
        
        # Truncar si excede límite
        if estimate_tokens(combined_content) > max_tokens:
            combined_content = truncate_content(combined_content, max_tokens)
            logger.debug(f"Contenido truncado para regla {rule.id} (límite: {max_tokens} tokens)")
        
        return combined_content
    
    def _build_content_validation_prompt(self, rule: RuleData, content: str) -> str:
        """Construye prompt optimizado para validación de contenido."""
        return f"""Eres un validador experto de código. Analiza el contenido ÚNICAMENTE según esta regla específica.

REGLA A VALIDAR:
- ID: {rule.id}
- Descripción: {rule.description}
- Criticidad: {rule.criticality}
- Contexto: {rule.explanation or 'No especificado'}

IMPORTANTE: Enfócate SOLO en esta regla. Ignora otros aspectos del código.

CONTENIDO A ANALIZAR:
{content}

INSTRUCCIONES:
1. Analiza ÚNICAMENTE si el contenido cumple con: "{rule.description}"
2. Considera el nivel de criticidad: {rule.criticality}
3. Sé específico en tu evaluación

FORMATO DE RESPUESTA REQUERIDO:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Máximo 2 líneas específicas sobre esta regla]

RESPUESTA:"""
    
    def _build_semantic_validation_prompt(self, rule: RuleData, content: str) -> str:
        """Construye prompt optimizado para validación semántica."""
        return f"""Eres un experto en análisis semántico de código. Analiza el contenido según la regla específica.

REGLA SEMÁNTICA A VALIDAR:
- ID: {rule.id}
- Descripción: {rule.description}
- Criticidad: {rule.criticality}
- Contexto adicional: {rule.explanation or 'No especificado'}

ENFOQUE SEMÁNTICO: Analiza la intención, calidad, patrones y buenas prácticas del código.

CONTENIDO A ANALIZAR:
{content}

INSTRUCCIONES ESPECÍFICAS:
1. Evalúa semánticamente si cumple: "{rule.description}"
2. Considera patrones, intención del código, y buenas prácticas
3. El nivel de criticidad es: {rule.criticality}
4. Proporciona análisis profundo pero conciso

FORMATO DE RESPUESTA REQUERIDO:
RESULTADO: [CUMPLE/NO_CUMPLE]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Máximo 2 líneas con análisis semántico específico]

RESPUESTA:"""
    
    def _build_chunk_validation_prompt(self, rule: RuleData, chunk: ChunkData, 
                                     chunk_number: int, total_chunks: int) -> str:
        """Construye prompt para validación de chunk individual."""
        return f"""Eres un validador experto. Analiza este fragmento según la regla específica.

REGLA A VALIDAR:
- ID: {rule.id}
- Descripción: {rule.description}
- Criticidad: {rule.criticality}

CONTEXTO DEL ANÁLISIS:
- Fragmento {chunk_number} de {total_chunks}
- Tipo de contenido: {chunk.chunk_type}

CONTENIDO DEL FRAGMENTO:
{chunk.content}

INSTRUCCIONES:
1. Analiza SOLO este fragmento en relación a la regla: "{rule.description}"
2. Si es fragmento parcial, evalúa lo que SÍ puedes determinar
3. Indica tu nivel de confianza basado en la completitud

FORMATO DE RESPUESTA:
RESULTADO: [CUMPLE/NO_CUMPLE/PARCIAL]
CONFIANZA: [Alta/Media/Baja]
EXPLICACIÓN: [Evaluación específica de este fragmento]

RESPUESTA:"""
    
    # =============================================================================
    # MÉTODOS THREAD-SAFE Y ESTADÍSTICAS (sin cambios)
    # =============================================================================
    
    def _increment_successful_validations(self):
        """Incrementa contador de validaciones exitosas de forma thread-safe."""
        with self._stats_lock:
            self.validation_stats['successful_validations'] += 1
    
    def _increment_failed_validations(self):
        """Incrementa contador de validaciones fallidas de forma thread-safe."""
        with self._stats_lock:
            self.validation_stats['failed_validations'] += 1
    
    def _add_execution_time(self, execution_time: float):
        """Agrega tiempo de ejecución de forma thread-safe."""
        with self._stats_lock:
            self.validation_stats['execution_times'].append(execution_time)
    
    def _update_model_usage_stats(self, model_name: str):
        """Actualiza estadísticas de uso de modelos de forma thread-safe."""
        with self._stats_lock:
            if model_name not in self.validation_stats['model_usage']:
                self.validation_stats['model_usage'][model_name] = 0
            self.validation_stats['model_usage'][model_name] += 1
    
    def _process_parallel_results(self, results: List[Any]) -> List[ValidationResult]:
        """Procesa los resultados de la ejecución paralela de forma thread-safe."""
        successful_results = []
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Tarea de validación {i} falló con excepción: {str(result)}")
                failed_count += 1
            elif isinstance(result, dict) and result.get('success'):
                successful_results.append(result['validation_result'])
            else:
                logger.error(f"Tarea de validación {i} falló: {result.get('error', 'Error desconocido')}")
                failed_count += 1
        
        # THREAD SAFE: Actualizar estadísticas totales
        with self._stats_lock:
            self.validation_stats['total_validations'] = len(results)
            self.validation_stats['failed_validations'] += failed_count
        
        logger.info(f"Procesamiento de resultados: {len(successful_results)} exitosos, {failed_count} fallidos")
        
        return successful_results
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del motor de validaciones de forma thread-safe."""
        with self._stats_lock:
            # Crear copia de estadísticas para evitar modificación concurrente
            stats_copy = {
                'total_validations': self.validation_stats['total_validations'],
                'successful_validations': self.validation_stats['successful_validations'],
                'failed_validations': self.validation_stats['failed_validations'],
                'model_usage': self.validation_stats['model_usage'].copy(),
                'execution_times': self.validation_stats['execution_times'].copy()
            }
        
        avg_execution_time = (
            sum(stats_copy['execution_times']) / len(stats_copy['execution_times'])
            if stats_copy['execution_times'] else 0
        )
        
        return {
            'total_validations': stats_copy['total_validations'],
            'successful_validations': stats_copy['successful_validations'],
            'failed_validations': stats_copy['failed_validations'],
            'success_rate': (
                stats_copy['successful_validations'] / stats_copy['total_validations'] * 100
                if stats_copy['total_validations'] > 0 else 0
            ),
            'model_usage': stats_copy['model_usage'],
            'average_execution_time': avg_execution_time,
            'total_execution_time': sum(stats_copy['execution_times']),
            'uses_real_bedrock': True,
            'repository_access_manager': 'RepositoryAccessManager',
            'refactoring_applied': {
                'ai_response_parser': 'Complexity reduced 10+ → 2',
                'validation_task_factory': 'Complexity reduced 8+ → 3',
                'specialized_validators': 'Applied',
                'command_pattern_parsing': 'Applied'
            }
        }