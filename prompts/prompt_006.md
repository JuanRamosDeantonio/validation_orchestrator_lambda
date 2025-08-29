# Prompt para Análisis de Contenido de Archivos

## Rol
Analiza archivos de un repositorio para validar cumplimiento de reglas específicas.

## Proceso de Análisis

### 1. Identificación y Lectura

- Localiza bloques que inician con `TÍTULO:`
- Extrae contenido desde `CONTENIDO:` hasta el siguiente `TÍTULO:` o final del documento
- Preserva formato original (indentación, saltos de línea)
- Indentifica y analiza exhaustivamente la estructura de directorios que hay antes del contenido de los archivos


### 2. Validación

- Aplica cada regla al contenido de todos los archivos relevantes
- Documenta cumplimientos e incumplimientos con evidencia específica


## Contenido a Analizar
```
Estructura de directorios

- 📁 `int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql`
  - 📄 `README.md`
  - 📁 `Resource`
    - 📁 `Config`
      - 📄 `addRtnBcSettleAccGMF.xml`
    - 📁 `Contract`
      - 📄 `ReturnBalanceSettleAccGMF.txt`
    - 📁 `MQ`
      - 📄 `MQ-SrvReturnBalanceSettleAccGMFFcd.mq`
      - 📄 `Reverse_MQ-SrvReturnBalanceSettleAccGMFFcd.mq`
      - 📄 `Verify_MQ-SrvReturnBalanceSettleAccGMFFcd.mq`
    - 📁 `Test`
      - 📄 `ReturnBalanceSettleAccGMF-soapui-project.xml`
  - 📁 `SrvReturnBalanceSettleAccGMFFcd`
    - 📄 `.project`
    - 📄 `application.descriptor`
    - 📁 `co`
      - 📁 `com`
        - 📁 `bancopopular`
          - 📁 `fcd`
            - 📄 `ReturnBalanceSettleAccGMFFcdWS_REQ.msgflow`
            - 📄 `ReturnBalanceSettleAccGMFFcdWS_RESP.msgflow`
- 📁 `int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql`
  - 📄 `Especificacion-‐-AddReturnBalanceSettleAccGMF.md`
  - 📄 `Guion.md`
  - 📄 `Home.md`
  - 📄 `Pruebas-‐-AddReturnBalanceSettleAccGMF.md`
  - 📁 `Recursos`
    - 📄 `DiagramaArq.png`


Contenido de archivos



TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Guion.md

CONTENIDO: ```text
﻿# Tabla de Contenido

