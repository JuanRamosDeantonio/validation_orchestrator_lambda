# Validation Orchestrator Lambda

Lambda function que orquesta la validación de repositorios Git usando múltiples reglas y modelos de IA.

## 🎯 Funcionalidad

- **Input**: `repository_url`, `user_name`, `user_email`
- **Output**: `validation_result` (true/false), `message`
- **Proceso**: Carga reglas, valida usando IA, consolida resultados

## 📁 Estructura del Proyecto

```
validation_orchestrator_lambda/
├── lambda_function.py          # Entry point
├── orchestrator.py             # Coordinador principal
├── rules_processor.py          # Gestión de reglas
├── validation_engine.py        # Motor de validaciones
├── result_processor.py         # Procesamiento de resultados
├── integrations.py             # Clientes S3, Lambda, Bedrock
├── utils.py                    # Utilidades
├── models.py                   # Modelos de datos
├── content_processor.py        # Procesamiento de contenido
├── prompt_factory.py           # Fábrica de prompts
├── model_selector.py           # Selección de modelos IA
└── requirements.txt            # Dependencias
```

## 🚀 Despliegue

### Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Desplegar con SAM:
```bash
cd deployment/
sam build
sam deploy --guided
```

## 🔧 Configuración

### Variables de entorno requeridas:
- `SYNC_RULES_LAMBDA`: Nombre de la lambda de sincronización de reglas
- `GET_REPO_STRUCTURE_LAMBDA`: Nombre de la lambda de estructura de repositorio
- `FILE_READER_LAMBDA`: Nombre de la lambda de lectura de archivos
- `REPORT_LAMBDA`: Nombre de la lambda de reportes
- `S3_BUCKET`: Bucket S3 para almacenamiento
- `BEDROCK_REGION`: Región de AWS Bedrock

### Modelos de IA soportados:
- `claude-3-haiku`: Para validaciones rápidas (estructura, contenido)
- `claude-3-sonnet`: Para validaciones semánticas

## 📊 Flujo de Procesamiento

1. **Carga de reglas** desde sync_rules_lambda
2. **Obtención de contenido** del repositorio
3. **Clasificación de reglas** por tipo y criticidad
4. **Validación paralela** usando modelos de IA optimizados
5. **Consolidación** de resultados según criticidad
6. **Respuesta simple** true/false

## 🎯 Estrategia de Validación

- **Un prompt por regla** para máxima precisión
- **Ejecución paralela** de todas las reglas
- **Chunking inteligente** para documentos grandes
- **Selección automática** de modelo óptimo por regla
- **Consolidación por criticidad** (alta → falla inmediata)

## 💰 Optimización de Costos

- Usar Haiku para reglas estructurales/contenido (6x más barato)
- Usar Sonnet solo para reglas semánticas críticas
- Chunking optimizado por tokens
- Validación escalonada (básicas primero)

## 🔍 Logging

Los logs incluyen:
- Progreso de cada fase de validación
- Errores detallados por regla
- Métricas de performance y costos
- Información de debugging

## 🛡️ Manejo de Errores

- Errores por regla individual no afectan al resto
- Fallback automático a modelos alternativos
- Retry logic para llamadas a servicios externos
- Respuesta graciosa ante fallos del sistema