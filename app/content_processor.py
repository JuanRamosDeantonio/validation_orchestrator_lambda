"""
content_processor.py - Procesador de contenido con chunking inteligente
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from utils import setup_logger, Config, estimate_tokens, truncate_content
from models import RuleData, ChunkData

# Configurar logging
logger = setup_logger(__name__)

class ChunkingStrategy(Enum):
    """Estrategias de chunking disponibles."""
    BY_SIZE = "by_size"
    BY_MARKDOWN_STRUCTURE = "by_markdown_structure"
    BY_CODE_STRUCTURE = "by_code_structure"
    BY_DOCUMENTATION = "by_documentation"
    BY_RELEVANCE = "by_relevance"
    INTELLIGENT_HYBRID = "intelligent_hybrid"

@dataclass
class ContentAnalysis:
    """Análisis de contenido para determinar estrategia óptima."""
    total_size: int
    file_count: int
    content_types: Dict[str, int] = field(default_factory=dict)
    markdown_sections: int = 0
    code_files: int = 0
    documentation_files: int = 0
    large_files: List[str] = field(default_factory=list)
    recommended_strategy: ChunkingStrategy = ChunkingStrategy.BY_SIZE
    estimated_chunks: int = 1

class ContentProcessor:
    """
    Procesador especializado en chunking inteligente y optimización de contenido.
    
    Implementa múltiples estrategias de chunking para optimizar el envío de contenido
    a modelos de IA, considerando límites de tokens y manteniendo coherencia semántica.
    """
    
    def __init__(self):
        self.chunking_strategies = {
            ChunkingStrategy.BY_SIZE: self._chunk_by_size,
            ChunkingStrategy.BY_MARKDOWN_STRUCTURE: self._chunk_by_markdown_structure,
            ChunkingStrategy.BY_CODE_STRUCTURE: self._chunk_by_code_structure,
            ChunkingStrategy.BY_DOCUMENTATION: self._chunk_by_documentation,
            ChunkingStrategy.BY_RELEVANCE: self._chunk_by_relevance,
            ChunkingStrategy.INTELLIGENT_HYBRID: self._chunk_intelligent_hybrid
        }
        
        self.content_patterns = {
            'markdown_header': re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE),
            'code_function': re.compile(r'^\s*(def|function|class|interface)\s+\w+', re.MULTILINE),
            'code_comment': re.compile(r'^\s*(#|//|\*|"""|\'\'\').*$', re.MULTILINE),
            'documentation_section': re.compile(r'(README|CHANGELOG|CONTRIBUTING|INSTALL|SETUP)', re.IGNORECASE),
            'configuration_file': re.compile(r'\.(json|yaml|yml|toml|ini|conf|config)$', re.IGNORECASE)
        }
        
    def process_content_for_rule(self, rule: RuleData, content: Dict[str, str], 
                                max_tokens: int = None) -> Dict[str, Any]:
        """
        Procesa contenido específicamente para una regla, aplicando la estrategia óptima.
        
        Args:
            rule: Regla que determina el procesamiento
            content: Contenido de archivos a procesar
            max_tokens: Límite máximo de tokens (usa Config.MAX_CHUNK_SIZE si no se especifica)
            
        Returns:
            dict: Contenido procesado con chunks y metadata
        """
        if max_tokens is None:
            max_tokens = Config.MAX_CHUNK_SIZE
            
        try:
            logger.info(f"Procesando contenido para regla {rule.id} ({rule.type})")
            
            # Analizar contenido para determinar estrategia
            analysis = self._analyze_content(content, rule)
            
            # Determinar si necesita chunking
            if analysis.total_size <= max_tokens * 4:  # Convertir tokens a caracteres aprox.
                logger.debug(f"Contenido pequeño para regla {rule.id}, no requiere chunking")
                return self._create_single_content_response(content, analysis)
            
            # Aplicar chunking con estrategia óptima
            logger.info(f"Aplicando chunking con estrategia: {analysis.recommended_strategy.value}")
            chunks = self._apply_chunking_strategy(content, rule, analysis, max_tokens)
            
            # Validar y optimizar chunks
            optimized_chunks = self._optimize_chunks(chunks, max_tokens)
            
            logger.info(f"Chunking completado: {len(optimized_chunks)} chunks generados para regla {rule.id}")
            
            return {
                'requires_chunking': True,
                'chunks': optimized_chunks,
                'analysis': analysis,
                'processing_metadata': {
                    'strategy_used': analysis.recommended_strategy.value,
                    'original_size': analysis.total_size,
                    'chunks_created': len(optimized_chunks),
                    'average_chunk_size': sum(chunk.size_tokens for chunk in optimized_chunks) // len(optimized_chunks) if optimized_chunks else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando contenido para regla {rule.id}: {str(e)}")
            # Fallback: retornar contenido truncado simple
            return self._create_fallback_response(content, max_tokens, str(e))
    
    def _analyze_content(self, content: Dict[str, str], rule: RuleData) -> ContentAnalysis:
        """
        Analiza el contenido para determinar la estrategia de chunking óptima.
        
        Args:
            content: Contenido a analizar
            rule: Regla que influye en el análisis
            
        Returns:
            ContentAnalysis: Análisis completo del contenido
        """
        analysis = ContentAnalysis(
            total_size=sum(len(text) for text in content.values()),
            file_count=len(content)
        )
        
        # Análisis por tipo de archivo
        for file_path, file_content in content.items():
            file_size = len(file_content)
            
            # Clasificar tipo de archivo
            if file_path.endswith('.md'):
                analysis.content_types['markdown'] = analysis.content_types.get('markdown', 0) + 1
                analysis.markdown_sections += len(self.content_patterns['markdown_header'].findall(file_content))
                
                if self.content_patterns['documentation_section'].search(file_path):
                    analysis.documentation_files += 1
                    
            elif any(file_path.endswith(ext) for ext in ['.py', '.js', '.java', '.cpp', '.c', '.ts']):
                analysis.content_types['code'] = analysis.content_types.get('code', 0) + 1
                analysis.code_files += 1
                
            elif self.content_patterns['configuration_file'].search(file_path):
                analysis.content_types['config'] = analysis.content_types.get('config', 0) + 1
                
            else:
                analysis.content_types['other'] = analysis.content_types.get('other', 0) + 1
            
            # Identificar archivos grandes
            if file_size > Config.MAX_CHUNK_SIZE * 2:  # Archivos > 2x el límite de chunk
                analysis.large_files.append(file_path)
        
        # Determinar estrategia recomendada
        analysis.recommended_strategy = self._determine_optimal_strategy(analysis, rule)
        analysis.estimated_chunks = self._estimate_chunk_count(analysis)
        
        logger.debug(f"Análisis de contenido: {analysis.file_count} archivos, "
                    f"{analysis.total_size:,} caracteres, estrategia: {analysis.recommended_strategy.value}")
        
        return analysis
    
    def _determine_optimal_strategy(self, analysis: ContentAnalysis, rule: RuleData) -> ChunkingStrategy:
        """
        Determina la estrategia de chunking óptima basada en el análisis y la regla.
        
        Args:
            analysis: Análisis del contenido
            rule: Regla que influye en la estrategia
            
        Returns:
            ChunkingStrategy: Estrategia recomendada
        """
        rule_description = rule.description.lower()
        
        # Estrategia basada en tipo de regla
        if rule.type.lower() == 'semántica':
            if 'documentación' in rule_description or 'documentation' in rule_description:
                if analysis.documentation_files > 0 or analysis.content_types.get('markdown', 0) > 0:
                    return ChunkingStrategy.BY_DOCUMENTATION
            
            elif 'arquitectura' in rule_description or 'architecture' in rule_description:
                if analysis.code_files > 0:
                    return ChunkingStrategy.BY_CODE_STRUCTURE
            
            elif any(keyword in rule_description for keyword in ['calidad', 'quality', 'buenas prácticas']):
                return ChunkingStrategy.INTELLIGENT_HYBRID
        
        # Estrategia basada en contenido predominante
        dominant_type = max(analysis.content_types.items(), key=lambda x: x[1])[0] if analysis.content_types else 'other'
        
        if dominant_type == 'markdown' and analysis.markdown_sections > 5:
            return ChunkingStrategy.BY_MARKDOWN_STRUCTURE
        elif dominant_type == 'code' and analysis.code_files > 3:
            return ChunkingStrategy.BY_CODE_STRUCTURE
        elif len(analysis.large_files) > 2:
            return ChunkingStrategy.BY_RELEVANCE
        else:
            return ChunkingStrategy.BY_SIZE
    
    def _estimate_chunk_count(self, analysis: ContentAnalysis) -> int:
        """
        Estima cuántos chunks se generarán.
        
        Args:
            analysis: Análisis del contenido
            
        Returns:
            int: Número estimado de chunks
        """
        avg_chunk_size = Config.MAX_CHUNK_SIZE * 4  # Convertir tokens a caracteres
        estimated_chunks = max(1, analysis.total_size // avg_chunk_size)
        
        # Ajustar basado en estrategia
        if analysis.recommended_strategy == ChunkingStrategy.BY_MARKDOWN_STRUCTURE:
            estimated_chunks = max(estimated_chunks, analysis.markdown_sections // 3)
        elif analysis.recommended_strategy == ChunkingStrategy.BY_CODE_STRUCTURE:
            estimated_chunks = max(estimated_chunks, analysis.code_files)
        
        return min(estimated_chunks, Config.MAX_CHUNKS_PER_RULE)
    
    def _apply_chunking_strategy(self, content: Dict[str, str], rule: RuleData, 
                               analysis: ContentAnalysis, max_tokens: int) -> List[ChunkData]:
        """
        Aplica la estrategia de chunking seleccionada.
        
        Args:
            content: Contenido a dividir
            rule: Regla que guía el chunking
            analysis: Análisis del contenido
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Lista de chunks generados
        """
        strategy = analysis.recommended_strategy
        strategy_function = self.chunking_strategies.get(strategy, self._chunk_by_size)
        
        try:
            chunks = strategy_function(content, rule, max_tokens)
            logger.debug(f"Estrategia {strategy.value} generó {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.warning(f"Error en estrategia {strategy.value}: {str(e)}, fallback a chunking por tamaño")
            return self._chunk_by_size(content, rule, max_tokens)
    
    def _chunk_by_size(self, content: Dict[str, str], rule: RuleData, max_tokens: int) -> List[ChunkData]:
        """
        Chunking simple por tamaño de contenido.
        
        Args:
            content: Contenido a dividir
            rule: Regla (no usado en esta estrategia)
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks divididos por tamaño
        """
        chunks = []
        current_chunk_content = []
        current_tokens = 0
        max_chars = max_tokens * 4  # Conversión aproximada tokens->caracteres
        
        for file_path, file_content in content.items():
            file_tokens = estimate_tokens(file_content)
            file_section = f"--- {file_path} ---\n{file_content}"
            
            if current_tokens + file_tokens > max_tokens and current_chunk_content:
                # Crear chunk actual
                chunk_content = "\n\n".join(current_chunk_content)
                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_type="size_based",
                    size_tokens=current_tokens
                ))
                
                # Iniciar nuevo chunk
                current_chunk_content = [file_section]
                current_tokens = file_tokens
            else:
                current_chunk_content.append(file_section)
                current_tokens += file_tokens
        
        # Agregar último chunk
        if current_chunk_content:
            chunk_content = "\n\n".join(current_chunk_content)
            chunks.append(ChunkData(
                content=chunk_content,
                chunk_type="size_based",
                size_tokens=current_tokens
            ))
        
        return chunks
    
    def _chunk_by_markdown_structure(self, content: Dict[str, str], rule: RuleData, 
                                   max_tokens: int) -> List[ChunkData]:
        """
        Chunking basado en estructura de markdown (headers, secciones).
        
        Args:
            content: Contenido a dividir
            rule: Regla que guía el chunking
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks basados en estructura markdown
        """
        chunks = []
        
        for file_path, file_content in content.items():
            if not file_path.endswith('.md'):
                # Archivos no-markdown van a chunks simples
                file_tokens = estimate_tokens(file_content)
                if file_tokens <= max_tokens:
                    chunks.append(ChunkData(
                        content=f"--- {file_path} ---\n{file_content}",
                        chunk_type="non_markdown",
                        size_tokens=file_tokens
                    ))
                continue
            
            # Dividir markdown por secciones
            sections = self._extract_markdown_sections(file_content)
            current_chunk_sections = []
            current_tokens = 0
            
            for section in sections:
                section_tokens = estimate_tokens(section['content'])
                section_text = f"## {section['title']}\n{section['content']}"
                
                if current_tokens + section_tokens > max_tokens and current_chunk_sections:
                    # Crear chunk con secciones actuales
                    chunk_content = f"--- {file_path} ---\n" + "\n\n".join(current_chunk_sections)
                    chunks.append(ChunkData(
                        content=chunk_content,
                        chunk_type="markdown_sections",
                        size_tokens=current_tokens,
                        rule_focus=True
                    ))
                    
                    # Iniciar nuevo chunk
                    current_chunk_sections = [section_text]
                    current_tokens = section_tokens
                else:
                    current_chunk_sections.append(section_text)
                    current_tokens += section_tokens
            
            # Agregar último chunk del archivo
            if current_chunk_sections:
                chunk_content = f"--- {file_path} ---\n" + "\n\n".join(current_chunk_sections)
                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_type="markdown_sections",
                    size_tokens=current_tokens,
                    rule_focus=True
                ))
        
        return chunks
    
    def _chunk_by_code_structure(self, content: Dict[str, str], rule: RuleData, 
                               max_tokens: int) -> List[ChunkData]:
        """
        Chunking basado en estructura de código (funciones, clases).
        
        Args:
            content: Contenido a dividir
            rule: Regla que guía el chunking
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks basados en estructura de código
        """
        chunks = []
        
        for file_path, file_content in content.items():
            if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.java', '.cpp', '.c', '.ts']):
                # Archivos no-código van a chunks simples
                file_tokens = estimate_tokens(file_content)
                if file_tokens <= max_tokens:
                    chunks.append(ChunkData(
                        content=f"--- {file_path} ---\n{file_content}",
                        chunk_type="non_code",
                        size_tokens=file_tokens
                    ))
                continue
            
            # Extraer estructura de código
            code_blocks = self._extract_code_blocks(file_content, file_path)
            
            # Agrupar bloques de código en chunks
            current_chunk_blocks = []
            current_tokens = 0
            
            for block in code_blocks:
                block_tokens = estimate_tokens(block['content'])
                
                if current_tokens + block_tokens > max_tokens and current_chunk_blocks:
                    # Crear chunk con bloques actuales
                    chunk_content = f"--- {file_path} ---\n" + "\n\n".join(
                        [f"// {b['type']}: {b['name']}\n{b['content']}" for b in current_chunk_blocks]
                    )
                    chunks.append(ChunkData(
                        content=chunk_content,
                        chunk_type="code_blocks",
                        size_tokens=current_tokens,
                        rule_focus=True
                    ))
                    
                    # Iniciar nuevo chunk
                    current_chunk_blocks = [block]
                    current_tokens = block_tokens
                else:
                    current_chunk_blocks.append(block)
                    current_tokens += block_tokens
            
            # Agregar último chunk del archivo
            if current_chunk_blocks:
                chunk_content = f"--- {file_path} ---\n" + "\n\n".join(
                    [f"// {b['type']}: {b['name']}\n{b['content']}" for b in current_chunk_blocks]
                )
                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_type="code_blocks",
                    size_tokens=current_tokens,
                    rule_focus=True
                ))
        
        return chunks
    
    def _chunk_by_documentation(self, content: Dict[str, str], rule: RuleData, 
                              max_tokens: int) -> List[ChunkData]:
        """
        Chunking especializado para documentación.
        
        Args:
            content: Contenido a dividir
            rule: Regla de documentación
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks optimizados para documentación
        """
        chunks = []
        
        # Priorizar archivos de documentación
        doc_files = []
        code_files = []
        
        for file_path, file_content in content.items():
            if (file_path.endswith('.md') or 
                self.content_patterns['documentation_section'].search(file_path)):
                doc_files.append((file_path, file_content))
            else:
                code_files.append((file_path, file_content))
        
        # Procesar archivos de documentación primero
        for file_path, file_content in doc_files:
            doc_sections = self._extract_documentation_sections(file_content, rule)
            
            for section in doc_sections:
                if estimate_tokens(section['content']) <= max_tokens:
                    chunks.append(ChunkData(
                        content=f"--- {file_path}: {section['title']} ---\n{section['content']}",
                        chunk_type="documentation_section",
                        size_tokens=estimate_tokens(section['content']),
                        rule_focus=True
                    ))
        
        # Agregar código relevante si hay espacio
        remaining_space = Config.MAX_CHUNKS_PER_RULE - len(chunks)
        if remaining_space > 0 and code_files:
            code_chunks = self._chunk_by_size(dict(code_files), rule, max_tokens)
            chunks.extend(code_chunks[:remaining_space])
        
        return chunks
    
    def _chunk_by_relevance(self, content: Dict[str, str], rule: RuleData, 
                          max_tokens: int) -> List[ChunkData]:
        """
        Chunking basado en relevancia para la regla específica.
        
        Args:
            content: Contenido a dividir
            rule: Regla que determina la relevancia
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks ordenados por relevancia
        """
        # Extraer keywords de la regla
        rule_keywords = self._extract_rule_keywords(rule)
        
        # Puntuar archivos por relevancia
        file_scores = []
        for file_path, file_content in content.items():
            relevance_score = self._calculate_relevance_score(file_content, rule_keywords)
            file_scores.append((relevance_score, file_path, file_content))
        
        # Ordenar por relevancia (mayor score primero)
        file_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Crear chunks priorizando contenido más relevante
        chunks = []
        current_chunk_content = []
        current_tokens = 0
        
        for score, file_path, file_content in file_scores:
            file_tokens = estimate_tokens(file_content)
            file_section = f"--- {file_path} (relevancia: {score:.2f}) ---\n{file_content}"
            
            if current_tokens + file_tokens > max_tokens and current_chunk_content:
                # Crear chunk actual
                chunk_content = "\n\n".join(current_chunk_content)
                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_type="relevance_based",
                    size_tokens=current_tokens,
                    rule_focus=True
                ))
                
                # Iniciar nuevo chunk
                current_chunk_content = [file_section]
                current_tokens = file_tokens
            else:
                current_chunk_content.append(file_section)
                current_tokens += file_tokens
        
        # Agregar último chunk
        if current_chunk_content:
            chunk_content = "\n\n".join(current_chunk_content)
            chunks.append(ChunkData(
                content=chunk_content,
                chunk_type="relevance_based",
                size_tokens=current_tokens,
                rule_focus=True
            ))
        
        return chunks
    
    def _chunk_intelligent_hybrid(self, content: Dict[str, str], rule: RuleData, 
                                max_tokens: int) -> List[ChunkData]:
        """
        Chunking híbrido inteligente que combina múltiples estrategias.
        
        Args:
            content: Contenido a dividir
            rule: Regla que guía el chunking
            max_tokens: Límite de tokens por chunk
            
        Returns:
            list: Chunks optimizados con estrategia híbrida
        """
        chunks = []
        
        # Separar contenido por tipo
        markdown_content = {k: v for k, v in content.items() if k.endswith('.md')}
        code_content = {k: v for k, v in content.items() if any(k.endswith(ext) for ext in ['.py', '.js', '.java'])}
        other_content = {k: v for k, v in content.items() if k not in markdown_content and k not in code_content}
        
        # Aplicar estrategia específica a cada tipo
        if markdown_content:
            md_chunks = self._chunk_by_markdown_structure(markdown_content, rule, max_tokens)
            chunks.extend(md_chunks)
        
        if code_content:
            code_chunks = self._chunk_by_code_structure(code_content, rule, max_tokens)
            chunks.extend(code_chunks)
        
        if other_content:
            other_chunks = self._chunk_by_relevance(other_content, rule, max_tokens)
            chunks.extend(other_chunks)
        
        # Reordenar chunks por relevancia si hay muchos
        if len(chunks) > Config.MAX_CHUNKS_PER_RULE:
            chunks = self._reorder_chunks_by_relevance(chunks, rule)[:Config.MAX_CHUNKS_PER_RULE]
        
        return chunks
    
    def _extract_markdown_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extrae secciones de un documento markdown.
        
        Args:
            content: Contenido markdown
            
        Returns:
            list: Lista de secciones con título y contenido
        """
        sections = []
        lines = content.split('\n')
        current_section = {'title': 'Introducción', 'content': ''}
        
        for line in lines:
            header_match = self.content_patterns['markdown_header'].match(line)
            if header_match:
                # Guardar sección anterior si tiene contenido
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # Iniciar nueva sección
                current_section = {
                    'title': header_match.group(1),
                    'content': ''
                }
            else:
                current_section['content'] += line + '\n'
        
        # Agregar última sección
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_code_blocks(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """
        Extrae bloques de código (funciones, clases) de un archivo.
        
        Args:
            content: Contenido del archivo de código
            file_path: Ruta del archivo para determinar lenguaje
            
        Returns:
            list: Lista de bloques de código
        """
        blocks = []
        lines = content.split('\n')
        current_block = None
        indent_stack = []
        
        for i, line in enumerate(lines):
            # Detectar inicio de función/clase
            func_match = self.content_patterns['code_function'].match(line)
            if func_match:
                # Guardar bloque anterior si existe
                if current_block:
                    blocks.append(current_block)
                
                # Extraer nombre de la función/clase
                name = self._extract_function_name(line)
                block_type = 'class' if 'class' in line else 'function'
                
                current_block = {
                    'type': block_type,
                    'name': name,
                    'content': line + '\n',
                    'start_line': i
                }
                indent_stack = [len(line) - len(line.lstrip())]
            
            elif current_block:
                # Agregar línea al bloque actual
                current_block['content'] += line + '\n'
                
                # Detectar fin de bloque por indentación (para Python)
                if file_path.endswith('.py') and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_stack[0] and i > current_block['start_line'] + 1:
                        blocks.append(current_block)
                        current_block = None
                        indent_stack = []
        
        # Agregar último bloque
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def _extract_function_name(self, line: str) -> str:
        """
        Extrae el nombre de una función de su línea de definición.
        
        Args:
            line: Línea de código con definición de función
            
        Returns:
            str: Nombre de la función
        """
        patterns = [
            r'def\s+(\w+)',  # Python
            r'function\s+(\w+)',  # JavaScript
            r'class\s+(\w+)',  # Clases
            r'interface\s+(\w+)',  # Interfaces
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def _extract_documentation_sections(self, content: str, rule: RuleData) -> List[Dict[str, str]]:
        """
        Extrae secciones relevantes de documentación según la regla.
        
        Args:
            content: Contenido de documentación
            rule: Regla que determina qué extraer
            
        Returns:
            list: Secciones relevantes de documentación
        """
        all_sections = self._extract_markdown_sections(content)
        rule_keywords = self._extract_rule_keywords(rule)
        
        relevant_sections = []
        for section in all_sections:
            # Calcular relevancia de la sección
            relevance = self._calculate_relevance_score(
                section['title'] + ' ' + section['content'], 
                rule_keywords
            )
            
            if relevance > 0.3:  # Umbral de relevancia
                relevant_sections.append(section)
        
        # Si no hay secciones relevantes, incluir las primeras
        if not relevant_sections and all_sections:
            relevant_sections = all_sections[:2]
        
        return relevant_sections
    
    def _extract_rule_keywords(self, rule: RuleData) -> List[str]:
        """
        Extrae palabras clave de una regla para análisis de relevancia.
        
        Args:
            rule: Regla de la cual extraer keywords
            
        Returns:
            list: Lista de keywords relevantes
        """
        text = f"{rule.description} {rule.explanation or ''}"
        
        # Extraer palabras técnicas importantes
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filtrar palabras comunes
        stop_words = {
            'debe', 'tener', 'para', 'con', 'una', 'el', 'la', 'de', 'que', 'en',
            'por', 'se', 'es', 'del', 'las', 'los', 'y', 'o', 'pero', 'como',
            'código', 'archivo', 'función', 'debe', 'ser', 'estar'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return list(set(keywords[:10]))  # Top 10 keywords únicos
    
    def _calculate_relevance_score(self, content: str, keywords: List[str]) -> float:
        """
        Calcula score de relevancia de contenido basado en keywords.
        
        Args:
            content: Contenido a evaluar
            keywords: Keywords de referencia
            
        Returns:
            float: Score de relevancia entre 0 y 1
        """
        if not keywords:
            return 0.5  # Score neutral si no hay keywords
        
        content_lower = content.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword in content_lower:
                matches += 1
        
        return min(matches / len(keywords), 1.0)
    
    def _reorder_chunks_by_relevance(self, chunks: List[ChunkData], rule: RuleData) -> List[ChunkData]:
        """
        Reordena chunks por relevancia para la regla.
        
        Args:
            chunks: Chunks a reordenar
            rule: Regla de referencia
            
        Returns:
            list: Chunks ordenados por relevancia
        """
        keywords = self._extract_rule_keywords(rule)
        
        chunk_scores = []
        for chunk in chunks:
            relevance = self._calculate_relevance_score(chunk.content, keywords)
            chunk_scores.append((relevance, chunk))
        
        # Ordenar por relevancia (mayor primero)
        chunk_scores.sort(reverse=True, key=lambda x: x[0])
        
        return [chunk for score, chunk in chunk_scores]
    
    def _optimize_chunks(self, chunks: List[ChunkData], max_tokens: int) -> List[ChunkData]:
        """
        Optimiza chunks generados para mejorar calidad y eficiencia.
        
        Args:
            chunks: Chunks a optimizar
            max_tokens: Límite de tokens
            
        Returns:
            list: Chunks optimizados
        """
        optimized = []
        
        for chunk in chunks:
            # Verificar tamaño del chunk
            if chunk.size_tokens > max_tokens:
                # Truncar chunk muy grande
                chunk.content = truncate_content(chunk.content, max_tokens)
                chunk.size_tokens = max_tokens
                logger.debug(f"Chunk truncado por exceder límite de tokens")
            
            # Verificar que el chunk tenga contenido útil
            if len(chunk.content.strip()) > 50:  # Mínimo 50 caracteres útiles
                optimized.append(chunk)
            else:
                logger.debug(f"Chunk descartado por ser demasiado pequeño")
        
        return optimized
    
    def _create_single_content_response(self, content: Dict[str, str], 
                                      analysis: ContentAnalysis) -> Dict[str, Any]:
        """
        Crea respuesta para contenido que no requiere chunking.
        
        Args:
            content: Contenido original
            analysis: Análisis del contenido
            
        Returns:
            dict: Respuesta con contenido único
        """
        combined_content = "\n\n".join([
            f"--- {file_path} ---\n{file_content}"
            for file_path, file_content in content.items()
        ])
        
        return {
            'requires_chunking': False,
            'content': combined_content,
            'analysis': analysis,
            'processing_metadata': {
                'strategy_used': 'single_content',
                'original_size': analysis.total_size,
                'chunks_created': 1
            }
        }
    
    def _create_fallback_response(self, content: Dict[str, str], max_tokens: int, 
                                error_msg: str) -> Dict[str, Any]:
        """
        Crea respuesta de fallback en caso de error.
        
        Args:
            content: Contenido original
            max_tokens: Límite de tokens
            error_msg: Mensaje de error
            
        Returns:
            dict: Respuesta de fallback
        """
        logger.warning(f"Creando respuesta de fallback: {error_msg}")
        
        # Truncar contenido simple
        combined_content = "\n\n".join([
            f"--- {file_path} ---\n{file_content}"
            for file_path, file_content in content.items()
        ])
        
        truncated_content = truncate_content(combined_content, max_tokens)
        
        return {
            'requires_chunking': False,
            'content': truncated_content,
            'analysis': ContentAnalysis(
                total_size=len(combined_content),
                file_count=len(content),
                recommended_strategy=ChunkingStrategy.BY_SIZE
            ),
            'processing_metadata': {
                'strategy_used': 'fallback',
                'original_size': len(combined_content),
                'chunks_created': 1,
                'error': error_msg
            }
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del procesamiento de contenido.
        
        Returns:
            dict: Estadísticas de procesamiento
        """
        return {
            'available_strategies': [strategy.value for strategy in ChunkingStrategy],
            'chunking_patterns': {
                'markdown_header': self.content_patterns['markdown_header'].pattern,
                'code_function': self.content_patterns['code_function'].pattern,
                'documentation_section': self.content_patterns['documentation_section'].pattern
            },
            'configuration': {
                'max_chunk_size': Config.MAX_CHUNK_SIZE,
                'max_chunks_per_rule': Config.MAX_CHUNKS_PER_RULE,
                'max_document_size': Config.MAX_DOCUMENT_SIZE
            }
        }