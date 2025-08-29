import os
from typing import Any, List
from app.models import RuleData
import shutil
from pathlib import Path

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