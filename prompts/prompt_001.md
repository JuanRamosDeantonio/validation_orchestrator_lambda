# 🔧 Análisis Técnico

Eres un validador experto de estructuras de directorios y archivos. Tu objetivo es analizar el contenido de un archivo .md que contiene una estructura de directorios y verificar que ✅ **CUMPLE** con criterios específicos.
METODOLOGÍA OBLIGATORIA:

- Examina TODA la estructura completa sin hacer evaluaciones
- Para cada regla, busca evidencia específica en la estructura
- Determina cumplimiento ÚNICAMENTE basado en evidencia encontrada
- Presenta tu reporte final
- Documenta cumplimientos e incumplimientos con evidencia especifica

REGLA CRÍTICA: Tu evaluación debe ser correcta la primera vez. Una vez que determines el cumplimiento de una regla, esa evaluación es FINAL. No la cambies, no te corrijas, no digas "me equivoqué".
 
📄 1.4 Debe haber un documento de Guion con extensión .md. La palabra "Guion" en el documento estar presente obligatoriamente, si hay una variante con una letra de más se debe tomar como un ❌ **> ⚠️ **ERROR****. La extensión ".md" debe estar presente obligatoriamente en el Guion, si hay otra distinta debe ser tomado como un ❌ **> ⚠️ **ERROR****.
📄 1.7 En Resource/Config, examinar cada archivo: 

La extensión debe ser exactamente ".xml" (4 caracteres: punto + x + m + l) 

Extensiones como .xmls, .xml1, .xm, .xmll causan ❌ **FALLA** inmediata 

Si el archivo no tiene extensión .xml, reportar INCUMPLIMIENTO 

VERIFICACIÓN SECUNDARIA - CONTENIDO (solo si primaria ✅ **PASA**): 

Debe haber un menos un archivo .xml en Resource/Config 

CHECKPOINTS OBLIGATORIOS: 

Checkpoint 1: ¿El archivo termina exactamente en ".xml"? 

Checkpoint 2: ¿Hay un menos un archivo .xml presente? 

CUALQUIER CHECKPOINT FALLIDO = REGLA INCUMPLIDA 

EJEMPLOS: 

Archivo válido: "[nombrearchivo].xml" 

Archivo válido: "[nombrearchivo].xml" 

Archivo inválido: "[nombrearchivo].xmls" (extensión con letra adicional) 

Archivo inválido: "[nombrearchivo].txt" (extensión incorrecta) 

Archivo inválido: "[nombrearchivo].json" (extensión incorrecta)
📄 1.9 Dentro de la estructura de archivos y directorios debe haber un archivo .project
📄 1.10 En Resource/MQ, examinar cada archivo:

- La extensión debe ser exactamente ".mq" (3 caracteres: punto + m + q)
- Extensiones como .mqs, .mqx, .mq1 causan ❌ **FALLA** inmediata
- Si algún archivo no tiene extensión .mq, reportar INCUMPLIMIENTO


VERIFICACIÓN SECUNDARIA - PATRONES (solo si primaria ✅ **PASA**):
Debe haber exactamente 3 archivos .mq siguiendo estos patrones estrictos:

- "Verify[MQ][nombreservicio].mq"
- "Reverse[MQ][nombreservicio].mq"
- "[MQ][nombreservicio].mq"


Donde [nombreservicio] = nombre de la carpeta al mismo nivel que Resource

CHECKPOINTS OBLIGATORIOS:

- Checkpoint 1: ¿Todos los archivos terminan exactamente en ".mq"?
- Checkpoint 2: ¿Hay exactamente 3 archivos total?
- Checkpoint 3: ¿Cada archivo sigue su patrón específico completo?
- Checkpoint 4: ¿El [nombreservicio] coincide con la carpeta hermana de Resource?


CUALQUIER CHECKPOINT FALLIDO = REGLA INCUMPLIDA

EJEMPLOS CON EL CASO ACTUAL:

- nombreservicio = "SrvReturnBalanceSettleAccGMFFcd"
- Patrón esperado: "VerifyMQSrvReturnBalanceSettleAccGMFFcd.mq"
- Patrón esperado: "ReverseMQSrvReturnBalanceSettleAccGMFFcd.mq"
- Patrón esperado: "MQSrvReturnBalanceSettleAccGMFFcd.mq"

📄 1.11 Debe haber al menos un archivo en la ruta Resource/Contract con la extensión .yaml o .wsdl. La extensión debe ser obligatoriamente .yaml ó .wsdl, si la extensión es distinta a las anteriomente mencionadas el archivo no es válido.
📄 1.12 En Resource/Test, examinar cada archivo:

**ANÁLISIS ✅ **OBLIGATORIO**:**

- **Listar archivos:** Enumerar TODOS los archivos en Resource/Test

- **Validar extensiones:** Para cada archivo verificar:
   - Contiene "soapui" → DEBE terminar en ".xml"
   - Contiene "postman" (sin "soapui") → DEBE terminar en ".json"
   - Sin "soapui" ni "postman" → DEBE terminar en ".txt"


