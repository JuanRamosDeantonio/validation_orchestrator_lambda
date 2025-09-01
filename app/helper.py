import os
from typing import Any, List
from app.models import RuleData
import shutil
from pathlib import Path
import re

class RuleIdSorter:
    """Responsabilidad: Ordenamiento de reglas por ID."""
    
    @staticmethod
    def get_sort_key(rule_id: str):
        """Genera clave de ordenamiento: numérica para '1.2.3', alfabética para otros."""
        try:
            return (0, tuple(int(p) for p in rule_id.split(".")))
        except:
            return (1, rule_id.lower())


class RuleFilter:
    """Responsabilidad: Filtrado de reglas."""
    
    @staticmethod
    def get_failed_rules(all_rules: List[RuleData]) -> List[RuleData]:
        """Obtiene solo las reglas que tienen errores."""
        return [rule for rule in all_rules if rule.has_errors()]
    
    @staticmethod
    def get_sorted_failed_rules(all_rules: List[RuleData]) -> List[RuleData]:
        """Obtiene reglas fallidas ordenadas por ID."""
        failed_rules = RuleFilter.get_failed_rules(all_rules)
        failed_rules.sort(key=lambda rule: RuleIdSorter.get_sort_key(rule.id))
        return failed_rules


class MarkdownBuilder:
    """Responsabilidad: Construcción de elementos Markdown."""
    
    @staticmethod
    def build_header(failed_rules: List[RuleData]) -> str:
        """Construye el encabezado del reporte."""
        if not failed_rules:
            return ""
        
        failed_ids = ", ".join(rule.id for rule in failed_rules)
        return f"**Reglas incumplidas:** {len(failed_rules)} - [{failed_ids}]\n\n## Detalle de Incumplimientos\n\n"
    
    @staticmethod
    def build_rule_section(rule: RuleData) -> str:
        """Construye la sección markdown de una regla."""
        title = f"### Regla {rule.id}: {rule.description}"
        
        if rule.has_errors():
            error_bullets = "\n".join(f"- {error}" for error in rule.errors)
            return f"{title}\n{error_bullets}"
        else:
            return f"{title}\n- Sin errores registrados."
    
    @staticmethod
    def join_sections(sections: List[str]) -> str:
        """Une secciones markdown con separador doble."""
        return "\n\n".join(section for section in sections if section.strip())


class RuleViolationReporter:
    """Responsabilidad: Generación de reportes de violaciones."""
    
    def __init__(self):
        self.filter = RuleFilter()
        self.builder = MarkdownBuilder()
    
    def generate_full_report(self, all_rules: List[RuleData]) -> str:
        """Genera reporte completo de todas las reglas con errores."""
        failed_rules = self.filter.get_sorted_failed_rules(all_rules)
        
        if not failed_rules:
            return ""
        
        header = self.builder.build_header(failed_rules)
        sections = [self.builder.build_rule_section(rule) for rule in failed_rules]
        
        return header + self.builder.join_sections(sections)
    
    def generate_single_rule_report(self, rule: RuleData, all_rules: List[RuleData]) -> str:
        """Genera reporte para una regla específica con contexto global."""
        failed_rules = self.filter.get_sorted_failed_rules(all_rules)
        
        if not failed_rules:
            return "No hay reglas con errores registrados."
        
        header = self.builder.build_header(failed_rules)
        rule_section = self.builder.build_rule_section(rule)
        
        return header + rule_section


# API pública - mantiene compatibilidad con código existente
def format_rule_violations_report(all_rules: List[RuleData]) -> str:
    """Genera reporte markdown de todas las reglas con errores."""
    reporter = RuleViolationReporter()
    return reporter.generate_full_report(all_rules)


def format_single_rule_violation_report(rule: RuleData, all_rules: List[RuleData]) -> str:
    """Genera reporte markdown para una regla específica."""
    reporter = RuleViolationReporter()
    return reporter.generate_single_rule_report(rule, all_rules)


