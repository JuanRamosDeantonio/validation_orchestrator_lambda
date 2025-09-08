OBJETIVO



Analizar el reporte dinámico generado por IA y producir una versión limpia que refleje el estado final de cada regla, considerando todas las correcciones realizadas.



DETECCIÓN DE AUTOCORRECCIONES (IGNORAR ICONOS DECORATIVOS)



**VALIDACIÓN CONTEXTUAL OBLIGATORIA:**

Antes de procesar cualquier indicador, verificar el CONTEXTO:



FORMATOS CON MARKDOWN son CORRECCIONES VÁLIDAS SI:

- Van precedidos de palabras de corrección: "Tras revisar...", "Inicialmente...", "Error en análisis..."

- Hay contradicción clara con evaluación previa en la misma sección

- Aparecen después de reconocimiento de error


FORMATOS CON MARKDOWN NO son correcciones SI:

- Son la única conclusión al final sin contexto de cambio

- No hay palabras de corrección precedentes

- Son análisis independientes sin referencia a evaluación previa



Indicadores Textuales de Corrección PRIORITARIOS:

- Frases explícitas de cambio: "SÍ SE CUMPLE", "CORREGIDO", "CUMPLIMIENTO CONFIRMADO"

- Revisiones: "Tras revisar...", "revisión más detallada", "Corrección del Análisis"

- Estados finales: "Estado: CUMPLE", "Estado: CUMPLIDA", "Estado: ✅ CUMPLE"

- Reconocimiento de error: "En realidad sí cumple", "Error en evaluación inicial"

- Títulos con "CORREGIDO" o similar



CRÍTICO: Detectar contradicciones entre resumen y detalle:

- Regla listada como "incumplida" en resumen PERO descrita como cumplida en el detalle

- Especial atención a reglas con formato "R[número]" (ej: R1.1, R1.5, R4.5)



Indicadores de Estado Cambiado:

- Misma regla con diferentes estados: Primera vez incumple, luego se marca como que cumple

- Evidencia contradictoria: Evidencia positiva pero la conclusión no concuerda

- Evaluación duplicada: Misma regla evaluada dos veces con resultados diferentes

- Corrección numérica: Números que cambian entre evaluaciones (ej: 5 reglas → 3 reglas)



Patrones de Corrección Específicos:

- Sección que inicia afirmando que se incumple pero termina con que sí cumple

- Explicación inicial de incumplimiento seguida de justificación de cumplimiento

- Cambio en el conteo total de reglas cumplidas/incumplidas



JERARQUÍA DE CORRECCIONES (de mayor a menor prioridad):



1. Corrección explícita con frase directa: "SÍ SE CUMPLE", "CORREGIDO", "Tras revisar", "CUMPLIMIENTO CONFIRMADO"

2. Contradicción directa: Razón de incumplimiento que describe cumplimiento

3. Evaluación duplicada: Última evaluación encontrada tiene precedencia

4. Evidencia contradictoria: Analizar contexto completo



REGLA ESPECIAL - CONTRADICCIÓN RESUMEN VS DETALLE **CON VALIDACIÓN**:



SI una regla aparece en:

- RESUMEN: como "incumplida" 

- DETALLE: con texto que indica cumplimiento ("CUMPLE", "CUMPLIMIENTO CONFIRMADO", "Estado: CUMPLE", etc.)



**ENTONCES VERIFICAR CONTEXTO:**

→ SI hay análisis evaluativo que concluye en cumplimiento: Usar el estado del DETALLE como final

→ SI hay palabras de corrección explícitas: Usar el estado del DETALLE como final  

→ SI es solo formato aislado sin análisis previo: MANTENER estado del RESUMEN

→ Aplicar especialmente a reglas "R[número]" con evidencia de evaluación completa



PROCESO DE LIMPIEZA



1. IDENTIFICAR CORRECCIONES por regla:



- Buscar múltiples evaluaciones de la misma regla en el texto

- Detectar cambios de estado: INCUMPLE a CUMPLE o CUMPLE A INCUMPLE

- Localizar frases de corrección: "Tras revisar...", "SÍ SE CUMPLE", "CORREGIDO", "CUMPLIMIENTO CONFIRMADO"



1.5. VALIDAR CORRECCIÓN REAL:



ANTES de aplicar corrección, verificar que NO sea:

- Explicación detallada sin cambio de estado

- Condicional ("podría cumplir si...")

- Análisis de múltiples escenarios

- Aclaración sin corrección real



1.7. VALIDACIÓN ESPECIAL REGLAS "R":



- Buscar todas las reglas con formato "R[número]" (R1.1, R1.5, R4.5, etc.)

- Verificar si hay contradicción entre su clasificación inicial y contenido del detalle

- Aplicar corrección automáticamente si se detecta contradicción

- Priorizar el contenido del detalle sobre el resumen inicial



2. APLICAR CORRECCIONES:



- SI hay corrección explícita: Usar el estado final corregido (ignorar evaluación inicial)

- SI hay contradicción sin corrección explícita: Usar la última evaluación encontrada

- SI hay evidencia de que se cumple pero conclusión de que no se cumple: Verificar si hay corrección posterior

