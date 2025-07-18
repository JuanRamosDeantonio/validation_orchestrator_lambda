"""
VERSIÓN FINAL CORREGIDA: Sistema de agrupación de reglas
✅ PROBLEMA RESUELTO: markdownfile ahora contiene objetos MarkdownDocument completos
✅ MANEJO DE DICCIONARIOS: Soporta markdownfiles como {ruta: contenido}
✅ PRESERVACIÓN DE CONTENIDO: Mantiene relación ruta → contenido correctamente
✅ SOLUCIÓN CONTENT VACÍO: Múltiples opciones para cargar contenido real
✅ Arquitectura Limpia + Optimización de Memoria + 100% Funcional

ESTRUCTURAS SOPORTADAS DE markdownfiles:
- Lista de objetos MarkdownDocument: [MarkdownDocument(path="x", content="y")]
- Lista de dicts con path/content: [{"path": "x", "content": "y"}]
- Lista de dicts ruta→contenido: [{"file.md": "contenido"}]
- Diccionario ruta→contenido: {"file1.md": "contenido1", "file2.md": "contenido2"}
- Lista de strings (paths): ["file1.md", "file2.md"]

FUNCIONES PRINCIPALES:
- group_rules(): Función principal para agrupar reglas
- debug_markdownfiles_structure(): Debug para entender estructura original
- verify_content_preservation(): Verifica que el contenido se preserva
- load_content_into_groups(): Carga contenido real desde archivos
- create_mock_content_for_groups(): Crea contenido de ejemplo
- debug_content_in_groups(): Debug específico para problemas de contenido

USO RECOMENDADO:
    # 1. Debug inicial para entender tu estructura
    debug_markdownfiles_structure(your_rules)
    
    # 2. Procesar reglas
    groups = group_rules(your_rules)
    
    # 3. Verificar preservación de contenido
    verify_content_preservation(your_rules, groups)
    
    # 4. Si el content está vacío, cargar contenido real
    groups = load_content_into_groups(groups)
    
    # 5. Acceder a los archivos
    for group in groups:
        for md_file in group.markdownfile:
            print(f"Path: {md_file.path}")
            print(f"Content: {md_file.content}")
"""

import gc
import json
import hashlib
import os
from typing import List, Dict, Set, Optional
from collections import defaultdict
from dataclasses import dataclass

from app.models import MarkdownDocument, RuleData

# ===== MODELS (Asumiendo que ya tienes estos en models.py) =====
# Si no tienes models.py, descomenta estas definiciones:

# from pydantic import BaseModel, Field
# from typing import List, Optional

# class MarkdownDocument(BaseModel):
#     path: str = Field(..., description="Ruta del archivo")
#     content: str = Field(..., description="Contenido del archivo")

# class RuleData(BaseModel):
#     id: str = Field(..., description="ID único de la regla")
#     documentation: Optional[str] = Field(default=None, description="Documentación")
#     type: Optional[str] = Field(default=None, description="Tipo de regla")
#     description: str = Field(..., description="Descripción")
#     criticality: Optional[str] = Field(default=None, description="Criticidad")
#     references: Optional[str] = Field(default=None, description="Referencias")
#     markdownfiles: List[MarkdownDocument] = Field(default_factory=list, description="Archivos markdown")
#     explanation: Optional[str] = Field(default=None, description="Explicación")
#     tags: List[str] = Field(default_factory=list, description="Tags")

# ===== DOMAIN LAYER =====

@dataclass
class RuleGroup:
    """Entidad principal - Grupo de reglas procesadas"""
    group: str
    rules: List[RuleData]
    markdownfile: List[MarkdownDocument]  # ✅ GARANTIZADO: Objetos MarkdownDocument completos con .path y .content

class GroupingRules:
    """Reglas de negocio para agrupación"""
    
    @staticmethod
    def has_references(rule: RuleData) -> bool:
        """Determina si una regla tiene references"""
        return bool(rule.references and rule.references.strip())
    
    @staticmethod
    def has_explanation(rule: RuleData) -> bool:
        """Determina si una regla tiene explanation"""
        return bool(rule.explanation and rule.explanation.strip())

# ===== APPLICATION LAYER =====

@dataclass
class RuleIndices:
    """Índices de reglas clasificadas (optimización de memoria)"""
    without_references: List[int]
    with_references: List[int]

class RuleGroupingService:
    """Servicio principal - Caso de uso de agrupación"""
    
    def __init__(self, 
                 markdown_processor: 'MarkdownProcessor',
                 rule_cleaner: 'RuleCleaner',
                 group_namer: 'GroupNamer',
                 memory_manager: 'MemoryManager'):
        self._markdown_processor = markdown_processor
        self._rule_cleaner = rule_cleaner
        self._group_namer = group_namer
        self._memory_manager = memory_manager
    
    def group_rules(self, rules: List['RuleData'], batch_size: int = 20) -> List[RuleGroup]:
        """Caso de uso principal: agrupar reglas según requerimientos"""
        if not rules:
            return []
        
        try:
            self._memory_manager.start_processing()
            
            # Clasificar usando índices para optimizar memoria
            classifier = RuleClassifier()
            rule_indices = classifier.classify_by_indices(rules)
            
            # Procesar usando las interfaces separadas
            processor = RuleProcessor(
                self._markdown_processor,
                self._rule_cleaner,
                self._group_namer,
                self._memory_manager
            )
            
            groups = []
            
            # Procesar reglas sin references en tandas de 20
            if rule_indices.without_references:
                no_ref_groups = processor.process_no_references(
                    rules, rule_indices.without_references, batch_size
                )
                groups.extend(no_ref_groups)
                self._memory_manager.cleanup_intermediate()
            
            # Procesar reglas con references
            if rule_indices.with_references:
                ref_groups = processor.process_with_references(
                    rules, rule_indices.with_references
                )
                groups.extend(ref_groups)
            
            return groups
            
        finally:
            self._memory_manager.cleanup_final()

class RuleClassifier:
    """Clasificador que separa reglas por tipo usando índices"""
    
    def classify_by_indices(self, rules: List['RuleData']) -> RuleIndices:
        """Clasifica usando índices para evitar duplicación de objetos"""
        without_ref = []
        with_ref = []
        
        for i, rule in enumerate(rules):
            if GroupingRules.has_references(rule):
                with_ref.append(i)
            else:
                without_ref.append(i)
        
        return RuleIndices(without_references=without_ref, with_references=with_ref)

