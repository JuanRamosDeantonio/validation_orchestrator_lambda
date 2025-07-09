"""
rules_processor.py - Procesador de reglas de validación
"""

import logging
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

from app.utils import setup_logger, Config, ErrorHandler, S3JsonReader, S3PathHelper  # CORREGIDO: Import consistente
from app.models import RuleData  # CORREGIDO: Import consistente
from app.integrations import IntegrationManager  # CORREGIDO: Bug #1 - Import consistente

# Configurar logging
logger = setup_logger(__name__)

class RulesProcessor:
    """
    Procesador centralizado para la gestión de reglas de validación.
    
    Se encarga de cargar, clasificar, agrupar y preparar las reglas
    para su posterior validación en el motor de validaciones.
    """
    
    def __init__(self, integration_manager: IntegrationManager):
        self.integration_manager = integration_manager
        self._cached_rules = None
        self._rules_metadata = {}
        
    async def load_and_process_rules(self) -> Dict[str, Any]:
        """
        Carga y procesa todas las reglas desde el archivo rulesmetadata.json en S3.
        
        Este es el método principal que orquesta todo el procesamiento
        de reglas desde la carga hasta la clasificación final.
        
        Returns:
            dict: Reglas procesadas con clasificación y agrupación
            
        Raises:
            Exception: Si falla la carga o procesamiento de reglas
        """
        try:
            logger.info("Iniciando carga y procesamiento de reglas de validación")
            
            # Cargar reglas desde S3 (no lambda)
            raw_rules = await self._load_rules_from_s3()
            
            # Parsear reglas a objetos RuleData
            parsed_rules = self._parse_rules_metadata(raw_rules)
            
            # Clasificar reglas por tipo
            classified_rules = self._classify_rules_by_type(parsed_rules)
            
            # Agrupar reglas por archivos requeridos
            grouped_rules = self._group_rules_by_files(classified_rules)
            
            # Extraer archivos únicos requeridos
            required_files = self._extract_unique_required_files(parsed_rules)
            
            # Análisis de criticidad
            criticality_analysis = self._analyze_criticality_distribution(parsed_rules)
            
            logger.info(f"Procesamiento de reglas completado exitosamente")
            logger.info(f"Total de reglas procesadas: {len(parsed_rules)}")
            
            return {
                'raw_rules': raw_rules,
                'parsed_rules': parsed_rules,
                'classified_rules': classified_rules,
                'grouped_rules': grouped_rules,
                'required_files': required_files,
                'criticality_analysis': criticality_analysis,
                'processing_metadata': self._rules_metadata
            }
            
        except Exception as e:
            logger.error(f"Error en el procesamiento de reglas: {str(e)}")
            raise Exception(f"Falló el procesamiento de reglas: {str(e)}")
    
    async def _load_rules_from_s3(self) -> List[Dict[str, Any]]:
        """
        Carga las reglas desde el archivo rulesmetadata.json en S3.
        
        Returns:
            list: Lista de reglas en formato diccionario raw
            
        Raises:
            Exception: Si falla la carga desde S3
        """
        try:
            # CORREGIDO: Usar path centralizado
            logger.info(f"Cargando reglas desde S3: {S3PathHelper.build_full_rules_path()}")
            
            # Usar utilidad para leer JSON desde S3 con validación automática
            rules_data = S3JsonReader.read_rules_metadata(self.integration_manager.s3_client)
            
            # Extraer reglas del JSON
            raw_rules = rules_data.get('rules', [])
            
            if not raw_rules:
                logger.warning("El archivo rulesmetadata.json no contiene reglas")
                return []
            
            logger.info(f"Se cargaron {len(raw_rules)} reglas desde S3")
            
            # Guardar metadata de la carga - CORREGIDO: Usar path centralizado
            self._rules_metadata['load_timestamp'] = rules_data.get('timestamp')
            self._rules_metadata['source'] = 'S3_rulesmetadata.json'
            self._rules_metadata['rules_count'] = len(raw_rules)
            self._rules_metadata['file_path'] = S3PathHelper.build_full_rules_path()
            self._rules_metadata['data_version'] = rules_data.get('version', 'unknown')
            
            return raw_rules
            
        except Exception as e:
            logger.error(f"Error cargando reglas desde S3: {str(e)}")
            raise Exception(f"Falló la carga de reglas desde S3: {str(e)}")
    
    def _parse_rules_metadata(self, raw_rules: List[Dict[str, Any]]) -> List[RuleData]:
        """
        Convierte reglas raw en objetos RuleData validados.
        
        Args:
            raw_rules: Lista de reglas en formato diccionario
            
        Returns:
            list: Lista de objetos RuleData validados
            
        Raises:
            Exception: Si hay errores de validación en las reglas
        """
        try:
            logger.info("Parseando metadata de reglas a objetos RuleData")
            
            parsed_rules = []
            parsing_errors = []
            
            for i, raw_rule in enumerate(raw_rules):
                try:
                    # Validar y crear objeto RuleData usando Pydantic
                    rule_data = RuleData(**raw_rule)
                    parsed_rules.append(rule_data)
                    
                    logger.debug(f"Regla parseada exitosamente: {rule_data.id}")
                    
                except Exception as e:
                    error_msg = f"Error parseando regla en índice {i}: {str(e)}"
                    parsing_errors.append(error_msg)
                    logger.warning(error_msg)
            
            # Verificar si hubo errores críticos
            if len(parsing_errors) > len(raw_rules) * 0.5:  # Más del 50% falló
                raise Exception(f"Demasiados errores de parsing: {len(parsing_errors)} de {len(raw_rules)}")
            
            if parsing_errors:
                logger.warning(f"Se encontraron {len(parsing_errors)} errores de parsing no críticos")
                self._rules_metadata['parsing_errors'] = parsing_errors
            
            logger.info(f"Parsing completado: {len(parsed_rules)} reglas válidas de {len(raw_rules)} totales")
            
            return parsed_rules
            
        except Exception as e:
            logger.error(f"Error en el parsing de metadata de reglas: {str(e)}")
            raise Exception(f"Falló el parsing de reglas: {str(e)}")
    
    def _classify_rules_by_type(self, rules: List[RuleData]) -> Dict[str, List[RuleData]]:
        """
        Clasifica las reglas por tipo para procesamiento optimizado.
        
        Args:
            rules: Lista de reglas a clasificar
            
        Returns:
            dict: Reglas clasificadas por tipo {'estructura': [], 'contenido': [], 'semántica': []}
        """
        logger.info("Clasificando reglas por tipo de validación")
        
        classified = {
            'estructura': [],
            'contenido': [],
            'semántica': []
        }
        
        unknown_types = set()
        
        for rule in rules:
            rule_type = rule.type.lower().strip()
            
            # Normalizar variaciones del tipo
            if rule_type in ['estructura', 'structural', 'structure']:
                classified['estructura'].append(rule)
            elif rule_type in ['contenido', 'content', 'contenidos']:
                classified['contenido'].append(rule)
            elif rule_type in ['semántica', 'semantica', 'semantic', 'semántico']:
                classified['semántica'].append(rule)
            else:
                # Tipo desconocido - asignar a contenido por defecto
                logger.warning(f"Tipo de regla desconocido '{rule_type}' para regla {rule.id}, "
                              f"asignando a 'contenido' por defecto")
                classified['contenido'].append(rule)
                unknown_types.add(rule_type)
        
        # Registrar estadísticas de clasificación
        total_structural = len(classified['estructura'])
        total_content = len(classified['contenido'])
        total_semantic = len(classified['semántica'])
        
        logger.info(f"Clasificación completada:")
        logger.info(f"  - Reglas estructurales: {total_structural}")
        logger.info(f"  - Reglas de contenido: {total_content}")
        logger.info(f"  - Reglas semánticas: {total_semantic}")
        
        if unknown_types:
            logger.warning(f"Tipos de regla no reconocidos encontrados: {list(unknown_types)}")
            self._rules_metadata['unknown_types'] = list(unknown_types)
        
        # Guardar estadísticas en metadata
        self._rules_metadata['classification_stats'] = {
            'structural': total_structural,
            'content': total_content,
            'semantic': total_semantic,
            'unknown_types_count': len(unknown_types)
        }
        
        return classified
    
    def _group_rules_by_files(self, classified_rules: Dict[str, List[RuleData]]) -> Dict[str, Any]:
        """
        Agrupa reglas por archivos requeridos para optimizar la carga de contenido.
        
        Args:
            classified_rules: Reglas ya clasificadas por tipo
            
        Returns:
            dict: Agrupación de reglas por archivos y análisis de dependencias
        """
        logger.info("Agrupando reglas por archivos requeridos")
        
        # Agrupar por archivos principales (primer archivo en references)
        grouped_by_primary_file = defaultdict(list)
        
        # Agrupar por patrones de archivos
        grouped_by_pattern = defaultdict(list)
        
        # Reglas que no requieren archivos específicos
        rules_without_files = []
        
        # Análisis de dependencias entre archivos
        file_dependencies = defaultdict(set)
        
        for rule_type, rules in classified_rules.items():
            for rule in rules:
                if not rule.references:
                    rules_without_files.append(rule)
                    logger.debug(f"Regla {rule.id} no requiere archivos específicos")
                    continue
                
                # Archivo principal (primer archivo en la lista)
                primary_file = rule.references[0]
                grouped_by_primary_file[primary_file].append(rule)
                
                # Detectar patrones de archivos
                file_pattern = self._detect_file_pattern(primary_file)
                grouped_by_pattern[file_pattern].append(rule)
                
                # Analizar dependencias entre archivos
                if len(rule.references) > 1:
                    context_files = set(rule.references[1:])
                    file_dependencies[primary_file].update(context_files)
                
                logger.debug(f"Regla {rule.id} requiere archivo principal: {primary_file}")
        
        # Crear estadísticas de agrupación
        grouping_stats = {
            'total_primary_files': len(grouped_by_primary_file),
            'total_patterns': len(grouped_by_pattern),
            'rules_without_files': len(rules_without_files),
            'files_with_dependencies': len([f for f, deps in file_dependencies.items() if deps])
        }
        
        logger.info(f"Agrupación completada:")
        logger.info(f"  - Archivos principales únicos: {grouping_stats['total_primary_files']}")
        logger.info(f"  - Patrones de archivos detectados: {grouping_stats['total_patterns']}")
        logger.info(f"  - Reglas sin archivos específicos: {grouping_stats['rules_without_files']}")
        
        return {
            'by_primary_file': dict(grouped_by_primary_file),
            'by_pattern': dict(grouped_by_pattern),
            'without_files': rules_without_files,
            'file_dependencies': dict(file_dependencies),
            'grouping_stats': grouping_stats
        }
    
    def _detect_file_pattern(self, file_reference: str) -> str:
        """
        Detecta el patrón de un archivo para agrupación optimizada.
        
        Args:
            file_reference: Referencia de archivo (puede incluir wildcards)
            
        Returns:
            str: Patrón detectado del archivo
        """
        # Detectar extensiones comunes
        if file_reference.endswith('.py'):
            return 'python_files'
        elif file_reference.endswith('.js'):
            return 'javascript_files'
        elif file_reference.endswith('.md'):
            return 'markdown_files'
        elif file_reference.endswith('.json'):
            return 'json_files'
        elif file_reference.endswith('.yml') or file_reference.endswith('.yaml'):
            return 'yaml_files'
        elif '*' in file_reference:
            return 'wildcard_pattern'
        elif '/' in file_reference:
            return 'path_specific'
        else:
            return 'exact_match'
    
    def _extract_unique_required_files(self, rules: List[RuleData]) -> List[str]:
        """
        Extrae lista única de todos los archivos requeridos por las reglas.
        
        Args:
            rules: Lista de todas las reglas
            
        Returns:
            list: Lista de archivos únicos requeridos
        """
        logger.info("Extrayendo archivos únicos requeridos por todas las reglas")
        
        required_files = set()
        files_by_rule_type = defaultdict(set)
        
        for rule in rules:
            rule_type = rule.type.lower()
            for file_ref in rule.references:
                required_files.add(file_ref)
                files_by_rule_type[rule_type].add(file_ref)
        
        unique_files = list(required_files)
        
        logger.info(f"Se identificaron {len(unique_files)} archivos únicos requeridos")
        
        # Análisis por tipo de regla
        for rule_type, files in files_by_rule_type.items():
            logger.info(f"  - Reglas {rule_type}: {len(files)} archivos únicos")
        
        # Guardar análisis en metadata
        self._rules_metadata['required_files_analysis'] = {
            'total_unique_files': len(unique_files),
            'by_rule_type': {rule_type: len(files) for rule_type, files in files_by_rule_type.items()},
            'file_list': unique_files
        }
        
        return unique_files
    
    def _analyze_criticality_distribution(self, rules: List[RuleData]) -> Dict[str, Any]:
        """
        Analiza la distribución de criticidad de las reglas para optimización.
        
        Args:
            rules: Lista de reglas a analizar
            
        Returns:
            dict: Análisis de distribución de criticidad
        """
        logger.info("Analizando distribución de criticidad de reglas")
        
        criticality_count = defaultdict(int)
        criticality_by_type = defaultdict(lambda: defaultdict(int))
        
        for rule in rules:
            criticality = rule.criticality.lower()
            rule_type = rule.type.lower()
            
            criticality_count[criticality] += 1
            criticality_by_type[rule_type][criticality] += 1
        
        total_rules = len(rules)
        
        # Calcular porcentajes
        criticality_percentages = {
            crit: (count / total_rules) * 100 
            for crit, count in criticality_count.items()
        }
        
        # Identificar reglas críticas para priorización
        critical_rules = [rule for rule in rules if rule.criticality.lower() == 'alta']
        
        analysis = {
            'total_rules': total_rules,
            'by_criticality': dict(criticality_count),
            'percentages': criticality_percentages,
            'by_type_and_criticality': dict(criticality_by_type),
            'critical_rules_count': len(critical_rules),
            'critical_rules': [rule.id for rule in critical_rules]
        }
        
        logger.info(f"Análisis de criticidad completado:")
        logger.info(f"  - Reglas críticas (alta): {criticality_count.get('alta', 0)} "
                   f"({criticality_percentages.get('alta', 0):.1f}%)")
        logger.info(f"  - Reglas medias: {criticality_count.get('media', 0)} "
                   f"({criticality_percentages.get('media', 0):.1f}%)")
        logger.info(f"  - Reglas bajas: {criticality_count.get('baja', 0)} "
                   f"({criticality_percentages.get('baja', 0):.1f}%)")
        
        return analysis
    
    def get_rules_for_file(self, file_path: str, classified_rules: Dict[str, List[RuleData]]) -> List[RuleData]:
        """
        Obtiene todas las reglas que requieren un archivo específico.
        
        Args:
            file_path: Ruta del archivo a consultar
            classified_rules: Reglas clasificadas por tipo
            
        Returns:
            list: Lista de reglas que requieren el archivo
        """
        logger.debug(f"Buscando reglas que requieren el archivo: {file_path}")
        
        matching_rules = []
        
        for rule_type, rules in classified_rules.items():
            for rule in rules:
                if self._file_matches_rule_references(file_path, rule.references):
                    matching_rules.append(rule)
                    logger.debug(f"Regla {rule.id} coincide con archivo {file_path}")
        
        logger.debug(f"Se encontraron {len(matching_rules)} reglas para el archivo {file_path}")
        
        return matching_rules
    
    def _file_matches_rule_references(self, file_path: str, references: List[str]) -> bool:
        """
        Verifica si un archivo coincide con las referencias de una regla.
        
        Args:
            file_path: Ruta del archivo
            references: Lista de referencias de la regla
            
        Returns:
            bool: True si el archivo coincide con alguna referencia
        """
        import fnmatch
        
        for reference in references:
            # Manejo de patrones con wildcards
            if '*' in reference:
                if fnmatch.fnmatch(file_path, reference):
                    return True
            else:
                # Coincidencia exacta o contenida
                if reference in file_path or file_path.endswith(reference):
                    return True
        
        return False
    
    def get_optimization_recommendations(self, processed_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera recomendaciones para optimizar el procesamiento de validaciones.
        
        Args:
            processed_rules: Resultado del procesamiento de reglas
            
        Returns:
            dict: Recomendaciones de optimización
        """
        logger.info("Generando recomendaciones de optimización")
        
        classified_rules = processed_rules['classified_rules']
        criticality_analysis = processed_rules['criticality_analysis']
        required_files = processed_rules['required_files']
        
        recommendations = {
            'execution_strategy': {},
            'cost_optimization': {},
            'performance_optimization': {},
            'risk_assessment': {}
        }
        
        # Estrategia de ejecución basada en criticidad
        critical_rules_count = criticality_analysis['critical_rules_count']
        total_rules = criticality_analysis['total_rules']
        
        if critical_rules_count > total_rules * 0.3:  # Más del 30% son críticas
            recommendations['execution_strategy'] = {
                'approach': 'critical_first',
                'reason': 'Alto porcentaje de reglas críticas requiere validación prioritaria',
                'recommended_order': ['alta', 'media', 'baja']
            }
        else:
            recommendations['execution_strategy'] = {
                'approach': 'parallel_by_type',
                'reason': 'Distribución balanceada permite procesamiento paralelo por tipo',
                'recommended_order': ['paralelo']
            }
        
        # Optimización de costos
        semantic_rules_count = len(classified_rules.get('semántica', []))
        total_rules_count = sum(len(rules) for rules in classified_rules.values())
        
        if semantic_rules_count > total_rules_count * 0.5:  # Más del 50% son semánticas
            recommendations['cost_optimization'] = {
                'concern': 'high_ai_usage',
                'recommendation': 'Considerar chunking agresivo y uso de modelos económicos',
                'estimated_cost_level': 'alto'
            }
        else:
            recommendations['cost_optimization'] = {
                'concern': 'moderate_ai_usage',
                'recommendation': 'Balancear calidad y costo con selección inteligente de modelos',
                'estimated_cost_level': 'moderado'
            }
        
        # Optimización de rendimiento
        total_files = len(required_files)
        if total_files > 50:
            recommendations['performance_optimization'] = {
                'concern': 'large_file_count',
                'recommendation': 'Implementar cache de contenido y carga asíncrona optimizada',
                'suggested_chunk_size': Config.MAX_CHUNK_SIZE // 2
            }
        
        # Evaluación de riesgo
        if critical_rules_count == 0:
            recommendations['risk_assessment'] = {
                'level': 'bajo',
                'reason': 'No hay reglas críticas que puedan causar fallo inmediato'
            }
        elif critical_rules_count > 5:
            recommendations['risk_assessment'] = {
                'level': 'alto',
                'reason': 'Muchas reglas críticas aumentan probabilidad de fallo'
            }
        else:
            recommendations['risk_assessment'] = {
                'level': 'moderado',
                'reason': 'Cantidad manejable de reglas críticas'
            }
        
        logger.info("Recomendaciones de optimización generadas exitosamente")
        
        return recommendations
    
    def get_rules_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas del procesamiento de reglas.
        
        Returns:
            dict: Estadísticas detalladas del procesador
        """
        return {
            'processing_metadata': self._rules_metadata,
            'cache_status': {
                'has_cached_rules': self._cached_rules is not None,
                'cached_rules_count': len(self._cached_rules) if self._cached_rules else 0
            },
            'source_info': {
                'source': self._rules_metadata.get('source', 'unknown'),
                'file_path': self._rules_metadata.get('file_path', 'unknown'),
                'load_timestamp': self._rules_metadata.get('load_timestamp', 'unknown'),
                'data_version': self._rules_metadata.get('data_version', 'unknown')
            }
        }
    
    async def refresh_rules_cache(self) -> bool:
        """
        Refresca el cache de reglas cargando desde S3 nuevamente.
        
        Returns:
            bool: True si se refrescó exitosamente
        """
        try:
            logger.info("Refrescando cache de reglas")
            
            # Limpiar cache actual
            self._cached_rules = None
            self._rules_metadata = {}
            
            # Cargar reglas frescas
            processed_rules = await self.load_and_process_rules()
            
            # Guardar en cache
            self._cached_rules = processed_rules
            
            logger.info("Cache de reglas refrescado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error refrescando cache de reglas: {str(e)}")
            return False
    
    def validate_rules_structure(self, rules: List[RuleData]) -> Dict[str, Any]:
        """
        Valida la estructura y consistencia de las reglas cargadas.
        
        Args:
            rules: Lista de reglas a validar
            
        Returns:
            dict: Resultado de la validación
        """
        validation_results = {
            'total_rules': len(rules),
            'valid_rules': 0,
            'issues': [],
            'warnings': []
        }
        
        rule_ids = set()
        
        for rule in rules:
            # Validar ID único
            if rule.id in rule_ids:
                validation_results['issues'].append(f"ID duplicado encontrado: {rule.id}")
            else:
                rule_ids.add(rule.id)
                validation_results['valid_rules'] += 1
            
            # Validar que tenga referencias si no es tipo general
            if not rule.references and rule.type.lower() != 'general':
                validation_results['warnings'].append(
                    f"Regla {rule.id} de tipo '{rule.type}' no tiene referencias de archivos"
                )
            
            # Validar descripción no vacía
            if not rule.description.strip():
                validation_results['issues'].append(f"Regla {rule.id} tiene descripción vacía")
            
            # Validar criticidad válida
            if rule.criticality.lower() not in ['baja', 'media', 'alta']:
                validation_results['warnings'].append(
                    f"Regla {rule.id} tiene criticidad desconocida: {rule.criticality}"
                )
        
        validation_results['is_valid'] = len(validation_results['issues']) == 0
        validation_results['has_warnings'] = len(validation_results['warnings']) > 0
        
        logger.info(f"Validación de reglas completada: {validation_results['valid_rules']}/{validation_results['total_rules']} válidas")
        
        if validation_results['issues']:
            for issue in validation_results['issues']:
                logger.error(f"Problema en reglas: {issue}")
        
        if validation_results['warnings']:
            for warning in validation_results['warnings']:
                logger.warning(f"Advertencia en reglas: {warning}")
        
        return validation_results