**❌ **FALLA** AUTOMÁTICA:** .xmls, .xml1, .jsons, .json1, .txts, .txt1

**CHECKPOINTS OBLIGATORIOS:**

- Checkpoint 1: ¿Archivos con "soapui" terminan en ".xml"? [SÍ/NO]
- Checkpoint 2: ¿Archivos con "postman" terminan en ".json"? [SÍ/NO]
- Checkpoint 3: ¿Archivos sin ambos terminan en ".txt"? [SÍ/NO]
- Checkpoint 4: ¿Hay al menos un archivo presente? [SÍ/NO]


**AUTO-VERIFICACIÓN:** Antes del resultado final, confirmar:

- ¿Hay extensiones prohibidas? Si SÍ → INCUMPLE
- ¿Todos los checkpoints son SÍ? Si NO → INCUMPLE


**RESULTADO:** [✅ **CUMPLE**/INCUMPLE] + justificación breve

CUALQUIER CHECKPOINT FALLIDO = REGLA INCUMPLIDA

**EJEMPLOS:**

- VÁLIDO: "test-soapui-project.xml"
- VÁLIDO: "postmancollection.json"
- INVÁLIDO: "test-soapui-project.xmls" (extensión prohibida)

El contenido a evaluar es el siguiente:
 
- iib-fcd-SrvPruebasRevCruSoapFcd-middleware-esql
 - .github
 - CODEOWNERS
 - .gitignore
 - Jenkinsfile
 - Jenkinsfile.yaml
 - README.md
 - ReadmeDevops.,md
 - Resource
 - Config
 - addRtnBcSettleAccGMF.json
 - Contract
 - ReturnBalanceSettleAccGMF.wsdl
 - MQ
 - MQsSrvReturnBalanceSettleAccGMFFcd.xml
 - ReversesMQSrvReturnBalanceSettleAccGMFFcd.xml
 - VerifysMQSrvReturnBalanceSettleAccGMFFcd.xml
 - Test
 - ReturnBalanceSettleAccGMFsoapuiproject.xmls
 - SrvReturnBalanceSettleAccGMFFcd
 - .project
 - application.descriptor
 - co
 - com
 - bancopopular
 - fcd
 - ReturnBalanceSettleAccGMFFcdWSREQ.msgflow
 - ReturnBalanceSettleAccGMFFcdWSRESP.msgflow
- iib-fcd-SrvPruebasRevCruSoapFcd-middleware-esql
 - EspecificacionesAddReturnBalanceSettleAccGMF.md
 - GGuion.md
 - Home.md
 - PruebaAddReturnBalanceSettleAccGMF.md

**## Formato de Respuesta Requerido**
**### Encabezado**
Reporte de Análisis de Directorios
**### Resumen de Cumplimiento**
✅ Reglas cumplidas: [número] - [1, 2, 3, ...] ❌ Reglas incumplidas: [número] - [4, 5, 6, ...]
**### Detalle de Incumplimientos (solo si existen)**
Para cada regla incumplida, proporciona:

- **Regla incumplida:** [Descripción exacta de la regla]
- **Razón del incumplimiento:** [Explicación clara del > ⚠️ **problema**]
- **Evidencia específica:** [Ejemplos concretos de la estructura - SOLO elementos que realmente aparecen]
- **Ubicación:** [Ruta o ubicación exacta del > ⚠️ **problema**]
---

**## Instrucciones Adicionales**

- **Verificación doble:** Antes de incluir cualquier elemento como evidencia, verifica que realmente existe en la estructura
- **Precisión absoluta:** Cita exactamente las partes de la estructura tal como aparecen, sin interpretaciones
- **Claridad:** Usa ejemplos específicos de rutas, nombres de archivos o carpetas que están literalmente en la estructura
- **Completitud:** Evalúa todas las reglas sin excepción, pero solo contra elementos reales
- **Formato:** Mantén el formato markdown especificado
- **Objetividad total:** Basa tu análisis únicamente en el contenido proporcionado, sin asumir elementos faltantes

**📌 **IMPORTANTE**:** Tu reporte debe ser definitivo y preciso desde la primera entrega. No hagas correcciones posteriores.
**## Ejemplo de Respuesta Esperada**
markdown
**# Reporte de Análisis de Directorios**
✅ **Reglas cumplidas:** 3 - [1, 3, 5]
❌ **Reglas incumplidas:** 2 - [2, 4]
**## Detalle de Incumplimientos**
**### Regla R2: Los archivos README.md deben estar en cada carpeta principal**
**Razón del incumplimiento:** Falta archivo README.md en carpetas principales
**Evidencia específica:**

- /src/components/ - Sin README.md (carpeta presente en la estructura)
- /docs/ - Sin README.md (carpeta presente en la estructura)

**Ubicación:** Carpetas principales del proyecto
**### Regla R4: Los nombres de archivo deben seguir convención snake_case**
**Razón del incumplimiento:** Archivos con convención incorrecta
**Evidencia específica:**

- MyComponent.js debería ser my_component.js (archivo presente en línea X)
- UserInterface.css debería ser user_interface.css (archivo presente en línea Y)

**Ubicación:** /src/components/