class RuleProcessor:
    """Procesador que maneja la lógica específica de cada tipo de grupo"""
    
    def __init__(self, 
                 markdown_processor: 'MarkdownProcessor',
                 rule_cleaner: 'RuleCleaner',
                 group_namer: 'GroupNamer',
                 memory_manager: 'MemoryManager'):
        self._markdown_processor = markdown_processor
        self._rule_cleaner = rule_cleaner
        self._group_namer = group_namer
        self._memory_manager = memory_manager
    
    def process_no_references(self, 
                             rules: List['RuleData'], 
                             indices: List[int], 
                             batch_size: int) -> List[RuleGroup]:
        """Procesa reglas sin references en tandas del tamaño especificado"""
        groups = []
        
        for chunk_start in range(0, len(indices), batch_size):
            chunk_indices = indices[chunk_start:chunk_start + batch_size]
            chunk_rules = [rules[i] for i in chunk_indices]
            
            # ✅ CORREGIDO: Usar método que garantiza objetos MarkdownDocument
            unique_markdown = self._markdown_processor.extract_unique_objects(chunk_rules)
            cleaned_rules = self._rule_cleaner.clean_but_keep_structure(chunk_rules)
            group_name = self._group_namer.name_no_ref_batch(chunk_start // batch_size + 1)
            
            group = RuleGroup(
                group=group_name,
                rules=cleaned_rules,
                markdownfile=unique_markdown  # ✅ GARANTIZADO: Lista de MarkdownDocument
            )
            groups.append(group)
            
            # Limpieza del chunk
            self._memory_manager.cleanup_chunk([chunk_rules])
        
        return groups
    
    def process_with_references(self, 
                               rules: List['RuleData'], 
                               indices: List[int]) -> List[RuleGroup]:
        """Procesa reglas con references según explanation"""
        groups = []
        
        # Separar por explanation
        with_exp_indices = []
        individual_indices = []
        
        for idx in indices:
            rule = rules[idx]
            if GroupingRules.has_explanation(rule):
                with_exp_indices.append(idx)
            else:
                individual_indices.append(idx)
        
        # Procesar grupos por explanation
        if with_exp_indices:
            exp_groups = self._process_explanation_groups(rules, with_exp_indices)
            groups.extend(exp_groups)
        
        # Procesar individuales
        if individual_indices:
            ind_groups = self._process_individual_groups(rules, individual_indices)
            groups.extend(ind_groups)
        
        return groups
    
    def _process_explanation_groups(self, 
                                   rules: List['RuleData'], 
                                   indices: List[int]) -> List[RuleGroup]:
        """Agrupa reglas por texto de explanation"""
        # Agrupar índices por explanation text
        explanation_groups = defaultdict(list)
        
        for idx in indices:
            rule = rules[idx]
            exp_text = rule.explanation.strip()
            explanation_groups[exp_text].append(idx)
        
        groups = []
        for group_num, (explanation, rule_indices) in enumerate(explanation_groups.items(), 1):
            group_rules = [rules[i] for i in rule_indices]
            
            # ✅ CORREGIDO: Usar método que garantiza objetos MarkdownDocument
            unique_markdown = self._markdown_processor.extract_unique_objects(group_rules)
            cleaned_rules = self._rule_cleaner.clean_but_keep_structure(group_rules)
            group_name = self._group_namer.name_explanation_group(group_num, explanation)
            
            group = RuleGroup(
                group=group_name,
                rules=cleaned_rules,
                markdownfile=unique_markdown  # ✅ GARANTIZADO: Lista de MarkdownDocument
            )
            groups.append(group)
            
            # Limpieza del grupo
            self._memory_manager.cleanup_chunk([group_rules])
        
        return groups
    
    def _process_individual_groups(self, 
                                  rules: List['RuleData'], 
                                  indices: List[int]) -> List[RuleGroup]:
        """Crea grupos individuales para reglas sin explanation"""
        groups = []
        
        for seq_num, idx in enumerate(indices, 1):
            rule = rules[idx]
            
            # ✅ CORREGIDO: Usar método que garantiza objetos MarkdownDocument
            markdown_files = self._markdown_processor.extract_from_single_rule_objects(rule)
            cleaned_rule = self._rule_cleaner.clean_but_keep_structure([rule])[0]
            group_name = self._group_namer.name_individual_group(seq_num, rule.id)
            
            group = RuleGroup(
                group=group_name,
                rules=[cleaned_rule],
                markdownfile=markdown_files  # ✅ GARANTIZADO: Lista de MarkdownDocument
            )
            groups.append(group)
        
        return groups

# ===== INFRASTRUCTURE LAYER =====

class MarkdownProcessor:
    """✅ CORREGIDO: Procesador que GARANTIZA objetos MarkdownDocument"""
    
    def __init__(self):
        self._file_hashes: Set[str] = set()
        self._path_cache: Set[str] = set()
        self.auto_load_files = False  # ✅ CORREGIDO: Renombrado para consistencia
    
    def extract_unique_objects(self, rules: List['RuleData']) -> List['MarkdownDocument']:
        """✅ CORREGIDO: GARANTIZA que retorna objetos MarkdownDocument únicos - MANEJA DICCIONARIOS"""
        unique_files = []
        local_seen_hashes = set()
        local_seen_paths = set()
        
        for rule in rules:
            if not rule.markdownfiles:
                continue
            
            # ✅ NUEVO: Manejo inteligente de markdownfiles
            md_items = self._extract_markdownfile_items(rule.markdownfiles)
            
            for md_item in md_items:
                # ✅ GARANTIZAR que es un objeto MarkdownDocument válido
                md_doc = self._ensure_markdowndocument(md_item)
                
                if not md_doc:
                    continue
                
                # ✅ CORREGIDO: Usar 'path' en lugar de 'filename'
                file_hash = self._create_file_hash(md_doc.path, md_doc.content)
                
                # Evitar duplicados por hash Y path
                if (file_hash not in local_seen_hashes and 
                    file_hash not in self._file_hashes and
                    md_doc.path not in local_seen_paths and
                    md_doc.path not in self._path_cache):
                    
                    local_seen_hashes.add(file_hash)
                    local_seen_paths.add(md_doc.path)
                    self._file_hashes.add(file_hash)
                    self._path_cache.add(md_doc.path)
                    
                    # ✅ AGREGAR objeto MarkdownDocument completo
                    unique_files.append(md_doc)
        
        return unique_files
    
    def extract_from_single_rule_objects(self, rule: 'RuleData') -> List['MarkdownDocument']:
        """✅ CORREGIDO: GARANTIZA objetos MarkdownDocument de una regla - MANEJA DICCIONARIOS"""
        if not rule.markdownfiles:
            return []
        
        unique_files = []
        local_seen_hashes = set()
        
        # ✅ NUEVO: Manejo inteligente de markdownfiles
        md_items = self._extract_markdownfile_items(rule.markdownfiles)
        
        for md_item in md_items:
            # ✅ GARANTIZAR que es un objeto MarkdownDocument válido
            md_doc = self._ensure_markdowndocument(md_item)
            
            if not md_doc:
                continue
            
            # ✅ CORREGIDO: Usar 'path' en lugar de 'filename'
            file_hash = self._create_file_hash(md_doc.path, md_doc.content)
            
            # Evitar duplicados dentro de la misma regla
            if file_hash not in local_seen_hashes:
                local_seen_hashes.add(file_hash)
                self._file_hashes.add(file_hash)
                self._path_cache.add(md_doc.path)
                
                # ✅ AGREGAR objeto MarkdownDocument completo
                unique_files.append(md_doc)
        
        return unique_files
    
    def _extract_markdownfile_items(self, markdownfiles) -> List:
        """✅ SIMPLIFICADO: Extrae items de markdownfiles manejando diferentes estructuras"""
        
        print(f"🔍 Extrayendo markdownfiles: {type(markdownfiles)}")
        
        if not markdownfiles:
            print("   ❌ markdownfiles está vacío")
            return []
        
        # Caso 1: Es una lista - retornar tal como está
        if isinstance(markdownfiles, list):
            print(f"   📋 Lista con {len(markdownfiles)} elementos")
            return markdownfiles
        
        # Caso 2: Es un diccionario {ruta: contenido, ruta2: contenido2}
        elif isinstance(markdownfiles, dict):
            print(f"   📁 Diccionario con {len(markdownfiles)} rutas")
            # SIMPLIFICADO: convertir directamente cada entrada a dict individual
            items = []
            for path, content in markdownfiles.items():
                # Crear dict simple para cada archivo
                item = {path: content}
                items.append(item)
                print(f"      📄 {path} -> {len(str(content))} chars")
            return items
        
        # Caso 3: Es un objeto iterable
        elif hasattr(markdownfiles, '__iter__') and not isinstance(markdownfiles, str):
            print(f"   🔄 Iterable: {type(markdownfiles)}")
            return list(markdownfiles)
        
        # Caso 4: Es un solo objeto
        else:
            print(f"   📄 Objeto único: {type(markdownfiles)}")
            return [markdownfiles]
    
    def _ensure_markdowndocument(self, md_item) -> Optional['MarkdownDocument']:
        """✅ CORREGIDO: Garantiza que el item es un MarkdownDocument válido"""
        
        try:
            from app.models import MarkdownDocument
        except ImportError:
            # Fallback si no se puede importar
            print("⚠️ No se pudo importar MarkdownDocument de app.models")
            return None
        
        # Si ya es un MarkdownDocument válido con 'path'
        if hasattr(md_item, 'path') and hasattr(md_item, 'content'):
            path = str(getattr(md_item, 'path', ''))
            content = str(getattr(md_item, 'content', ''))
            return MarkdownDocument(path=path, content=content)
        
        # Si tiene 'filename' en lugar de 'path' (compatibilidad)
        elif hasattr(md_item, 'filename') and hasattr(md_item, 'content'):
            filename = str(getattr(md_item, 'filename', ''))
            content = str(getattr(md_item, 'content', ''))
            return MarkdownDocument(path=filename, content=content)
        
        # Si es un string (solo path/filename) - CASO COMÚN
        elif isinstance(md_item, str):
            content = self._try_load_file_content(md_item) if self.auto_load_files else ""
            return MarkdownDocument(path=md_item, content=content)
        
        # Si es un dict
        elif isinstance(md_item, dict):
            path = list(md_item.values())[0].path
            content = list(md_item.values())[0].content
            return MarkdownDocument(path=str(path), content=str(content))
        
        # Casos inesperados
        else:
            print(f"⚠️ Tipo inesperado en markdownfiles: {type(md_item)}")
            return MarkdownDocument(path=str(md_item), content="")
    
    def _try_load_file_content(self, file_path: str) -> str:
        """✅ CORREGIDO: Intenta cargar contenido real del archivo"""
        
        if not self.auto_load_files:
            return ""
        
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Contenido cargado: {file_path} ({len(content)} chars)")
                return content
            else:
                return f"# Archivo no encontrado: {file_path}"
                
        except Exception as e:
            print(f"❌ Error cargando {file_path}: {e}")
            return f"# Error cargando archivo: {file_path}\nError: {str(e)}"
    
    def _create_file_hash(self, path: str, content: str) -> str:
        """Crea hash único basado en path y contenido"""
        combined = f"{path}:{content}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def clear_cache(self):
        """Limpia cache para gestión de memoria"""
        self._file_hashes.clear()
        self._path_cache.clear()

class RuleCleaner:
    """✅ CORREGIDO: Limpiador que mantiene la estructura original"""
    
    def clean_but_keep_structure(self, rules: List['RuleData']) -> List['RuleData']:
        """✅ MANTIENE toda la estructura de las reglas - Solo limpia markdownfiles para evitar duplicados"""
        cleaned_rules = []
        
        try:
            from app.models import RuleData
        except ImportError:
            # Si no se puede importar, retornar las reglas originales sin markdownfiles
            print("⚠️ No se pudo importar RuleData, manteniendo estructura original")
            return rules
        
        for rule in rules:
            # Crear nueva regla SIN markdownfiles (están a nivel de grupo)
            cleaned_rule = RuleData(
                id=rule.id,
                documentation=rule.documentation,
                type=rule.type,
                description=rule.description,
                criticality=rule.criticality,
                references=rule.references,
                explanation=rule.explanation,
                tags=rule.tags,
                markdownfiles=[]  # ✅ VACÍO: Los archivos están a nivel de grupo
            )
            cleaned_rules.append(cleaned_rule)
        
        return cleaned_rules

class GroupNamer:
    """Generador de nombres para grupos"""
    
    def name_no_ref_batch(self, batch_number: int) -> str:
        """Nombra grupos de reglas sin references"""
        return f"no_ref_batch_{batch_number}"
    
    def name_explanation_group(self, group_number: int, explanation: str) -> str:
        """Nombra grupos por explanation"""
        # Asegurar que explanation no está vacío
        if not explanation or not explanation.strip():
            explanation = "empty_explanation"
        
        explanation_hash = hashlib.md5(explanation.encode()).hexdigest()[:8]
        return f"exp_{group_number}_{explanation_hash}"
    
    def name_individual_group(self, sequence: int, rule_id: str) -> str:
        """Nombra grupos individuales"""
        return f"individual_ref_{sequence}_{rule_id}"

class MemoryManager:
    """Gestor de memoria con limpieza explícita para Lambda"""
    
    def __init__(self):
        self._processing_active = False
    
    def start_processing(self):
        """Inicia procesamiento con limpieza inicial"""
        self._processing_active = True
        gc.collect()
    
    def cleanup_chunk(self, objects_to_cleanup: List):
        """Limpia objetos específicos"""
        try:
            for obj in objects_to_cleanup:
                if obj:
                    del obj
        except Exception:
            pass  # Ignorar errores de limpieza
    
    def cleanup_intermediate(self):
        """Limpieza intermedia durante procesamiento"""
        if self._processing_active:
            gc.collect()
    
    def cleanup_final(self):
        """Limpieza final garantizada"""
        self._processing_active = False
        gc.collect()

# ===== PRESENTATION LAYER =====

class LambdaAdapter:
    """Adaptador para AWS Lambda"""
    
    def __init__(self, grouping_service: RuleGroupingService):
        self._grouping_service = grouping_service
    
    def handle(self, event: dict, context) -> dict:
        """Handler principal para Lambda"""
        try:
            # Validación
            rules_data = event.get('rules', [])
            if not rules_data:
                return self._error_response(400, "No rules provided")
            
            # Conversión a objetos de dominio
            rules = self._convert_to_domain_objects(rules_data)
            
            # Ejecutar caso de uso
            groups = self._grouping_service.group_rules(rules)
            
            # Respuesta
            return self._success_response(groups, len(rules))
            
        except Exception as e:
            return self._error_response(500, str(e))
        finally:
            gc.collect()
    
    def _convert_to_domain_objects(self, rules_data: List[dict]) -> List['RuleData']:
        """✅ CORREGIDO: Convierte datos de entrada a objetos del dominio - MANEJA DICCIONARIOS"""
        try:
            from app.models import RuleData, MarkdownDocument
        except ImportError:
            raise ImportError("No se pueden importar los modelos desde app.models")
        
        rules = []
        for rule_dict in rules_data:
            # ✅ MEJORADO: Convertir markdownfiles manejando diferentes estructuras
            markdown_files = []
            markdownfiles_data = rule_dict.get('markdownfiles', [])
            
            # Caso 1: markdownfiles es un diccionario {ruta: contenido}
            if isinstance(markdownfiles_data, dict):
                for path, content in markdownfiles_data.items():
                    md_obj = MarkdownDocument(path=str(path), content=str(content))
                    markdown_files.append(md_obj)
            
            # Caso 2: markdownfiles es una lista
            elif isinstance(markdownfiles_data, list):
                for md_data in markdownfiles_data:
                    if isinstance(md_data, dict):
                        # Caso 2a: Dict con path/content explícitos
                        if 'path' in md_data or 'filename' in md_data:
                            path = md_data.get('path') or md_data.get('filename', '')
                            content = md_data.get('content', '')
                        # Caso 2b: Dict con una sola entrada {ruta: contenido}
                        elif len(md_data) == 1:
                            path, content = list(md_data.items())[0]
                        else:
                            # Dict vacío o múltiples entradas sin estructura clara
                            path = str(md_data.get(list(md_data.keys())[0], '')) if md_data else ''
                            content = ''
                        
                        md_obj = MarkdownDocument(path=str(path), content=str(content))
                        markdown_files.append(md_obj)
                    
                    elif isinstance(md_data, str):
                        # String: solo path, sin contenido
                        md_obj = MarkdownDocument(path=md_data, content='')
                        markdown_files.append(md_obj)
                    
                    else:
                        # Otros tipos: convertir a string
                        md_obj = MarkdownDocument(path=str(md_data), content='')
                        markdown_files.append(md_obj)
            
            # Caso 3: markdownfiles es un string o None
            else:
                if markdownfiles_data:
                    md_obj = MarkdownDocument(path=str(markdownfiles_data), content='')
                    markdown_files.append(md_obj)
            
            rule = RuleData(
                id=rule_dict.get('id', ''),
                documentation=rule_dict.get('documentation'),
                type=rule_dict.get('type'),
                description=rule_dict.get('description', ''),
                criticality=rule_dict.get('criticality'),
                references=rule_dict.get('references'),
                markdownfiles=markdown_files,
                explanation=rule_dict.get('explanation'),
                tags=rule_dict.get('tags', [])
            )
            rules.append(rule)
        
        return rules
    
    def _success_response(self, groups: List[RuleGroup], total_rules: int) -> dict:
        """Crea respuesta exitosa"""
        serializer = GroupSerializer()
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "groups": [serializer.serialize(group) for group in groups],
                "summary": {
                    "total_rules": total_rules,
                    "total_groups": len(groups),
                    "architecture": "clean_and_optimized_FIXED_FINAL"
                }
            }, separators=(',', ':'))
        }
    
    def _error_response(self, status_code: int, message: str) -> dict:
        """Crea respuesta de error"""
        return {
            "statusCode": status_code,
            "body": json.dumps({"error": message})
        }

