"""
validation_engine.py - Motor central de validaciones paralelas
"""

import asyncio
import logging
import time
import threading  # NUEVO: Para thread safety
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import re

from app.utils import setup_logger, Config, ErrorHandler, estimate_tokens, truncate_content, validate_text_input
from app.models import RuleData, ValidationResult, ChunkData
from app.integrations import IntegrationManager

# Configurar logging
logger = setup_logger(__name__)

class ValidationEngine:
    """
    Motor central que ejecuta validaciones en paralelo usando múltiples modelos de IA.
    
    Implementa la estrategia de "un prompt por regla" para maximizar precisión,
    con selección automática de modelos y manejo inteligente de contenido grande.
    """
    
    def __init__(self, integration_manager: IntegrationManager):
        self.integration_manager = integration_manager
        
        # NUEVO: Thread safety para estadísticas - Corrige Bug #5
        self._stats_lock = threading.Lock()
        
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'model_usage': {},
            'execution_times': []
        }
        
    async def execute_parallel_validation(self, classified_rules: Dict[str, List[RuleData]], 
                                        content: Dict[str, str]) -> List[ValidationResult]:
        """
        Ejecuta validaciones paralelas para todas las reglas usando estrategia optimizada.
        
        Args:
            classified_rules: Reglas organizadas por tipo
            content: Contenido de archivos del repositorio
            
        Returns:
            list: Lista de resultados de validación completados
            
        Raises:
            Exception: Si falla críticamente la ejecución del motor
        """
        start_time = time.time()
        
        try:
            logger.info("Iniciando motor de validaciones paralelas")
            
            # Crear tareas de validación individuales para cada regla
            validation_tasks = []
            total_rules = 0
            
            for rule_type, rules in classified_rules.items():
                logger.info(f"Preparando {len(rules)} reglas de tipo '{rule_type}' para validación")
                
                for rule in rules:
                    task = self._create_single_rule_validation_task(rule, content)
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
            self._add_execution_time(execution_time)  # Thread safe
            
            logger.info(f"Motor de validaciones completado en {execution_time:.2f} segundos")
            logger.info(f"Resultados: {len(processed_results)} exitosos de {total_rules} totales")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error crítico en el motor de validaciones: {str(e)}")
            raise Exception(f"Motor de validaciones falló: {str(e)}")
    
    async def _create_single_rule_validation_task(self, rule: RuleData, content: Dict[str, str]) -> Dict[str, Any]:
        """
        Crea una tarea de validación individual para una regla específica.
        
        Args:
            rule: Regla específica a validar
            content: Contenido completo disponible
            
        Returns:
            dict: Resultado de validación o información de error
        """
        try:
            logger.debug(f"Creando tarea de validación para regla {rule.id} ({rule.type})")
            
            # Extraer contenido específico para esta regla
            rule_content = self._extract_rule_specific_content(rule, content)
            
            if not rule_content and rule.type.lower() != 'estructura':
                logger.warning(f"No se encontró contenido para regla {rule.id}")
                return self._create_no_content_result(rule)
            
            # Seleccionar estrategia de validación según tipo de regla
            if rule.type.lower() == 'estructura':
                result = await self._validate_structural_rule(rule, rule_content)
            elif rule.type.lower() == 'contenido':
                result = await self._validate_content_rule(rule, rule_content)
            elif rule.type.lower() == 'semántica':
                result = await self._validate_semantic_rule(rule, rule_content)
            else:
                raise Exception(f"Tipo de regla no soportado: {rule.type}")
            
            self._increment_successful_validations()  # Thread safe
            
            return {
                'success': True,
                'validation_result': result,
                'rule_id': rule.id,
                'execution_time': getattr(result, 'execution_time', None)
            }
            
        except Exception as e:
            logger.error(f"Error en validación de regla {rule.id}: {str(e)}")
            self._increment_failed_validations()  # Thread safe
            
            return {
                'success': False,
                'error': str(e),
                'rule_id': rule.id,
                'rule_type': rule.type
            }
    
    # NUEVOS MÉTODOS THREAD-SAFE - Corrigen Bug #5
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
        """
        Actualiza estadísticas de uso de modelos de forma thread-safe.
        
        Args:
            model_name: Nombre del modelo utilizado
        """
        with self._stats_lock:
            if model_name not in self.validation_stats['model_usage']:
                self.validation_stats['model_usage'][model_name] = 0
            self.validation_stats['model_usage'][model_name] += 1
    
    def _extract_rule_specific_content(self, rule: RuleData, all_content: Dict[str, str]) -> Dict[str, str]:
        """
        Extrae únicamente el contenido requerido por una regla específica.
        
        Args:
            rule: Regla que especifica archivos requeridos
            all_content: Todo el contenido disponible
            
        Returns:
            dict: Contenido filtrado para la regla
        """
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
        """
        Encuentra archivos que coinciden con una referencia (soporta wildcards).
        
        Args:
            file_reference: Referencia de archivo (puede incluir patrones)
            all_content: Contenido completo disponible
            
        Returns:
            dict: Archivos que coinciden con la referencia
        """
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
    
    def _create_no_content_result(self, rule: RuleData) -> Dict[str, Any]:
        """
        Crea un resultado para reglas sin contenido disponible.
        
        Args:
            rule: Regla sin contenido
            
        Returns:
            dict: Resultado indicando falta de contenido
        """
        result = ValidationResult(
            rule_id=rule.id,
            rule_type=rule.type,
            rule_criticality=rule.criticality,
            resultado="NO_CUMPLE",
            confianza="Alta",
            explicacion=f"No se encontraron archivos requeridos: {', '.join(rule.references)}",
            content_size_analyzed=0,
            model_used="no_content_check"
        )
        
        return {
            'success': True,
            'validation_result': result,
            'rule_id': rule.id
        }
    
    async def _validate_structural_rule(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida reglas estructurales usando lógica programada (sin IA).
        
        Args:
            rule: Regla estructural
            content: Contenido a validar
            
        Returns:
            ValidationResult: Resultado de validación estructural
        """
        start_time = time.time()
        
        logger.debug(f"Ejecutando validación estructural para regla {rule.id}")
        
        # Lógica estructural específica según la descripción de la regla
        validation_logic = self._determine_structural_logic(rule)
        
        if validation_logic == 'file_existence':
            result = self._validate_file_existence(rule, content)
        elif validation_logic == 'directory_structure':
            result = self._validate_directory_structure(rule, content)
        elif validation_logic == 'file_naming':
            result = self._validate_file_naming(rule, content)
        else:
            # Validación estructural genérica
            result = self._validate_generic_structure(rule, content)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        logger.debug(f"Validación estructural completada para {rule.id} en {execution_time:.3f}s")
        
        return result
    
    def _determine_structural_logic(self, rule: RuleData) -> str:
        """
        Determina qué lógica estructural aplicar según la descripción de la regla.
        
        Args:
            rule: Regla estructural
            
        Returns:
            str: Tipo de lógica estructural a aplicar
        """
        description_lower = rule.description.lower()
        
        if any(keyword in description_lower for keyword in ['existe', 'debe tener', 'requerido']):
            return 'file_existence'
        elif any(keyword in description_lower for keyword in ['estructura', 'directorio', 'carpeta']):
            return 'directory_structure'
        elif any(keyword in description_lower for keyword in ['nombre', 'nomenclatura', 'naming']):
            return 'file_naming'
        else:
            return 'generic_structure'
    
    def _validate_file_existence(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida la existencia de archivos requeridos.
        
        Args:
            rule: Regla de existencia de archivos
            content: Contenido disponible
            
        Returns:
            ValidationResult: Resultado de la validación
        """
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
        """
        Valida la estructura de directorios del repositorio.
        
        Args:
            rule: Regla de estructura de directorios
            content: Contenido disponible
            
        Returns:
            ValidationResult: Resultado de la validación
        """
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
        """
        Valida nomenclatura de archivos según buenas prácticas.
        
        Args:
            rule: Regla de nomenclatura
            content: Contenido disponible
            
        Returns:
            ValidationResult: Resultado de la validación
        """
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
            
            # Nombres muy largos - usar configuración centralizada
            if len(filename) > Config.MAX_FILENAME_LENGTH:
                problems.append("nombre muy largo")
                has_problems = True
            
            # Mayúsculas inconsistentes (excepto extensiones conocidas)
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
        """
        Validación estructural genérica cuando no se puede determinar lógica específica.
        
        Args:
            rule: Regla estructural genérica
            content: Contenido a validar
            
        Returns:
            ValidationResult: Resultado de validación genérica
        """
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
    
    async def _validate_content_rule(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida reglas de contenido usando Claude Haiku (rápido y económico).
        
        Args:
            rule: Regla de contenido
            content: Contenido a analizar
            
        Returns:
            ValidationResult: Resultado de validación de contenido
        """
        start_time = time.time()
        
        logger.debug(f"Ejecutando validación de contenido para regla {rule.id}")
        
        # Preparar contenido para análisis
        prepared_content = self._prepare_content_for_ai(rule, content, max_tokens=Config.MAX_CHUNK_SIZE)
        
        # Construir prompt específico para contenido
        prompt = self._build_content_validation_prompt(rule, prepared_content)
        
        # Usar Claude Haiku para reglas de contenido (optimización de costos)
        ai_response = await self.integration_manager.bedrock_client.invoke_haiku(prompt)
        
        execution_time = time.time() - start_time
        
        if not ai_response.get('success'):
            raise Exception(f"Validación de IA falló: {ai_response.get('error')}")
        
        # Registrar uso del modelo
        self._update_model_usage_stats('claude-3-haiku')
        
        result = self._parse_ai_response(
            rule, ai_response['content'], 'claude-3-haiku', 
            len(prepared_content), execution_time
        )
        
        logger.debug(f"Validación de contenido completada para {rule.id} en {execution_time:.3f}s")
        
        return result
    
    async def _validate_semantic_rule(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida reglas semánticas usando Claude Sonnet (alta calidad).
        
        Args:
            rule: Regla semántica
            content: Contenido a analizar
            
        Returns:
            ValidationResult: Resultado de validación semántica
        """
        start_time = time.time()
        
        logger.debug(f"Ejecutando validación semántica para regla {rule.id}")
        
        # Determinar si necesita chunking
        total_content_size = sum(len(c) for c in content.values())
        
        if total_content_size > Config.MAX_CHUNK_SIZE * 4:  # Muy grande para un solo prompt
            logger.info(f"Contenido grande detectado para regla {rule.id}, aplicando chunking")
            result = await self._validate_semantic_with_chunking(rule, content)
        else:
            # Contenido manejable en un solo prompt
            result = await self._validate_semantic_single_prompt(rule, content)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        # Registrar uso del modelo
        self._update_model_usage_stats('claude-3-sonnet')
        
        logger.debug(f"Validación semántica completada para {rule.id} en {execution_time:.3f}s")
        
        return result
    
    async def _validate_semantic_single_prompt(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida regla semántica con un solo prompt (contenido normal).
        
        Args:
            rule: Regla semántica
            content: Contenido a analizar
            
        Returns:
            ValidationResult: Resultado de validación
        """
        # Preparar contenido optimizado para análisis semántico
        prepared_content = self._prepare_content_for_ai(rule, content, max_tokens=Config.MAX_CHUNK_SIZE)
        
        # Construir prompt específico para análisis semántico
        prompt = self._build_semantic_validation_prompt(rule, prepared_content)
        
        # Usar Claude Sonnet para análisis semántico de calidad
        ai_response = await self.integration_manager.bedrock_client.invoke_sonnet(prompt)
        
        if not ai_response.get('success'):
            raise Exception(f"Validación semántica falló: {ai_response.get('error')}")
        
        return self._parse_ai_response(
            rule, ai_response['content'], 'claude-3-sonnet', len(prepared_content)
        )
    
    async def _validate_semantic_with_chunking(self, rule: RuleData, content: Dict[str, str]) -> ValidationResult:
        """
        Valida regla semántica con chunking para contenido grande.
        
        Args:
            rule: Regla semántica
            content: Contenido grande a analizar
            
        Returns:
            ValidationResult: Resultado consolidado de chunks
        """
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
        """
        Valida un chunk individual de contenido semántico.
        
        Args:
            rule: Regla semántica
            chunk: Chunk de contenido a validar
            chunk_number: Número del chunk actual
            total_chunks: Total de chunks
            
        Returns:
            ValidationResult: Resultado del chunk
        """
        prompt = self._build_chunk_validation_prompt(rule, chunk, chunk_number, total_chunks)
        
        ai_response = await self.integration_manager.bedrock_client.invoke_sonnet(prompt)
        
        if not ai_response.get('success'):
            raise Exception(f"Validación de chunk {chunk_number} falló: {ai_response.get('error')}")
        
        return self._parse_ai_response(
            rule, ai_response['content'], 'claude-3-sonnet', 
            chunk.size_tokens * 4, chunk_number=chunk_number
        )
    
    def _create_intelligent_chunks(self, rule: RuleData, content: Dict[str, str]) -> List[ChunkData]:
        """
        Crea chunks inteligentes basados en la estructura del contenido.
        
        Args:
            rule: Regla que determina la estrategia de chunking
            content: Contenido a dividir en chunks
            
        Returns:
            list: Lista de chunks inteligentes
        """
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
        """
        Chunking simple por tamaño para casos generales.
        
        Args:
            content: Contenido a dividir
            max_tokens: Máximo de tokens por chunk
            
        Returns:
            list: Chunks divididos por tamaño
        """
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
    
    def _prepare_content_for_ai(self, rule: RuleData, content: Dict[str, str], max_tokens: int) -> str:
        """
        Prepara contenido optimizado para envío a IA con validación robusta.
        
        Args:
            rule: Regla que determina la preparación
            content: Contenido original
            max_tokens: Límite de tokens
            
        Returns:
            str: Contenido preparado y optimizado
        """
        # Validar contenido de entrada usando utilidad corregida
        validated_content = {}
        for file_path, file_content in content.items():
            validated_content[file_path] = validate_text_input(file_content, f"file_{file_path}")
        
        # Combinar contenido con separadores claros
        combined_content = "\n\n".join([
            f"--- {file_path} ---\n{file_content}" 
            for file_path, file_content in validated_content.items()
        ])
        
        # Truncar si excede límite usando función corregida
        if estimate_tokens(combined_content) > max_tokens:
            combined_content = truncate_content(combined_content, max_tokens)
            logger.debug(f"Contenido truncado para regla {rule.id} (límite: {max_tokens} tokens)")
        
        return combined_content
    
    def _build_content_validation_prompt(self, rule: RuleData, content: str) -> str:
        """
        Construye prompt optimizado para validación de contenido.
        
        Args:
            rule: Regla de contenido
            content: Contenido preparado
            
        Returns:
            str: Prompt estructurado
        """
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
        """
        Construye prompt optimizado para validación semántica.
        
        Args:
            rule: Regla semántica
            content: Contenido preparado
            
        Returns:
            str: Prompt para análisis semántico
        """
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
        """
        Construye prompt para validación de chunk individual.
        
        Args:
            rule: Regla semántica
            chunk: Chunk a validar
            chunk_number: Número del chunk
            total_chunks: Total de chunks
            
        Returns:
            str: Prompt para chunk
        """
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
    
    def _parse_ai_response(self, rule: RuleData, ai_content: str, model_used: str, 
                          content_size: int, chunk_number: Optional[int] = None) -> ValidationResult:
        """
        Parsea respuesta de IA a ValidationResult estructurado.
        
        Args:
            rule: Regla validada
            ai_content: Respuesta del modelo
            model_used: Modelo utilizado
            content_size: Tamaño del contenido analizado
            chunk_number: Número de chunk (si aplica)
            
        Returns:
            ValidationResult: Resultado parseado
        """
        try:
            # Validar input usando función corregida
            validated_ai_content = validate_text_input(ai_content, f"ai_response_{rule.id}")
            
            # Parsear respuesta línea por línea
            lines = validated_ai_content.strip().split('\n')
            resultado = "NO_CUMPLE"  # Default conservador
            confianza = "Baja"
            explicacion = "Respuesta no pudo ser parseada"
            
            for line in lines:
                line = line.strip()
                if line.startswith('RESULTADO:'):
                    resultado_raw = line.replace('RESULTADO:', '').strip().upper()
                    if 'CUMPLE' in resultado_raw and 'NO_CUMPLE' not in resultado_raw:
                        resultado = "CUMPLE"
                    elif 'PARCIAL' in resultado_raw:
                        resultado = "PARCIAL"
                    else:
                        resultado = "NO_CUMPLE"
                elif line.startswith('CONFIANZA:'):
                    confianza = line.replace('CONFIANZA:', '').strip()
                elif line.startswith('EXPLICACIÓN:'):
                    explicacion = line.replace('EXPLICACIÓN:', '').strip()
            
            # Agregar información de chunk si aplica
            if chunk_number:
                explicacion = f"[Chunk {chunk_number}] {explicacion}"
            
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado=resultado,
                confianza=confianza,
                explicacion=explicacion,
                content_size_analyzed=content_size,
                model_used=model_used,
                chunks_processed=1 if not chunk_number else chunk_number
            )
            
        except Exception as e:
            logger.error(f"Error parseando respuesta de IA para regla {rule.id}: {str(e)}")
            
            return ValidationResult(
                rule_id=rule.id,
                rule_type=rule.type,
                rule_criticality=rule.criticality,
                resultado="NO_CUMPLE",
                confianza="Baja",
                explicacion=f"Error procesando respuesta: {str(e)}",
                content_size_analyzed=content_size,
                model_used=model_used
            )
    
    def _consolidate_chunk_results(self, rule: RuleData, chunk_results: List[Any], 
                                 chunks: List[ChunkData]) -> ValidationResult:
        """
        Consolida resultados de múltiples chunks en un resultado final.
        
        Args:
            rule: Regla que se validó
            chunk_results: Resultados de validación de chunks
            chunks: Chunks originales
            
        Returns:
            ValidationResult: Resultado consolidado
        """
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
    
    def _process_parallel_results(self, results: List[Any]) -> List[ValidationResult]:
        """
        Procesa los resultados de la ejecución paralela de forma thread-safe.
        
        Args:
            results: Resultados raw de asyncio.gather
            
        Returns:
            list: Lista de ValidationResult exitosos
        """
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
        """
        Obtiene estadísticas completas del motor de validaciones de forma thread-safe.
        
        Returns:
            dict: Estadísticas detalladas del motor
        """
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
            'total_execution_time': sum(stats_copy['execution_times'])
        }