def join_sections(*parts: Any, sep: str = None) -> str:
    """Une secciones limpiando vacías."""
    separator = sep or "\n\n"
    cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
    return separator.join(cleaned)


class PromptHandler:
    """Clase simple para gestionar prompts con configuración IS_PRINT"""
    
    def __init__(self, prompts: list, is_print: bool, folder: str = "prompts", use_tmp: bool = False):
        """
        Args:
            prompts: Lista de strings con los prompts
            is_print: Configuración para crear o eliminar archivos
            folder: Nombre de la carpeta
            use_tmp: True para Lambda (/tmp), False para uso local
        """
        self.prompts = prompts
        self.IS_PRINT = is_print  # Configuración por defecto
        self.folder_path = Path("/tmp" if use_tmp else ".") / folder
    
    def handle_prompts(self):
        """Ejecuta la lógica según IS_PRINT"""
        if self.IS_PRINT:
            self._create_files()
        else:
            self._remove_files()
    
    def _create_files(self):
        """Crea carpeta limpia y archivos de prompts"""
        # Limpiar carpeta existente
        if self.folder_path.exists():
            shutil.rmtree(self.folder_path)
        
        # Crear carpeta y archivos
        self.folder_path.mkdir(parents=True, exist_ok=True)
        for i, prompt in enumerate(self.prompts, 1):
            if prompt.strip():
                file_path = self.folder_path / f"prompt_{i:03d}.md"
                file_path.write_text(prompt, encoding='utf-8')
    
    def _remove_files(self):
        """Elimina carpeta y contenido"""
        if self.folder_path.exists():
            shutil.rmtree(self.folder_path)


def printer_prompt(prompts: list[str], is_print: bool):
    """Función corregida para manejar prompts"""
    is_lambda = 'AWS_LAMBDA_FUNCTION_NAME' in os.environ
    handler = PromptHandler(prompts, is_print, use_tmp=is_lambda)  # ← CORREGIDO
    handler.handle_prompts()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TextFilter - Versión final correcta y funcional

Objetivo:
- Conserva: números (0-9), letras (a-z, A-Z), acentos, punto, coma, espacios, saltos de línea
- En archivos: elimina guiones (-) y guiones bajos (_)
- En texto normal: conserva guiones (-), elimina guiones bajos (_)  
- Elimina TODOS los backticks al final

Uso:
    from text_filter import clean_text
    result = clean_text("tu texto aquí")