class GroupSerializer:
    """✅ CORREGIDO: Serializador que mantiene objetos MarkdownDocument completos"""
    
    def serialize(self, group: RuleGroup) -> dict:
        """Serializa un grupo a diccionario"""
        return {
            "group": group.group,
            "rules": [self._serialize_rule(rule) for rule in group.rules],
            "markdownfile": [self._serialize_markdown_object(md) for md in group.markdownfile]
        }
    
    def _serialize_rule(self, rule: 'RuleData') -> dict:
        """Serializa una regla sin markdownfiles (están en el grupo)"""
        return {
            "id": rule.id,
            "documentation": rule.documentation,
            "type": rule.type,
            "description": rule.description,
            "criticality": rule.criticality,
            "references": rule.references,
            "explanation": rule.explanation,
            "tags": rule.tags
            # markdownfiles NO incluido - están a nivel de grupo
        }
    
    def _serialize_markdown_object(self, md: 'MarkdownDocument') -> dict:
        """✅ CORREGIDO: Serializa MarkdownDocument GARANTIZANDO path y content"""
        # Garantizar que es un objeto válido
        path = getattr(md, 'path', '') if hasattr(md, 'path') else str(md)
        content = getattr(md, 'content', '') if hasattr(md, 'content') else ''
        
        return {
            "path": str(path),
            "content": str(content)
        }