- SI NO hay corrección: Mantener la evaluación original



3. DETERMINAR ESTADO FINAL:



- Regla CUMPLIDA tras corrección: Solo listar número (sin detalles de incumplimiento)

- Regla INCUMPLIDA tras corrección: Incluir detalles del incumplimiento REAL

- Regla sin cambios: Mantener estado y detalles originales



4. Clasificar resultado final en:



- Reglas cumplidas: Solo número de regla

- Reglas incumplidas: Número + detalle completo del incumplimiento



5. VALIDACIÓN FINAL:



- Verificar que ninguna regla aparezca en ambas listas

- Confirmar que el conteo total sea consistente

- Validar que todas las correcciones detectadas se aplicaron correctamente

- Verificar especialmente que reglas "R[número]" estén en la lista correcta



ESTRUCTURA DE SALIDA



```markdown

# Reporte General



## Resumen de Cumplimiento



**Reglas cumplidas:** [cantidad] - [lista de números]

**Reglas incumplidas:** [cantidad] - [lista de números]



## Detalle de Incumplimientos



[Solo para reglas fallidas, ordenadas numéricamente de menor a mayor]



### Regla X.X: [Descripción]



**Razón del incumplimiento:** [Explicación específica]

**Evidencia específica:** [Detalles concretos]

**Ubicación:** [Dónde se encontró el problema]



## Reglas Cumplidas



[Lista simple sin detalles]

```



RESTRICCIONES CRÍTICAS



- NO inventar información que no existe en el reporte original

- NO perder ninguna regla durante el proceso

- Mantener el título "Reporte General"

- Considerar TODAS las correcciones para determinar el estado final

- Ordenar reglas numéricamente (1.1, 1.2, 1.3, etc.)

- CADA REGLA DEBE APARECER SOLO EN UNA LISTA (cumplidas O incumplidas, nunca en ambas)



EJEMPLOS ESPECÍFICOS DE CORRECCIONES PROBLEMÁTICAS:



Ejemplo 1 - Texto problemático:

```

### Regla R1.5: [descripción]

**Razón del incumplimiento:** Tras revisar más detalladamente, la regla SÍ SE CUMPLE

```

Detección: Frase "SÍ SE CUMPLE" en razón de incumplimiento = CORRECCIÓN EXPLÍCITA

Resultado: Mover R1.5 a "Reglas cumplidas" y ELIMINAR completamente de incumplimientos



Ejemplo 2 - Contradicción resumen vs detalle:

```

Resumen: "Reglas incumplidas: 1 - [R1.1]"

Detalle: "Estado: CUMPLE" o "CUMPLIMIENTO CONFIRMADO"

```

Resultado: R1.1 debe ir a "Reglas cumplidas" (ignorar resumen inicial)



Ejemplo 3 - Evaluación duplicada:

```

Primera evaluación: "Regla 2.4 no cumple porque..."

Segunda evaluación: "Tras revisar, la regla 2.4 SÍ SE CUMPLE"

```

Resultado: Usar la segunda evaluación (corrección explícita)



**Ejemplo 4 - FORMATO DE CONCLUSIÓN (NO ES CORRECCIÓN):**

```

### Regla R1.1: [análisis completo]

- **Estado:** ✅ **CUMPLE**

```

Detección: Es formato de presentación final, NO corrección = MANTENER ESTADO ORIGINAL



RESULTADO ESPERADO



Un reporte limpio que muestre:

- Estado final CORREGIDO de cada regla (considerando TODAS las correcciones)

- Detalles completos solo para reglas que DEFINITIVAMENTE fallan (después de correcciones)

- Lista simple de reglas que cumplen (incluyendo las corregidas de incumplidas a cumplidas)

- Sin mencionar las correcciones en el reporte final (solo el estado definitivo)

- Formato consistente y profesional

- Especial cuidado con reglas formato "R[número]" para evitar pérdidas



TEXTO A PROCESAR:



/n/n# Reporte de Análisis de Directorios

## Resumen de Cumplimiento
✅ **Reglas cumplidas:** 3 - [1.4, 1.9, 1.11]
❌ **Reglas incumplidas:** 3 - [1.7, 1.10, 1.12]

## Detalle de Incumplimientos

### Regla 1.7: En Resource/Config, examinar cada archivo - La extensión debe ser exactamente ".xml"

**Razón del incumplimiento:** El archivo en Resource/Config no tiene la extensión .xml requerida

**Evidencia específica:**
- `addRtnBcSettleAccGMF.json` - tiene extensión .json en lugar de .xml

**Ubicación:** Resource/Config/addRtnBcSettleAccGMF.json

---

### Regla 1.10: En Resource/MQ, examinar cada archivo - La extensión debe ser exactamente ".mq"

**Razón del incumplimiento:** Todos los archivos en Resource/MQ tienen extensión .xml en lugar de .mq

**Evidencia específica:**
- `MQsSrvReturnBalanceSettleAccGMFFcd.xml` - tiene extensión .xml en lugar de .mq
- `ReversesMQSrvReturnBalanceSettleAccGMFFcd.xml` - tiene extensión .xml en lugar de .mq  
- `VerifysMQSrvReturnBalanceSettleAccGMFFcd.xml` - tiene extensión .xml en lugar de .mq

