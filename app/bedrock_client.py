import os
import json
import logging
import boto3
import codecs
from typing import Optional


# Configuración global de logging si aún no está definida
logger = logging.getLogger()
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


class SingletonMeta(type):
    """
    Metaclase Singleton que asegura que solo exista una instancia de la clase.
    Es útil especialmente en AWS Lambda, donde se reutiliza el runtime entre invocaciones.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BedrockClient(metaclass=SingletonMeta):
    """
    Cliente para Amazon Bedrock optimizado para uso en entornos locales o AWS Lambda.
    
    Soporta la invocación del modelo Claude (u otros) mediante `boto3`, y puede utilizar
    credenciales explícitas si se ejecuta en modo local.

    Atributos:
        model_id (str): ID del modelo Bedrock (por ejemplo, 'anthropic.claude-v2').
        environment (str): 'local' o 'lambda'. Controla cómo se configuran las credenciales.
    """

    def __init__(self, model_id: str, environment: str = "lambda"):
        """
        Inicializa el cliente Bedrock.

        Args:
            model_id (str): Identificador del modelo a utilizar (ej. 'anthropic.claude-v2').
            environment (str): Entorno de ejecución, 'local' o 'lambda'.

        Raises:
            ValueError: Si el entorno es inválido.
            EnvironmentError: Si faltan variables de entorno necesarias en modo local.
        """
        if hasattr(self, "client"):
            return  # Ya inicializado (por patrón Singleton)

        self.model_id = model_id
        self.environment = environment.lower()

        if self.environment not in ("lambda", "local"):
            raise ValueError("El parámetro 'environment' debe ser 'lambda' o 'local'.")

        if self.environment == "local":
            self._configure_local_environment()

        self.region = os.environ.get("AWS_DEFAULT_REGION")
        if not self.region:
            raise EnvironmentError("La variable 'AWS_DEFAULT_REGION' no está definida.")

        # Recomendación: usar boto3.session.Session para mayor control
        session = boto3.session.Session()
        self.client = session.client("bedrock-runtime", region_name=self.region)

        logger.info(f"BedrockClient inicializado en entorno '{self.environment}' con modelo '{self.model_id}'.")

    def _configure_local_environment(self):
        """
        Valida y carga las variables de entorno necesarias para ejecución local.
        Requiere que estén definidas:
            - AWS_ACCESS_KEY_ID
            - AWS_SECRET_ACCESS_KEY
            - AWS_DEFAULT_REGION

        Raises:
            EnvironmentError: Si alguna variable falta.
        """
        required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]
        for var in required_vars:
            if not os.environ.get(var):
                raise EnvironmentError(f"La variable de entorno '{var}' es requerida para ejecución local.")
        logger.info("Credenciales AWS cargadas correctamente desde entorno local.")

    def _build_payload(self, prompt: str, temperature: float, max_tokens: int) -> dict:
        """
        Construye el payload para enviar al modelo.

        Args:
            prompt (str): Instrucción o texto base.
            temperature (float): Nivel de creatividad del modelo (0.0-1.0).
            max_tokens (int): Máximo número de tokens de salida.

        Returns:
            dict: Estructura lista para serializar y enviar a Bedrock.
        """

        messages = [{"role": "user", "content": prompt}]
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,  # Límite de seguridad
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.9
        }
    def _format_prompt(self, raw_prompt: str) -> str:
        """
        Formatea el prompt según el modelo configurado.
        Actualmente, los modelos Claude requieren que el prompt comience con 'Human:'.
    
        Args:
            raw_prompt (str): Texto base sin formato.
    
        Returns:
            str: Prompt con estructura adecuada para el modelo.
        """
        if self.model_id.startswith("anthropic"):
            return f"\n\nHuman: {raw_prompt}\n\nAssistant:"
        return raw_prompt

    def generate_report(self, prompt: str, temperature: float = 0.7, max_tokens: int = 12000) -> Optional[str]:
        """
        Envía un prompt al modelo configurado en Bedrock y retorna la respuesta generada.

        Args:
            prompt (str): Texto de entrada que define la estructura del informe.
            temperature (float): Grado de variabilidad creativa. (por defecto: 0.7).
            max_tokens (int): Límite de tokens a generar (por defecto: 2048).

        Returns:
            Optional[str]: Texto generado por el modelo, o None si ocurre un error.

        Example:
            >>> client = BedrockClient(model_id="anthropic.claude-v2", environment="local")
            >>> client.generate_report("Genera un informe técnico agrupado por errores y advertencias")
        """
        try:
            body = self._build_payload(prompt, temperature, max_tokens)
            logger.debug("Payload enviado a Bedrock: %s", body)

            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )

            # Decodificación eficiente del stream de respuesta
            response_body = json.load(codecs.getreader("utf-8")(response["body"]))
            output = response_body.get("content")[0].get("text")

            logger.info("Informe generado exitosamente desde Bedrock.")
            return output

        except Exception as e:
            logger.error("Error al generar informe desde Bedrock: %s", e, exc_info=True)
            return None


def run_bedrock_prompt(prompt: str) -> Optional[str]:
    """
    Método de conveniencia para ejecutar un prompt en Bedrock sin crear explícitamente el cliente.

    Args:
        prompt (str): Instrucción o contenido a enviar al modelo.

    Returns:
        Optional[str]: Resultado generado por el modelo, o None si ocurre un error.
    """
    # Configura aquí el modelo y entorno por defecto
    DEFAULT_MODEL_ID = os.environ.get("BEDROCK_REPORT_MODEL_ID", "")
    DEFAULT_ENVIRONMENT = os.environ.get("EXECUTION_ENVIRONMENT", "lambda")  # usa env si está definida

    try:
        client = BedrockClient(
            model_id=DEFAULT_MODEL_ID,
            environment=DEFAULT_ENVIRONMENT
        )

        base_prompt = f"""
        ### OBJETIVO
        Procesar reportes dinámicos generados por IA para producir un reporte final limpio que refleje el estado definitivo de cada regla, considerando todas las correcciones realizadas durante el análisis.

        ---

        ## ALGORITMO DE PROCESAMIENTO

        ### PASO 1: EXTRACCIÓN DE REGLAS
        ```
        Para cada regla encontrada en el texto:
        1. Extraer número de regla (formato: X.Y donde X e Y son dígitos)
        2. Identificar TODAS las menciones de esa regla en el texto
        3. Registrar estado inicial y cualquier estado posterior
        4. Documentar evidencias, razones de incumplimiento y ubicaciones
        ```

        ### PASO 2: DETECCIÓN DE CORRECCIONES
        Identificar patrones de corrección por orden de prioridad:

        **PATRONES DE ALTA PRIORIDAD (Corrección Explícita):**
        - Texto contiene frases: "Tras revisar", "SÍ SE CUMPLE", "CORREGIDO", "Corrección del Análisis"
        - Títulos que incluyen: "CORREGIDO", "Corrección", "ACTUALIZACIÓN"  
        - Frases de rectificación: "En realidad sí cumple", "Error en evaluación inicial"

        **PATRONES DE MEDIA PRIORIDAD (Cambio de Estado):**
        - Misma regla evaluada múltiples veces: primera aparición ❌ → aparición posterior ✅
        - Misma regla evaluada múltiples veces: primera aparición ✅ → aparición posterior ❌
        - Evidencia positiva (múltiples ✅) pero conclusión inicial ❌

        **PATRONES DE BAJA PRIORIDAD (Inconsistencias):**
        - Múltiples evaluaciones de misma regla con resultados contradictorios
        - Cambios en conteos numéricos sin explicación clara
        - Información duplicada con diferentes conclusiones

        ### PASO 3: RESOLUCIÓN DE ESTADO FINAL
        ```
        Para cada regla identificada:
            if existe_correccion_explicita:
                estado_final = estado_después_de_corrección_explícita
            elif existe_cambio_de_estado_documentado:
                estado_final = último_estado_encontrado_cronológicamente
            elif hay_contradicción_evidencia_vs_conclusión:
                estado_final = estado_que_coincida_con_evidencia_concreta
            else:
                estado_final = primera_evaluación_encontrada
        ```

        ### PASO 4: CONSTRUCCIÓN DE SALIDA
        ```
        REGLAS_CUMPLIDAS = [lista de números de regla que cumplen]
        REGLAS_INCUMPLIDAS = [lista de objetos con detalles completos de incumplimiento]

        Para cada regla procesada:
            if estado_final == CUMPLE:
                agregar solo número a REGLAS_CUMPLIDAS
            else:
                agregar objeto completo a REGLAS_INCUMPLIDAS con:
                    - número de regla
                    - descripción de la regla
                    - razón específica del incumplimiento
                    - evidencia concreta encontrada
                    - ubicación donde se detectó el problema
        ```

        ---

        ## FORMATO DE SALIDA OBLIGATORIO

        ```markdown
        # Reporte General

        ## Resumen de Cumplimiento
        ✅ **Reglas cumplidas:** {{{{cantidad_total}}}} - [{{{{números_ordenados_ascendentemente}}}}]
        ❌ **Reglas incumplidas:** {{{{cantidad_total}}}} - [{{{{números_ordenados_ascendentemente}}}}]

        ## Detalle de Incumplimientos

        ### Regla {{{{número}}}}: {{{{descripción_completa_de_la_regla}}}}
        **Razón del incumplimiento:** {{{{explicación_específica_del_problema}}}}
        **Evidencia específica:** {{{{detalles_concretos_encontrados}}}}
        **Ubicación:** {{{{dónde_se_encontró_el_problema}}}}

        {{{{REPETIR_PARA_CADA_REGLA_INCUMPLIDA}}}}

        ---

        ## REGLAS DE PROCESAMIENTO OBLIGATORIAS

        ### CUMPLIMIENTO ESTRICTO:
        1. **Título exacto:** Usar "Reporte General" sin modificaciones
        2. **Ordenamiento numérico:** Ordenar reglas por número ascendente (1.1, 1.2, 1.4, 1.7, etc.)
        3. **Conservación de información:** NO inventar datos no presentes en el texto original
        4. **Inclusión completa:** Incluir TODAS las reglas identificadas sin pérdidas
        5. **Detalle diferenciado:**
        - Reglas cumplidas: número + descripción breve
        - Reglas incumplidas: detalles completos obligatorios
        6. **Consistencia numérica:** Verificar que suma de cumplidas + incumplidas = total

        ### VALIDACIONES AUTOMÁTICAS:
        - Confirmar que no se pierdan reglas durante el procesamiento
        - Verificar que el estado final sea consistente con la evidencia disponible
        - Asegurar que todos los campos obligatorios estén completos para reglas incumplidas

        ---

        ## CASOS ESPECIALES Y EXCEPCIONES

        **Regla aparece múltiples veces sin corrección explícita:**
        - Acción: Usar la última evaluación encontrada en orden cronológico

        **Contradicción sin resolución clara:**
        - Acción: Priorizar evidencia concreta y tangible sobre conclusiones subjetivas

        **Información insuficiente para determinar estado:**
        - Acción: Clasificar como incumplida y documentar la falta de información

        **Texto con errores o datos inconsistentes:**
        - Acción: Procesar con la información disponible, NO inventar datos faltantes

        **Reglas mencionadas pero no evaluadas:**
        - Acción: Excluir del reporte final, procesar solo reglas con evaluación

        ---

        ## TEXTO A PROCESAR:
        {prompt}

        ---"""

    
        return client.generate_report(base_prompt)
    
    except Exception as e:
        logger.error(f"Error ejecutando prompt directo: {e}", exc_info=True)
        return None