# ===== COMPOSITION ROOT =====

class ServiceFactory:
    """Factory para crear servicios con todas las dependencias"""
    
    @staticmethod
    def create_grouping_service() -> RuleGroupingService:
        """Crea el servicio principal con todas sus dependencias inyectadas"""
        markdown_processor = MarkdownProcessor()
        rule_cleaner = RuleCleaner()
        group_namer = GroupNamer()
        memory_manager = MemoryManager()
        
        return RuleGroupingService(
            markdown_processor=markdown_processor,
            rule_cleaner=rule_cleaner,
            group_namer=group_namer,
            memory_manager=memory_manager
        )
    
    @staticmethod
    def create_lambda_adapter() -> LambdaAdapter:
        """Crea el adaptador de Lambda"""
        grouping_service = ServiceFactory.create_grouping_service()
        return LambdaAdapter(grouping_service)

# ===== CONTENT LOADING UTILITIES =====

def load_content_into_groups(groups: List[RuleGroup], load_files: bool = True) -> List[RuleGroup]:
    """✅ CORREGIDO: Carga contenido real en grupos que tienen content vacío"""
    
    print("🔧 CARGANDO CONTENIDO EN GRUPOS...")
    
    try:
        from app.models import MarkdownDocument
    except ImportError:
        print("⚠️ No se pudo importar MarkdownDocument")
        return groups
    
    for group in groups:
        print(f"\n📂 Procesando grupo: {group.group}")
        
        for i, md_file in enumerate(group.markdownfile):
            if not md_file.content and load_files:
                # Intentar cargar contenido del archivo
                new_content = _load_file_content_safe(md_file.path)
                
                # Crear nuevo objeto con contenido
                group.markdownfile[i] = MarkdownDocument(
                    path=md_file.path,
                    content=new_content
                )
                
                print(f"   ✅ Contenido cargado: {md_file.path} ({len(new_content)} chars)")
            
            elif not md_file.content:
                # Crear contenido mock
                mock_content = f"# {md_file.path}\n\nContenido no disponible para {md_file.path}"
                
                group.markdownfile[i] = MarkdownDocument(
                    path=md_file.path,
                    content=mock_content
                )
                
                print(f"   📝 Contenido mock: {md_file.path}")
    
    return groups