**Ubicación:** Resource/MQ/

---

### Regla 1.12: En Resource/Test, examinar cada archivo - Archivos con "soapui" deben terminar en ".xml"

**Razón del incumplimiento:** El archivo con "soapui" tiene extensión prohibida .xmls en lugar de .xml

**Evidencia específica:**
- `ReturnBalanceSettleAccGMFsoapuiproject.xmls` - contiene "soapui" pero termina en .xmls (extensión prohibida)

**Ubicación:** Resource/Test/ReturnBalanceSettleAccGMFsoapuiproject.xmls

**Reglas incumplidas:** 11 - [4.5, 4.7, 4.10 , 4.12, 4.13, 4.15, 4.16, 6.2, 6.3, 6.4, 6.6]

## Detalle de Incumplimientos

### Regla 4.5: En la sección "Glosario" deben incluirse las definiciones de términos y las rutas correspondientes al repositorio principal y al repositorio de la wiki.
- [ℹ️] No se encontraron archivos fuente para la regla '4.5'.

### Regla 4.7: Debe especificarse el grupo de ejecución donde será desplegado el servicio.
- [ℹ️] No se encontraron archivos fuente para la regla '4.7'.

### Regla 4.10 : Revisar sección "Despliegue de Componente de Configuración en WSRR". En el artefacto XML de configuración del servicio debe verificarse que contenga toda la información requerida (nombres de colas, endpoint, ofuscamiento de campos, etc.) y, en caso de cambios de propiedades, debe incluirse la configuración entre ambientes. Debe haber una tabla con columnas "Ambiente" y "Propiedad" por cada etiqueta "endpoint" que se encuentre en el archivo de configuración .xml, el valor de la etiqueta debe estar en el campo "Desarrollo" de la tabla. En el xml debe existir una etiqueta <serviceListCMP> o <serviceParams> en la cual  se dejan todos los direccionamientos de la aplicación los valores estos valores pueden ser posibles de modificar. Si existe el atributo endpoint para cada endpoint que encuentre en el .xml debera presentar su respectiva tabla con los MPG o WSP correspondiente y el endpoint de Dev que debera ser el mismo que se encuenta en el .xml. Validar que en la ip el .xml presente en vez de la ip los valores {ENDPOINT-INT} para la ip 10.213.130.25 y {ENDPOINT-EXT} para la ip 10.213.81.69
- [ℹ️] No se encontraron archivos fuente para la regla '4.10 '.

### Regla 4.12: Los pasos de reverso deben corresponder exactamente a los pasos de instalación e incluir los respectivos insumos o nombres de los elementos a reversar.
- [ℹ️] No se encontraron archivos fuente para la regla '4.12'.

### Regla 4.13: En el guión de instalación de BUS no deben incluirse configuraciones de DataPower (actualización de conceptos, creación de WSP o MPG), las cuales deben estar en un guión de instalación específico de DataPower.
- [ℹ️] No se encontraron archivos fuente para la regla '4.13'.

### Regla 4.15: Si el servicio requiere configuración de properties, debe detallarse en el guión de instalación. Si se requiere la modificación de un archivo .bar, debe validarse que en la carpeta Resource/Properties exista un archivo .properties. Las configuraciones de properties deben detallarse en el punto "Despliegue de los Componentes de la Solución".
- [ℹ️] No se encontraron archivos fuente para la regla '4.15'.

### Regla 4.16: Para fachadas REST, el guión de instalación debe incluir comandos CORS y listeners HTTPS embebidos, sin habilitar HTTP. Para los servicios REST se debe especificar que tenga siempre esta configuracion la cual se encuentra en el paso Configuración Consumo de Servicios REST
- [ℹ️] No se encontraron archivos fuente para la regla '4.16'.

### Regla 6.2: En el documento de pruebas deben existir 6 escenarios. El código de esatus de los casos exitosos debe ser 0. El código de estatus del error de timeout debe ser 91. El código de estatus del error de conexión debe ser 300. En el error de aplicación en la trama del mensaje de respuesta debe estar presente la representación de la estructura de carpetas de la aplicación: co.com.bancopopular.[nombre de carpeta segun el servicio]
- [ℹ️] No se encontraron archivos fuente para la regla '6.2'.

### Regla 6.3: Las url's de prueba deben coincidir con las url's de las etiquetas endpoint del documento xml de soapui
- [ℹ️] No se encontraron archivos fuente para la regla '6.3'.

### Regla 6.4: Debe incluirse la traza completa de la transacción, generando logs en la tabla de excepciones solo para errores de timeout, conexión y aplicación, pero no para escenarios exitosos ni errores de negocio. En cada uno de los casos el mensaje de respuesta debe estar presente en la trazabilidad y el RqUID debe coincidir.
- [ℹ️] No se encontraron archivos fuente para la regla '6.4'.

### Regla 6.6: Deben especificarse los pasos ejecutados para obtener cada escenario y su respectivo RQUID.
- [ℹ️] No se encontraron archivos fuente para la regla '6.6'.