- [Descripción de Entrega o Cambio](#descripción-de-entrega-o-cambio)
  - [Glosario](#glosario)
  - [Prerrequisitos](#prerrequisitos)
  - [Configuración de Objetos MQ](#configuración-de-objetos-mq)
  - [Configuración Base de Datos](#configuración-base-de-datos)
  - [Despliegue de Componente de Configuración en WSRR](#despliegue-de-componente-de-configuración-en-wsrr)
  - [Despliegue de los Componentes de la Solución](#despliegue-de-los-componentes-de-la-solución)
  - [Configuración Consumo de Servicios **REST**](#configuración-consumo-de-servicios-rest)
- [Descripción de Entrega o Cambio](#descripción-de-entrega-o-cambio)  
  - [Restauración de los Componentes de la Solución](#restauración-de-los-componentes-de-la-solución)
  - [Restauración de Objetos MQ](#restauración-de-objetos-mq)
  - [Restauración Base de Datos](#restauración-base-de-datos)
  - [Restauración de Componente de Configuración en WSRR](#restauración-de-componente-de-configuración-en-wsrr)


## Descripción de Entrega o Cambio

### Guion de montaje para el paso entre ambientes del Banco Popular para el requerimiento que corresponde al servicio de SrvReturnBalanceSettleAccGMFFcd, Devolución de saldo GMF a clientes con cuentas saldadas o por saldar .



## Glosario

NOTA: Para la correcta ejecución de los comandos que hacen parte del guión de montaje y sus anexos, se debe realizar el reemplazo de las siguientes palabras clave con el valor adecuado para cada ambiente:

BROKERNAME: Reemplazar por el nombre de la instancia de IBM Integration Bus creada para el ambiente donde se ejecutarán los comandos.

GRUPOEJECUCION: Reemplazar por el nombre del grupo de ejecución donde se desplegaran las aplicaciones.

WSRRURL: Reemplazar por la URL del ambiente de WSRR donde se realizará el despliegue.

WSRRUSER: Reemplazar por nombre de usuario usado para conectarse a WSRR.

QMNAME: Reemplazar por el nombre el Queue Manager creada para el ambiente donde se ejecutarán los comandos.

DBUSER: Reemplazar por el nombre de usuario usado para conectarse a la base de datos.

FOLDERPATH: Reemplazar por la ruta base donde reposa la documentación, scripts y fuentes ubicada en el directorio de SVN: 

Documentación:

[int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql.wiki](https://github.com/BancoPopular/int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/wiki)

Fuentes:

[int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql](https://github.com/BancoPopular/int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql)


## Prerrequisitos

Para el montaje de los servicios de SrvReturnBalanceSettleAccGMFFcd que cubren los escenarios descritos en el numeral 2. Descripción de entrega o cambio, es necesario tener desplegados previamente los componentes comunes descritos a continuación:

|Componente|Descripción|Ruta del Guion de instalación|Servidor de Integración en el cual desplegar|
| :-: | :-: | :-: | :-: |
|<p>GlobalCacheJava</p><p>GlobalCache</p>|Librerías comunes de la nueva arquitectura| svn://10.200.156.33/REPOSITORIO_SISTEMAS_INTEGRACION/BUS/PROYECTO_CORE/FABRICA/ASSIST/Commons_IBUS10/GlobalCache||
|Commons |Librerías comunes de la nueva arquitectura| svn://10.200.156.33/REPOSITORIO_SISTEMAS_INTEGRACION/BUS/PROYECTO_CORE/FABRICA/ASSIST/Commons_IBUS10/Commons||

- Cada archivo .bar generado se debe configurar con 25 instancias adicionales.
- Para realizar la instalación se debe validar que el directorio donde se requieran colocar los archivos ejecutables, tenga permisos de ejecución del usuario mqsi.
- El componente se debe desplegar en el grupo de ejecución: 



## Configuración de Objetos MQ

Utilizando una herramienta de transferencia de archivos remota (p.e: WinSCP) conectarse al servidor de IIB con el usuario mqsi y copiar los scripts de configuración de objetos MQ: 

MQ-SrvReturnBalanceSettleAccGMFFcd.mq y Verify\_MQ-SrvReturnBalanceSettleAccGMFFcd.mq que se encuentran en el directorio /FOLDERPATH/MQ.

- Utilizando la consolaSSH (Putty) asignar permisos (775) sobre los scripts en el servidor.
- Utilizando la consolaSSH (Putty) ejecutar los siguientes comandos como usuario mqsi:


runmqsc QMNAME  < /FOLDERPATH/MQ-SrvReturnBalanceSettleAccGMFFcd.mq |tee MQ-SrvReturnBalanceSettleAccGMFFcd.log

runmqsc QMNAME  < /FOLDERPATH/Verify\_MQ-SrvReturnBalanceSettleAccGMFFcd.mq |tee MQ\_Verify-SrvReturnBalanceSettleAccGMFFcd.log

- Verificar que los dos scripts no generen errores.
- Descargar los archivos MQ-SrvReturnBalanceSettleAccGMFFcd.log y MQ\_Verify-SrvReturnBalanceSettleAccGMFFcd.log que se generan en el punto 2 como soporte de evidencias del despliegue.


## Configuración Base de Datos

N/A



## Despliegue de Componente de Configuración en WSRR

Ingresar a WSRRURL con WSRRUSER y cargar el documento XML en la opción de Documentos XML en WSRR (véase siguiente figura).

Cargar o realizar upload de los archivos de configuración ubicados en la ruta /FOLDERPATH/Config y completar la información solicitada con los siguientes datos:

|Name| `addRtnBcSettleAccGMF.xml` |
| - | - |
|Description|Devolucion de Saldos GMF|
|Namespace|N/A|
|Version|1\.0|

Antes de realizar el cargue de Archivo(s) de Configuración de cada servicio/operación, se sugiere validar su contenido -Archivos de Configuración ubicados en la ruta especificada en el numeral 2.1 del presente documento- por si se debe ajustar los valores de los parámetros requeridos para el consumo del respectivo servicio específico de acuerdo con el ambiente (QA y Producción). 

para el caso puntual del archivo de configuración `QuerySecureCustomerData.xml` habría que ajustar las propiedades.

|Ambiente|Propiedad|
| - | - |
|MPG o WSP| mpg.iib.to.ast.gmf.lgy.int |
|Desarrollo|https://10.213.130.25:55639|
|QA||
|PRD||

## Despliegue de los Componentes de la Solución

(configuración bar en propiedades que lo requiera)

Utilizando una herramienta de transferencia de archivos remota (Ej, WinSCP) conectarse al servidor de IIB con el usuario mqsi y copiar el archivo de despliegue SrvReturnBalanceSettleAccGMFFcd.bar que se encuentran en el directorio /FOLDERPATH/BAR.

Utilizando la consolaSSH (Putty)  asignar permisos (775) sobre cada archivo de despliegue en el servidor.

Utilizando la consola SSH (Putty) ejecutar los siguientes comandos como usuario mqsi: 

mqsideploy BROKERNAME -e GRUPOEJECUCION -a /FOLDERPATH/SrvReturnBalanceSettleAccGMFFcd.bar -w 200 | tee BAR\_SrvReturnBalanceSettleAccGMFFcd.log

Descargar los archivos BAR\_SrvReturnBalanceSettleAccGMFFcd.log y que se generan como soporte de evidencias.

## Configuración Consumo de Servicios **REST**

La activación del consumo de servicios **REST** en el Broker viene deshabilitada por defecto, es decir, si se despliega una aplicación **REST** en un servidor de integración que no tenga cierta configuración previa, esta toma otros puertos diferentes a los que tiene asignados para los nodos SOAP HTTPS. En este orden, será necesario ejecutar los siguientes comandos para que el servicio **REST** desplegado en cierto servidor de integración tome los mismos puertos utilizados por peticiones SOAP HTTPS. A continuación, los comandos que se deben ejecutar para que la activación del consumo de servicios **REST** quede habilitada:

mqsichangeproperties BROKERNAME -e GRUPOEJECUCION -o ExecutionGroup -n httpNodesUseEmbeddedListener -v true

mqsichangeproperties BROKERNAME -e GRUPOEJECUCION -o HTTPSConnector -n corsEnabled -v true

# DESCRIPCIÓN DEL PROCEDIMIENTO DE REVERSO

## Restauración de los Componentes de la Solución

Utilizando la consola SSH (Putty) ejecutar los siguientes comandos como usuario mqsi: 

mqsideploy BROKERNAME  -e  GRUPOEJECUCION -d SrvReturnBalanceSettleAccGMFFcd.bar -w 200 | tee BAR\_REVERSE\_SrvReturnBalanceSettleAccGMFFcd.log

Descargar los archivos BAR\_REVERSE\_SrvReturnBalanceSettleAccGMFFcd.log que se generan como soporte de evidencia.

## Restauración de Objetos MQ

Utilizando una herramienta de transferencia de archivos remota (Ej, WinSCP) conectarse al servidor de IIB con el usuario mqsi y copiar los scripts de configuración de objetos MQ: Reverse\_MQ-SrvReturnBalanceSettleAccGMFFcd.mq y Verify\_MQ-SrvReturnBalanceSettleAccGMFFcd.mq que se encuentran en el directorio /FOLDERPATH/MQ.

- Utilizando la consolaSSH (Putty) asignar permisos (775) sobre los scripts en el servidor.
- Utilizando la consolaSSH (Putty) ejecutar los siguientes comandos como usuario mqsi:


runmqsc QMNAME  < /FOLDERPATH/Reverse\_SrvReturnBalanceSettleAccGMFFcd.mq |tee Reverse\_MQ-SrvReturnBalanceSettleAccGMFFcd.log

runmqsc QMNAME  < /FOLDERPATH/Verify\_MQ-SrvReturnBalanceSettleAccGMFFcd.mq |tee MQ\_Verify\_Reverse\_SrvReturnBalanceSettleAccGMFFcd.log

- Verificar que los dos scripts no generen errores.
- Descargar los archivos Reverse\_MQ-SrvReturnBalanceSettleAccGMFFcd.log y MQ\_Verify\_SrvReturnBalanceSettleAccGMFFcd.log que se generan en el punto 2 como soporte de evidencias del despliegue.


## Restauración Base de Datos
N/A

## Restauración de Componente de Configuración en WSRR

Ingresar a WSRRURL con WSRRUSER y buscar los documentos XML en la opción de Documentos XML en WSRR.

Eliminar los siguientes archivos de tipo XML y con versión 1.0: `addRtnBcSettleAccGMF.xml`

```
```

## Reglas a Validar
```
📄 4.5 En la sección "Glosario" deben incluirse las definiciones de términos y las rutas correspondientes al repositorio principal y al repositorio de la wiki.
```

## Formato de Respuesta

### Encabezado y Resumen
```
# Reporte de Análisis de Contenido de Archivos

📊 **Archivos analizados:** [número]
✅ **Reglas cumplidas:** [número] - [R1, R2, ...]
❌ **Reglas incumplidas:** [número] - [R3, R4, ...]
```

### Para cada regla incumplida:
~~~markdown
### ❌ Regla [ID]: [descripción]

- **> ⚠️ **Problema**:** [qué no se ✅ **CUMPLE**]
- **Evidencia:** 

  ```
  [fragmento exacto del código/contenido]
  ```

- **Ubicación:** [archivo, sección, líneas]
- **> 💡 **Recomendación**:** [corrección específica]

~~~

## Instrucciones Críticas

- **Secuencia obligatoria**: Ejecutar fases en orden
- **Evidencia textual**: Usar citas exactas del contenido
- **Completitud**: Analizar todos los archivos identificados
- **Precisión**: Basar conclusiones únicamente en el contenido proporcionado


## Casos Especiales

- **Sin archivos**: Reportar "No se identificaron archivos con formato TÍTULO:/CONTENIDO:"
- **Sin reglas**: Reportar "No se proporcionaron reglas de validación"


## Ejemplo
~~~markdown
# Reporte de Análisis de Contenido de Archivos

📊 **Archivos analizados:** 3
✅ **Reglas cumplidas:** 2 - [R1, R3]
❌ **Reglas incumplidas:** 1 - [R2]

### ❌ Regla R2: Todos los endpoints deben tener documentación

- **> ⚠️ **Problema**:** Endpoint "/admin" sin documentación en README
- **Evidencia:** 

  ```yaml
  paths:
    /admin:
      get:
        summary: "Admin endpoint"
  ```

- **Ubicación:** api-`spec.yaml` líneas 45-47, ausente en README.md

~~~

---

## 🚀 Próximos Pasos

1. [Definir próximas acciones]
2. [Establecer fechas límite]
3. [Asignar responsables]