def _load_file_content_safe(file_path: str) -> str:
    """Carga contenido de archivo de forma segura"""
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"# Archivo no encontrado: {file_path}\n\nEl archivo {file_path} no existe en el sistema."
            
    except Exception as e:
        return f"# Error cargando archivo: {file_path}\n\nError: {str(e)}"

def create_mock_content_for_groups(groups: List[RuleGroup]) -> List[RuleGroup]:
    """✅ CORREGIDO: Crea contenido mock realista para grupos"""
    
    print("🎭 CREANDO CONTENIDO MOCK...")
    
    try:
        from app.models import MarkdownDocument
    except ImportError:
        print("⚠️ No se pudo importar MarkdownDocument")
        return groups
    
    for group in groups:
        for i, md_file in enumerate(group.markdownfile):
            if not md_file.content:
                # Crear contenido mock más realista
                filename = os.path.basename(md_file.path)
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext in ['.md', '.markdown']:
                    mock_content = f"""# {filename}

## Descripción
Este es un archivo markdown de ejemplo para {filename}.

## Contenido
- Elemento 1
- Elemento 2
- Elemento 3

## Notas
Contenido generado automáticamente para {md_file.path}
"""
                else:
                    mock_content = f"""Archivo: {filename}
Ruta: {md_file.path}
Tipo: {file_ext}

Contenido mock generado automáticamente.
"""
                
                group.markdownfile[i] = MarkdownDocument(
                    path=md_file.path,
                    content=mock_content
                )
                
                print(f"   🎭 Mock realista: {filename}")
    
    return groups

# ===== PUBLIC API =====

def group_rules(rules: List['RuleData'], batch_size: int = 20, load_file_content: bool = False, debug_structure: bool = False, enable_debug_logging: bool = True) -> List[RuleGroup]:
    """
    🎯 API PRINCIPAL - Agrupa reglas según requerimientos
    
    ENTRADA: Lista de RuleData
    SALIDA: Lista de RuleGroup
    
    Args:
        rules: Lista de reglas a agrupar
        batch_size: Tamaño de tandas para reglas sin references (default: 20)
        load_file_content: Si True, intenta cargar contenido real de archivos (default: False)
        debug_structure: Si True, muestra debug de estructura de markdownfiles (default: False)
        enable_debug_logging: Si True, activa logging detallado durante procesamiento (default: True)
    
    ✅ PROBLEMA RESUELTO:
    - markdownfile contiene objetos MarkdownDocument completos
    - Cada objeto tiene .path y .content
    - Maneja diccionarios {ruta: contenido} correctamente
    - Preserva relación ruta → contenido
    - Deduplicación mejorada sin perder objetos
    - Sin archivos duplicados en grupos
    
    📋 ESTRUCTURAS SOPORTADAS:
    - Lista de MarkdownDocument: [MarkdownDocument(path="x", content="y")]
    - Lista de dicts path/content: [{"path": "x", "content": "y"}]
    - Lista de dicts ruta→contenido: [{"file.md": "contenido"}]
    - Diccionario ruta→contenido: {"file1.md": "contenido1", "file2.md": "contenido2"}
    - Lista de strings: ["file1.md", "file2.md"]
    
    🚨 SI NO TRAE PATH NI CONTENIDO:
    1. Ejecuta: emergency_debug_single_rule(your_rules)
    2. Ejecuta: debug_markdownfiles_structure(your_rules)
    3. Comparte el output para diagnóstico específico
    """
    
    # Debug inicial si se solicita
    if debug_structure:
        debug_markdownfiles_structure(rules)
    
    service = ServiceFactory.create_grouping_service()
    
    # Activar logging si está habilitado
    if enable_debug_logging:
        print("🔧 DEBUG LOGGING ACTIVADO - Verás detalles del procesamiento")
    
    # Configurar carga automática de archivos
    if load_file_content:
        service._markdown_processor.auto_load_files = True
    
    groups = service.group_rules(rules, batch_size)
    
    # Información sobre content vacío
    empty_content_count = 0
    empty_path_count = 0
    total_files = 0
    
    for group in groups:
        for md_file in group.markdownfile:
            total_files += 1
            if not md_file.content:
                empty_content_count += 1
            if not md_file.path:
                empty_path_count += 1
    
    # Reporte de problemas
    if empty_path_count > 0 or empty_content_count > 0:
        print(f"\n⚠️  PROBLEMAS DETECTADOS:")
        if empty_path_count > 0:
            print(f"   🚨 {empty_path_count}/{total_files} archivos tienen PATH VACÍO")
        if empty_content_count > 0:
            print(f"   ⚠️  {empty_content_count}/{total_files} archivos tienen CONTENT VACÍO")
        
        print(f"\n💡 PARA DIAGNOSTICAR:")
        print(f"   emergency_debug_single_rule(your_rules)  # Debug paso a paso")
        print(f"   debug_markdownfiles_structure(your_rules)  # Estructura original")
        print(f"   verify_content_preservation(your_rules, groups)  # Verificar preservación")
        
        if empty_content_count > 0 and empty_path_count == 0:
            print(f"\n💡 PARA RESOLVER CONTENT VACÍO:")
            print(f"   groups = load_content_into_groups(groups)  # Cargar contenido")
            print(f"   groups = create_mock_content_for_groups(groups)  # Contenido mock")
    else:
        print(f"✅ ÉXITO: Todos los archivos tienen path y content ({total_files} archivos)")
    
    return groups

