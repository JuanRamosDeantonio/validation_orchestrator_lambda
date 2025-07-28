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
        return {
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "stop_sequences": ["\n\nHuman:"]
        }

    def generate_report(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
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
            output = response_body.get("completion")

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
        return client.generate_report(prompt)

    except Exception as e:
        logger.error(f"Error ejecutando prompt directo: {e}", exc_info=True)
        return None