"""

class TextFilter:
    """Filtro de texto completo y funcional."""
    
    def __init__(self):
        """Inicializa el filtro con patrones optimizados."""
        # Patrón para detectar archivos con cualquier extensión
        self.file_pattern = re.compile(r'\b\w+(?:[-_\u2010\u2013\u2014]+\w+)*\.\w{1,15}\b')
        
        # Caracteres que SIEMPRE se eliminan
        self.forbidden_chars = [
            '@', '#', '$', '%', '&', '*', '(', ')', '[', ']', '{', '}', 
            '|', '\\', '/', ':', ';', '"', "'", '<', '>', '?', '!', '¡', 
            '¿', '=', '+', '^', '~'
        ]
        
        # Patrón de caracteres permitidos (sin backticks)
        self.allowed_pattern = r'[a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜçÇ\.,\- \n]'
        
        # Estadísticas
        self.extensions_found = []
        self.chars_removed = 0
    
    def clean_text(self, text):
        """
        Limpia el texto aplicando todas las reglas.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            str: Texto limpio garantizado
        """
        # Validar entrada
        if not text:
            return ""
        
        if not isinstance(text, str):
            text = str(text)
        
        original_length = len(text)
        
        # PASO 1: Limpiar archivos (eliminar guiones solo de archivos)
        text = self.file_pattern.sub(self._clean_file, text)
        
        # PASO 2: Eliminar caracteres prohibidos específicos (excepto backticks)
        for char in self.forbidden_chars:
            text = text.replace(char, '')
        
        # PASO 3: Aplicar filtro de caracteres permitidos
        allowed_chars = re.findall(self.allowed_pattern, text)
        result = ''.join(allowed_chars)
        
        # PASO 4: Limpiar espacios múltiples y bordes
        result = re.sub(r'  +', ' ', result)
        result = result.strip()
        
        # PASO FINAL: Eliminar TODOS los backticks (la solución más simple y efectiva)
        result = result.replace('`', '')
        
        # Actualizar estadísticas
        self.chars_removed += max(0, original_length - len(result))
        
        return result
    
    def _clean_file(self, match):
        """
        Limpia un archivo eliminando guiones y guiones bajos.
        
        Args:
            match: Match object del archivo detectado
            
        Returns:
            str: Nombre de archivo sin guiones
        """
        filename = match.group(0)
        
        # Registrar extensión para estadísticas
        if '.' in filename:
            ext = filename.split('.')[-1].lower()
            if ext not in self.extensions_found:
                self.extensions_found.append(ext)
        
        # Eliminar TODOS los tipos de guiones del archivo
        clean_filename = re.sub(r'[-_\u2010\u2013\u2014]', '', filename)
        return clean_filename
    
    def get_stats(self):
        """Retorna estadísticas del procesamiento."""
        return {
            'files_processed': len(self.extensions_found),
            'extensions_found': self.extensions_found.copy(),
            'chars_removed': self.chars_removed
        }
    
    def reset_stats(self):
        """Reinicia estadísticas."""
        self.extensions_found = []
        self.chars_removed = 0


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def clean_text(text):
    """
    Función principal - simple y funcional.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        str: Texto limpio SIN backticks
        
    Example:
        result = clean_text("¡Hola! `archivo_test.xml`")
        print(result)  # "Hola archivotest.xml"
    """
    filter_obj = TextFilter()
    return filter_obj.clean_text(text)


def clean_text_with_stats(text):
    """
    Limpia texto y retorna estadísticas.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        tuple: (texto_limpio, estadísticas)
    """
    filter_obj = TextFilter()
    clean_result = filter_obj.clean_text(text)
    stats = filter_obj.get_stats()
    return clean_result, stats


def clean_multiple_texts(texts):
    """
    Limpia múltiples textos de forma eficiente.
    
    Args:
        texts: Lista de textos a limpiar
        
    Returns:
        list: Lista de textos limpios
    """
    if not texts:
        return []
    
    filter_obj = TextFilter()
    return [filter_obj.clean_text(text) for text in texts]


# ============================================================================
# TESTS COMPLETOS
# ============================================================================

def test_basic_functionality():
    """Test de funcionalidad básica."""
    print("TEST FUNCIONALIDAD BÁSICA")
    print("=" * 50)
    
    test_cases = [
        # Casos básicos
        ("Texto simple", "¡Hola mundo!", "Hola mundo"),
        ("Números", "123-456-789", "123-456-789"),  # Conserva guiones en texto
        ("Acentos", "configuración técnica ñoño", "configuración técnica ñoño"),
        
        # Archivos (deben perder guiones)
        ("XML", "`config-file.xml`", "configfile.xml"),
        ("JSON", "`app_config.json`", "appconfig.json"),
        ("Múltiples guiones", "`test-‐-final.md`", "testfinal.md"),
        
        # Símbolos especiales
        ("Símbolos", "test@#$%&*()[]", "test"),
        ("Emojis", "📁 `archivo.txt` 📄", "archivo.txt"),
        
        # Texto normal con guiones (deben conservarse)
        ("Guiones texto", "int-iib-fcd-middleware", "int-iib-fcd-middleware"),
    ]
    
    all_passed = True
    for name, input_text, expected in test_cases:
        result = clean_text(input_text)
        passed = result == expected
        status = "✅" if passed else "❌"
        
        print(f"{status} {name:20}: '{input_text}' → '{result}'")
        if not passed:
            print(f"   Esperado: '{expected}'")
            all_passed = False
    
    print(f"\n{'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")
    return all_passed


def test_backticks_elimination():
    """Test específico para eliminación de backticks."""
    print("\nTEST ELIMINACIÓN DE BACKTICKS")
    print("=" * 50)
    
    backtick_tests = [
        "`simple.xml`",
        "📁 `complex-file_name.json` 🗂️",
        "`addRtnBcSettleAccGMF.xml`",
        "`ReturnBalanceSettleAccGMFsoapuiproject.xml`",
        "texto normal `con.archivo` en el medio",
        "múltiples `file1.txt` y `file2.json` archivos"
    ]
    
    all_clean = True
    for test_input in backtick_tests:
        result = clean_text(test_input)
        has_backticks = '`' in result
        status = "❌" if has_backticks else "✅"
        
        print(f"{status} '{test_input[:30]}...' → '{result}'")
        if has_backticks:
            all_clean = False
    
    print(f"\n{'✅ TODOS LOS BACKTICKS ELIMINADOS' if all_clean else '❌ FALTAN BACKTICKS POR ELIMINAR'}")
    return all_clean


def test_complete_scenario():
    """Test con escenario completo similar al tuyo."""
    print("\nTEST ESCENARIO COMPLETO")
    print("=" * 50)
    
    complete_text = """- 📁 `int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql`
  - 📄 `README.md`
  - 📁 `Resource`
    - 📄 `addRtnBcSettleAccGMF.xml`
    - 📄 `MQ-SrvReturnBalanceSettleAccGMFFcd.mq`
    - 📄 `Reverse_MQ-SrvReturnBalanceSettleAccGMFFcd.mq`
    - 📄 `ReturnBalanceSettleAccGMFsoapuiproject.xml`
  - 📄 `Especificacion-‐-AddReturnBalanceSettleAccGMF.md`"""
    
    result = clean_text(complete_text)
    
    print("RESULTADO:")
    print(result)
    
    # Verificaciones
    has_backticks = '`' in result
    has_emojis = any(emoji in result for emoji in ['📁', '📄'])
    has_file_dashes = any(file in result for file in ['MQ-Srv', 'Reverse_MQ', 'Especificacion-‐-'])
    
    print(f"\n📊 VERIFICACIONES:")
    print(f"❌ Backticks eliminados: {'❌ NO' if has_backticks else '✅ SÍ'}")
    print(f"❌ Emojis eliminados: {'❌ NO' if has_emojis else '✅ SÍ'}")
    print(f"❌ Guiones archivos eliminados: {'❌ NO' if has_file_dashes else '✅ SÍ'}")
    
    # Verificar que se conservan guiones en texto normal
    has_text_dashes = 'int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql' in result
    print(f"✅ Guiones texto conservados: {'✅ SÍ' if has_text_dashes else '❌ NO'}")
    
    success = not has_backticks and not has_emojis and not has_file_dashes and has_text_dashes
    print(f"\n{'✅ ESCENARIO COMPLETO EXITOSO' if success else '❌ HAY PROBLEMAS EN EL ESCENARIO'}")
    
    return success


def run_all_tests():
    """Ejecuta todos los tests."""
    print("🧪 EJECUTANDO TODOS LOS TESTS")
    print("=" * 70)
    
    test1 = test_basic_functionality()
    test2 = test_backticks_elimination()  
    test3 = test_complete_scenario()
    
    all_passed = test1 and test2 and test3
    
    print("\n" + "=" * 70)
    print(f"RESULTADO FINAL: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ HAY PROBLEMAS'}")
    
    if all_passed:
        print("🎉 El código está listo para usar en producción!")
    else:
        print("⚠️  Hay problemas que necesitan ser corregidos.")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()