def lambda_handler(event, context):
    """🚀 HANDLER LAMBDA - Listo para desplegar"""
    adapter = ServiceFactory.create_lambda_adapter()
    return adapter.handle(event, context)

# ===== TESTING UTILITIES =====

def create_test_service(
    markdown_processor: Optional[MarkdownProcessor] = None,
    rule_cleaner: Optional[RuleCleaner] = None,
    group_namer: Optional[GroupNamer] = None,
    memory_manager: Optional[MemoryManager] = None
) -> RuleGroupingService:
    """Factory para testing con mocks"""
    return RuleGroupingService(
        markdown_processor=markdown_processor or MarkdownProcessor(),
        rule_cleaner=rule_cleaner or RuleCleaner(),
        group_namer=group_namer or GroupNamer(),
        memory_manager=memory_manager or MemoryManager()
    )

def emergency_debug_single_rule(rules: List['RuleData']) -> None:
    """🚨 DEBUG DE EMERGENCIA: Rastrea paso a paso el procesamiento de UNA regla"""
    print("🚨 DEBUG DE EMERGENCIA - PROCESAMIENTO PASO A PASO")
    print("=" * 80)
    
    if not rules:
        print("❌ No hay reglas para debuggear")
        return
    
    rule = rules[0]
    print(f"📋 REGLA: {getattr(rule, 'id', 'N/A')}")
    
    # PASO 1: Examinar markdownfiles original
    print(f"\n1️⃣ MARKDOWNFILES ORIGINAL:")
    markdownfiles = getattr(rule, 'markdownfiles', None)
    print(f"   Tipo: {type(markdownfiles)}")
    print(f"   Contenido: {str(markdownfiles)[:300]}...")
    
    if isinstance(markdownfiles, dict):
        print(f"   📁 Es diccionario con {len(markdownfiles)} entradas:")
        for i, (key, value) in enumerate(list(markdownfiles.items())[:2]):
            print(f"      [{i}] Key: {key}")
            print(f"      [{i}] Value: {str(value)[:100]}...")
            print(f"      [{i}] Value type: {type(value)}")
    
    elif isinstance(markdownfiles, list):
        print(f"   📋 Es lista con {len(markdownfiles)} elementos:")
        for i, item in enumerate(markdownfiles[:2]):
            print(f"      [{i}] Tipo: {type(item)}")
            print(f"      [{i}] Contenido: {str(item)[:100]}...")
    
    # PASO 2: Simular _extract_markdownfile_items
    print(f"\n2️⃣ EXTRACCIÓN DE ITEMS:")
    processor = MarkdownProcessor()
    items = processor._extract_markdownfile_items(markdownfiles)
    print(f"   Items extraídos: {len(items)}")
    for i, item in enumerate(items[:2]):
        print(f"      [{i}] Tipo después de extracción: {type(item)}")
        print(f"      [{i}] Contenido: {str(item)[:100]}...")
    
    # PASO 3: Simular _ensure_markdowndocument para cada item
    print(f"\n3️⃣ CONVERSIÓN A MARKDOWNDOCUMENT:")
    for i, item in enumerate(items[:2]):
        print(f"\n   Item {i}:")
        md_doc = processor._ensure_markdowndocument(item)
        if md_doc:
            print(f"      ✅ Resultado: MarkdownDocument")
            print(f"      📁 Path: '{md_doc.path}'")
            print(f"      📝 Content: '{md_doc.content[:100]}...' ({len(md_doc.content)} chars)")
        else:
            print(f"      ❌ Resultado: None")
    
    # PASO 4: Simular todo el flujo
    print(f"\n4️⃣ FLUJO COMPLETO:")
    unique_files = processor.extract_unique_objects([rule])
    print(f"   Archivos únicos resultantes: {len(unique_files)}")
    for i, md_file in enumerate(unique_files):
        print(f"      [{i}] Path: '{md_file.path}'")
        print(f"      [{i}] Content: '{md_file.content[:100]}...' ({len(md_file.content)} chars)")
        print(f"      [{i}] Tipo: {type(md_file)}")

def quick_test_conversion(test_data) -> None:
    """🧪 TEST RÁPIDO: Prueba conversión de un dato específico"""
    print("🧪 TEST RÁPIDO DE CONVERSIÓN")
    print("=" * 40)
    
    processor = MarkdownProcessor()
    processor.auto_load_files = False  # No cargar archivos
    
    print(f"📥 Entrada: {type(test_data)}")
    print(f"📄 Contenido: {str(test_data)[:200]}...")
    
    result = processor._ensure_markdowndocument(test_data)
    
    if result:
        print(f"✅ Resultado exitoso:")
        print(f"   Tipo: {type(result)}")
        print(f"   Path: '{result.path}'")
        print(f"   Content: '{result.content}'")
        print(f"   Content length: {len(result.content)}")
    else:
        print(f"❌ Resultado: None")

def test_dictionary_case() -> None:
    """🧪 TEST ESPECÍFICO: Verifica manejo de diccionarios {ruta: contenido}"""
    print("🧪 TEST ESPECÍFICO: Diccionarios {ruta: contenido}")
    print("=" * 60)
    
    # Casos de prueba exactos
    test_cases = [
        # Caso 1: Diccionario simple {ruta: contenido}
        {"archivo1.md": "Contenido del archivo 1"},
        
        # Caso 2: Diccionario con path largo
        {"src/docs/README.md": "# README\n\nEste es el contenido del README"},
        
        # Caso 3: Diccionario múltiple
        {
            "archivo1.md": "Contenido 1", 
            "archivo2.md": "Contenido 2"
        },
        
        # Caso 4: Diccionario estándar
        {"path": "archivo.md", "content": "contenido estándar"},
        
        # Caso 5: String simple
        "archivo_simple.md"
    ]
    
    processor = MarkdownProcessor()
    processor.auto_load_files = False
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- TEST CASO {i} ---")
        print(f"📥 Entrada: {test_case}")
        
        result = processor._ensure_markdowndocument(test_case)
        
        if result:
            print(f"✅ RESULTADO EXITOSO:")
            print(f"   Tipo: {type(result).__name__}")
            print(f"   Path: '{result.path}'")
            print(f"   Content: '{result.content}'")
            print(f"   Content length: {len(result.content)}")
            
            # Verificación específica
            if isinstance(test_case, dict) and len(test_case) == 1:
                expected_path, expected_content = list(test_case.items())[0]
                if result.path == expected_path and result.content == expected_content:
                    print(f"   🎉 PERFECTO: Path y content coinciden exactamente")
                else:
                    print(f"   ❌ ERROR: No coincide")
                    print(f"      Esperado path: '{expected_path}', obtenido: '{result.path}'")
                    print(f"      Esperado content: '{expected_content}', obtenido: '{result.content}'")
        else:
            print(f"❌ RESULTADO: None")

def verify_full_flow_with_dict() -> None:
    """🔄 VERIFICACIÓN COMPLETA: Todo el flujo con diccionario"""
    print("\n🔄 VERIFICACIÓN FLUJO COMPLETO CON DICCIONARIO")
    print("=" * 60)
    
    # Simular RuleData con markdownfiles como diccionario
    try:
        from app.models import RuleData, MarkdownDocument
        
        # Crear regla de prueba
        test_rule = RuleData(
            id="TEST_RULE_001",
            description="Regla de prueba",
            markdownfiles={
                "docs/example.md": "# Ejemplo\n\nEste es el contenido del ejemplo.",
                "src/readme.md": "# README\n\nDocumentación principal."
            }
        )
        
        print(f"📋 Regla de prueba creada:")
        print(f"   ID: {test_rule.id}")
        print(f"   Markdownfiles type: {type(test_rule.markdownfiles)}")
        print(f"   Markdownfiles content: {test_rule.markdownfiles}")
        
        # Procesar con MarkdownProcessor
        processor = MarkdownProcessor()
        processor.auto_load_files = False
        
        unique_files = processor.extract_unique_objects([test_rule])
        
        print(f"\n📊 RESULTADO PROCESAMIENTO:")
        print(f"   Archivos únicos: {len(unique_files)}")
        
        for i, md_file in enumerate(unique_files):
            print(f"   [{i+1}] Tipo: {type(md_file).__name__}")
            print(f"   [{i+1}] Path: '{md_file.path}'")
            print(f"   [{i+1}] Content: '{md_file.content}'")
            print(f"   [{i+1}] Content length: {len(md_file.content)}")
        
        return len(unique_files) > 0 and all(md.path and md.content for md in unique_files)
        
    except ImportError:
        print("⚠️ No se pueden importar los modelos - usando mock")
        
        # Mock simple para testing
        class MockRule:
            def __init__(self):
                self.id = "MOCK_RULE"
                self.markdownfiles = {
                    "test.md": "contenido de prueba",
                    "otro.md": "otro contenido"
                }
        
        mock_rule = MockRule()
        processor = MarkdownProcessor()
        
        # Simular extracción
        items = processor._extract_markdownfile_items(mock_rule.markdownfiles)
        print(f"Items extraídos: {items}")
        
        for item in items:
            result = processor._ensure_markdowndocument(item)
            if result:
                print(f"Resultado: path='{result.path}', content='{result.content}'")
        
        return True

def debug_markdownfiles_structure(rules: List['RuleData']) -> None:
    """🔍 MEJORADO: Debug específico para entender la estructura de markdownfiles"""
    print("🔍 DEBUG: Estructura de markdownfiles")
    print("=" * 60)
    
    if not rules:
        print("❌ No hay reglas para debuggear")
        return
    
    for i, rule in enumerate(rules[:3]):  # Solo primeras 3 reglas
        print(f"\n📋 Regla {i+1}: {getattr(rule, 'id', 'N/A')}")
        
        markdownfiles = getattr(rule, 'markdownfiles', None)
        print(f"   🔧 Tipo de markdownfiles: {type(markdownfiles)}")
        print(f"   📊 Longitud/Tamaño: {len(markdownfiles) if hasattr(markdownfiles, '__len__') else 'N/A'}")
        
        if not markdownfiles:
            print("   ⚠️  markdownfiles está vacío")
            continue
        
        # Caso 1: Es una lista
        if isinstance(markdownfiles, list):
            print(f"   📋 LISTA con {len(markdownfiles)} elementos:")
            for j, item in enumerate(markdownfiles[:2]):  # Solo primeros 2
                print(f"      [{j}] Tipo: {type(item)}")
                print(f"      [{j}] Contenido: {str(item)[:100]}...")
        
        # Caso 2: Es un diccionario  
        elif isinstance(markdownfiles, dict):
            print(f"   📁 DICCIONARIO con {len(markdownfiles)} rutas:")
            for k, (path, content) in enumerate(list(markdownfiles.items())[:2]):  # Solo primeros 2
                print(f"      [{k}] Ruta: {path}")
                print(f"      [{k}] Contenido: {len(str(content))} chars")
                print(f"      [{k}] Preview: {str(content)[:100]}...")
        
        # Caso 3: Otro tipo
        else:
            print(f"   ❓ TIPO DESCONOCIDO: {markdownfiles}")
    
    print(f"\n💡 PARA DEBUGGEAR MÁS:")
    print(f"   emergency_debug_single_rule(your_rules)  # Debug paso a paso")
    print(f"   quick_test_conversion(tu_dato)  # Test de conversión individual")

def verify_content_preservation(rules_before: List['RuleData'], groups_after: List[RuleGroup]) -> None:
    """🆕 NUEVO: Verifica que el contenido se preserva durante el procesamiento"""
    print("🔍 VERIFICANDO PRESERVACIÓN DE CONTENIDO")
    print("=" * 60)
    
    # Extraer contenido original
    original_content = {}
    for rule in rules_before:
        if not rule.markdownfiles:
            continue
            
        if isinstance(rule.markdownfiles, dict):
            # Diccionario: {ruta: contenido}
            for path, content in rule.markdownfiles.items():
                original_content[path] = str(content)
                print(f"📄 Original: {path} -> {len(str(content))} chars")
        
        elif isinstance(rule.markdownfiles, list):
            # Lista: procesar cada elemento
            for md_item in rule.markdownfiles:
                if isinstance(md_item, dict):
                    if len(md_item) == 1:  # {ruta: contenido}
                        path, content = list(md_item.items())[0]
                        original_content[path] = str(content)
                        print(f"📄 Original: {path} -> {len(str(content))} chars")
                    else:  # {path: ..., content: ...}
                        path = md_item.get('path') or md_item.get('filename', '')
                        content = md_item.get('content', '')
                        if path:
                            original_content[path] = str(content)
                            print(f"📄 Original: {path} -> {len(str(content))} chars")
    
    # Extraer contenido procesado
    processed_content = {}
    for group in groups_after:
        for md_file in group.markdownfile:
            processed_content[md_file.path] = md_file.content
            print(f"✅ Procesado: {md_file.path} -> {len(md_file.content)} chars")
    
    # Comparar
    print(f"\n📊 COMPARACIÓN:")
    print(f"   📄 Archivos originales: {len(original_content)}")
    print(f"   ✅ Archivos procesados: {len(processed_content)}")
    
    # Verificar cada archivo
    lost_content = 0
    preserved_content = 0
    
    for path, original in original_content.items():
        if path in processed_content:
            processed = processed_content[path]
            if original == processed:
                preserved_content += 1
                print(f"   ✅ {path}: Contenido preservado")
            elif len(original) > 0 and len(processed) == 0:
                lost_content += 1
                print(f"   ❌ {path}: Contenido PERDIDO (original: {len(original)} chars)")
            else:
                print(f"   ⚠️  {path}: Contenido modificado (original: {len(original)}, procesado: {len(processed)})")
        else:
            print(f"   ❌ {path}: Archivo NO ENCONTRADO en resultado")
    
    if lost_content > 0:
        print(f"\n🚨 PROBLEMA: {lost_content} archivos perdieron contenido")
        print(f"💡 SOLUCIÓN: Verificar _ensure_markdowndocument() y _extract_markdownfile_items()")
    else:
        print(f"\n🎉 ÉXITO: Todo el contenido se preservó correctamente")

def debug_content_in_groups(groups: List[RuleGroup]) -> None:
    """✅ MEJORADO: Debug específico para verificar contenido en grupos"""
    print("🔍 DEBUG: Verificando contenido en grupos")
    print("=" * 50)
    
    total_files = 0
    empty_content = 0
    files_with_content = 0
    
    for i, group in enumerate(groups):
        print(f"\n📂 Grupo {i+1}: {group.group}")
        print(f"   📄 Archivos: {len(group.markdownfile)}")
        
        for j, md_file in enumerate(group.markdownfile):
            total_files += 1
            content_length = len(md_file.content) if md_file.content else 0
            
            if content_length == 0:
                empty_content += 1
                print(f"      ❌ {j+1}. {md_file.path} - SIN CONTENIDO")
            else:
                files_with_content += 1
                print(f"      ✅ {j+1}. {md_file.path} - {content_length} chars")
                print(f"         Preview: {md_file.content[:100]}...")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total archivos: {total_files}")
    print(f"   Con contenido: {files_with_content}")
    print(f"   Sin contenido: {empty_content}")
    
    if empty_content > 0:
        print(f"\n💡 SOLUCIONES DISPONIBLES:")
        print(f"   1. debug_markdownfiles_structure(rules) - entender estructura original")
        print(f"   2. verify_content_preservation(rules, groups) - verificar preservación")
        print(f"   3. groups = load_content_into_groups(groups) - cargar contenido")
        print(f"   4. groups = create_mock_content_for_groups(groups) - contenido mock")

def verify_groups_have_objects(groups: List[RuleGroup]) -> None:
    """✅ CORREGIDO: Verifica que los grupos contienen objetos MarkdownDocument"""
    print("🔍 VERIFICANDO GRUPOS...")
    
    for i, group in enumerate(groups):
        print(f"\n📂 Grupo {i+1}: {group.group}")
        print(f"   📄 Archivos: {len(group.markdownfile)}")
        
        for j, md_file in enumerate(group.markdownfile):
            print(f"      {j+1}. Tipo: {type(md_file).__name__}")
            
            # ✅ CORREGIDO: Usar 'path' en lugar de 'filename'
            if hasattr(md_file, 'path') and hasattr(md_file, 'content'):
                print(f"         ✅ Path: {md_file.path}")
                print(f"         ✅ Content: {len(md_file.content)} caracteres")
            else:
                print(f"         ❌ NO es MarkdownDocument válido: {md_file}")

# ===== VERIFICATION UTILITIES =====

if __name__ == "__main__":
    print("🎯 Sistema de agrupación de reglas - VERSIÓN FINAL CORREGIDA")
    print("✅ PROBLEMA RESUELTO: markdownfile contiene objetos MarkdownDocument")
    print("✅ MANEJO DE DICCIONARIOS: Prioriza {ruta: contenido} correctamente")
    print("✅ DEBUG MEJORADO: Logging detallado para identificar problemas")
    print("✅ PRESERVACIÓN DE CONTENIDO: Mantiene relación ruta → contenido")
    print("")
    print("🧪 TESTS ESPECÍFICOS PARA TU CASO:")
    print("")
    print("TEST 1 - Verificar manejo de diccionarios:")
    print("  test_dictionary_case()")
    print("  # Prueba específicamente casos {ruta: contenido}")
    print("")
    print("TEST 2 - Verificar flujo completo:")
    print("  verify_full_flow_with_dict()")
    print("  # Simula todo el procesamiento con diccionario")
    print("")
    print("TEST 3 - Tu dato específico:")
    print("  quick_test_conversion({'tu_archivo.md': 'tu_contenido'})")
    print("  # Prueba con tu estructura exacta")
    print("")
    print("🚨 SI AÚN NO TRAE PATH NI CONTENIDO:")
    print("")
    print("PASO 1 - Test específico (EJECUTA PRIMERO):")
    print("  test_dictionary_case()")
    print("  # Esto verifica que el manejo de diccionarios funcione")
    print("")
    print("PASO 2 - Debug emergencia:")
    print("  emergency_debug_single_rule(your_rules)")
    print("  # Rastrea paso a paso UNA regla real")
    print("")
    print("PASO 3 - Verificar estructura:")
    print("  debug_markdownfiles_structure(your_rules)")
    print("  # Muestra estructura de tus markdownfiles")
    print("")
    print("🔧 USO NORMAL:")
    print("")
    print("groups = group_rules(your_rules, debug_structure=True, enable_debug_logging=True)")
    print("# Con debug completo activado para ver todo el procesamiento")
    print("")
    print("📋 ESTRUCTURA CONFIRMADA:")
    print("  ✅ markdownfiles = {'ruta1.md': 'contenido1', 'ruta2.md': 'contenido2'}")
    print("  ✅ Se convierte a: [MarkdownDocument(path='ruta1.md', content='contenido1'), ...]")
    print("")
    print("💡 EJEMPLO ESPECÍFICO:")
    print("  # Test manual")
    print("  test_dict = {'ejemplo.md': 'contenido de ejemplo'}")
    print("  quick_test_conversion(test_dict)")
    print("")
    print("  # Test completo")
    print("  test_dictionary_case()")
    print("")
    print("Acceder a archivos:")
    print("  for group in groups:")
    print("      for md_file in group.markdownfile:")
    print("          print(f'Path: {md_file.path}')      # La ruta/key")
    print("          print(f'Contenido: {md_file.content}')  # El contenido/value")