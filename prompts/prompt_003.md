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

- int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql
 - README.md
 - Resource
 - Config
 - `addRtnBcSettleAccGMF.xml`
 - Contract
 - ReturnBalanceSettleAccGMF.wsdl
 - MQ
 - MQSrvReturnBalanceSettleAccGMFFcd.mq
 - ReverseMQSrvReturnBalanceSettleAccGMFFcd.mq
 - VerifyMQSrvReturnBalanceSettleAccGMFFcd.mq
 - Test
 - `ReturnBalanceSettleAccGMFsoapuiproject.xml`
 - SrvReturnBalanceSettleAccGMFFcd
 - .project
 - application.descriptor
 - co
 - com
 - bancopopular
 - fcd
 - ReturnBalanceSettleAccGMFFcdWSREQ.msgflow
 - ReturnBalanceSettleAccGMFFcdWSRESP.msgflow
- int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql
 - EspecificacionAddReturnBalanceSettleAccGMF.md
 - Guion.md
 - Home.md
 - PruebasAddReturnBalanceSettleAccGMF.md
 - Recursos
 - DiagramaArq.png


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


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/SrvReturnBalanceSettleAccGMFFcd/.project

CONTENIDO: ```xml
<?xml version="1.0" ?>
<projectDescription>
  
	
  <name>SrvReturnBalanceSettleAccGMFFcd</name>
  
	
  <comment/>
  
	
  <projects>
    
		
    <project>Commons</project>
    
	
  </projects>
  
	
  <buildSpec>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.applib.applibbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.applib.applibresourcevalidator</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.connector.policy.ui.PolicyBuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.applib.mbprojectbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.msg.validation.dfdl.mlibdfdlbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.flow.adapters.adapterbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.flow.sca.scabuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.msg.validation.dfdl.mbprojectresourcesbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.esql.lang.esqllangbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.map.builder.mslmappingbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.flow.msgflowxsltbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.flow.msgflowbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.decision.service.ui.decisionservicerulebuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.pattern.capture.PatternBuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.`mft.json`.builder.JSONBuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.restapi.ui.restApiDefinitionsBuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.msg.validation.dfdl.dfdlqnamevalidator</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.bar.ext.barbuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
		
    <buildCommand>
      
			
      <name>com.ibm.etools.mft.unittest.ui.TestCaseBuilder</name>
      
			
      <arguments>
			</arguments>
      
		
    </buildCommand>
    
	
  </buildSpec>
  
	
  <natures>
    
		
    <nature>com.ibm.etools.msgbroker.tooling.applicationNature</nature>
    
		
    <nature>com.ibm.etools.msgbroker.tooling.messageBrokerProjectNature</nature>
    
	
  </natures>
  

</projectDescription>

```


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Resource/MQ/MQ-SrvReturnBalanceSettleAccGMFFcd.mq

CONTENIDO: ```text
DEFINE QLOCAL ('MQINP.RTNBALANCESETTLEACC.FCD.WS.RESP') +
                BOQNAME('SYSTEM.DEAD.LETTER.QUEUE') +
                BOTHRESH(1) +
				MAXDEPTH(5000) +
                REPLACE
```


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/SrvReturnBalanceSettleAccGMFFcd/co/com/bancopopular/fcd/ReturnBalanceSettleAccGMFFcdWS_RESP.msgflow

CONTENIDO: ```xml
<?xml version="1.0" ?>
<ecore:EPackage xmlns:xmi="http://www.omg.org/XMI" xmlns:ComIbmCompute.msgnode="ComIbmCompute.msgnode" xmlns:ComIbmMQInput.msgnode="ComIbmMQInput.msgnode" xmlns:ComIbmMQOutput.msgnode="ComIbmMQOutput.msgnode" xmlns:ComIbmSOAPReply.msgnode="ComIbmSOAPReply.msgnode" xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore" xmlns:eflow="http://www.ibm.com/wbi/2005/eflow" xmlns:utility="http://www.ibm.com/wbi/2005/eflow_utility" xmi:version="2.0" nsURI="co/com/bancopopular/fcd/ReturnBalanceSettleAccGMFFcdWS_RESP.msgflow" nsPrefix="co_com_bancopopular_fcd_ReturnBalanceSettleAccGMFFcdWS_RESP.msgflow">
  
  
  <eClassifiers xmi:type="eflow:FCMComposite" name="FCMComposite_1">
    
    
    <eSuperTypes href="http://www.ibm.com/wbi/2005/eflow#//FCMBlock"/>
    
    
    <eStructuralFeatures xmi:type="ecore:EAttribute" xmi:id="Property.UDP_Application" name="UDP_Application" lowerBound="1" defaultValueLiteral="SrvReturnBalanceSettleAccGMFFcd">
      
      
      <eType xmi:type="ecore:EDataType" href="http://www.eclipse.org/emf/2002/Ecore#//EString"/>
      
    
    </eStructuralFeatures>
    
    
    <translation xmi:type="utility:TranslatableString" key="ReturnBalanceSettleAccGMFFcdWS_RESP" bundleName="co/com/bancopopular/fcd/ReturnBalanceSettleAccGMFFcdWS_RESP" pluginId="SrvReturnBalanceSettleAccGMFFcd"/>
    
    
    <colorGraphic16 xmi:type="utility:GIFFileGraphic" resourceName="platform:/plugin/SrvReturnBalanceSettleAccGMFFcd/icons/full/obj16/ReturnBalanceSettleAccGMFFcdWS_RESP.gif"/>
    
    
    <colorGraphic32 xmi:type="utility:GIFFileGraphic" resourceName="platform:/plugin/SrvReturnBalanceSettleAccGMFFcd/icons/full/obj30/ReturnBalanceSettleAccGMFFcdWS_RESP.gif"/>
    
    
    <composition>
      
      
      <nodes xmi:type="ComIbmMQInput.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_1" location="136,126" queueName="MQINP.RTNBALANCESETTLEACC.FCD.WS.RESP" messageDomainProperty="XMLNSC" transactionMode="no">
        
        
        <translation xmi:type="utility:ConstantString" string="MQINP.FCD.WS.RESP"/>
        
      
      </nodes>
      
      
      <nodes xmi:type="ComIbmCompute.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_2" location="321,126" computeExpression="esql://routine/common.modules.fcd#Facade_GetReplyIdentifierLog_IFX_WS.Main" computeMode="destinationAndMessage">
        
        
        <translation xmi:type="utility:ConstantString" string="CmpGetReplyIdentifierLog"/>
        
      
      </nodes>
      
      
      <nodes xmi:type="ComIbmMQOutput.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_3" location="392,204" queueName="LOG.REGISTER.REQ" transactionMode="no">
        
        
        <translation xmi:type="utility:ConstantString" string="LOG.REGISTER.REQ"/>
        
      
      </nodes>
      
      
      <nodes xmi:type="ComIbmCompute.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_4" location="298,4" dataSource="AUDITORIA" computeExpression="esql://routine/common.modules.fcd#Facade_GetInfoError_IFX_WS_RESP.Main" computeMode="destinationAndMessage">
        
        
        <translation xmi:type="utility:ConstantString" string="CmpGetInfoError"/>
        
      
      </nodes>
      
      
      <nodes xmi:type="ComIbmSOAPReply.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_5" location="508,127" transactionMode="no">
        
        
        <translation xmi:type="utility:ConstantString" string="SOAP Reply"/>
        
      
      </nodes>
      
      
      <nodes xmi:type="ComIbmMQOutput.msgnode:FCMComposite_1" xmi:id="FCMComposite_1_6" location="467,5" queueName="EXCEPTION.REGISTER.REQ" transactionMode="no">
        
        
        <translation xmi:type="utility:ConstantString" string="EXCEPTION.REGISTER.REQ"/>
        
      
      </nodes>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_1" targetNode="FCMComposite_1_5" sourceNode="FCMComposite_1_4" sourceTerminalName="OutTerminal.out" targetTerminalName="InTerminal.in">
        
        
        <bendPoints>25,47,-172,-75</bendPoints>
        
        
        <bendPoints>171,47,-26,-75</bendPoints>
        
      
      </connections>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_2" targetNode="FCMComposite_1_5" sourceNode="FCMComposite_1_2" sourceTerminalName="OutTerminal.out" targetTerminalName="InTerminal.in"/>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_3" targetNode="FCMComposite_1_2" sourceNode="FCMComposite_1_1" sourceTerminalName="OutTerminal.out" targetTerminalName="InTerminal.in"/>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_4" targetNode="FCMComposite_1_6" sourceNode="FCMComposite_1_4" sourceTerminalName="OutTerminal.out1" targetTerminalName="InTerminal.in"/>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_5" targetNode="FCMComposite_1_3" sourceNode="FCMComposite_1_2" sourceTerminalName="OutTerminal.out1" targetTerminalName="InTerminal.in"/>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_6" targetNode="FCMComposite_1_4" sourceNode="FCMComposite_1_1" sourceTerminalName="OutTerminal.catch" targetTerminalName="InTerminal.in"/>
      
      
      <connections xmi:type="eflow:FCMConnection" xmi:id="FCMConnection_7" targetNode="FCMComposite_1_4" sourceNode="FCMComposite_1_1" sourceTerminalName="OutTerminal.failure" targetTerminalName="InTerminal.in"/>
      
    
    </composition>
    
    
    <propertyOrganizer>
      
      
      <propertyDescriptor groupName="Group.Basic" configurable="true" userDefined="true" describedAttribute="Property.UDP_Application">
        
        
        <propertyName xmi:type="utility:TranslatableString" key="Property.UDP_Application" bundleName="co/com/bancopopular/fcd/ReturnBalanceSettleAccGMFFcdWS_RESP" pluginId="SrvReturnBalanceSettleAccGMFFcd"/>
        
      
      </propertyDescriptor>
      
    
    </propertyOrganizer>
    
    
    <stickyBoard/>
    
  
  </eClassifiers>
  

</ecore:EPackage>

```


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Resource/MQ/Reverse_MQ-SrvReturnBalanceSettleAccGMFFcd.mq

CONTENIDO: ```text
DELETE QLOCAL ('MQINP.RTNBALANCESETTLEACC.FCD.WS.RESP') PURGE
```


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Resource/MQ/Verify_MQ-SrvReturnBalanceSettleAccGMFFcd.mq

CONTENIDO: ```text
DISPLAY QLOCAL ('MQINP.RTNBALANCESETTLEACC.FCD.WS.RESP')
```


TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Resource/Config/`addRtnBcSettleAccGMF.xml`

CONTENIDO: ```xml
<?xml version="1.0" ?>
<srvConfiguration>
  
	
  <service>
    
		
    <type>DYNAMIC.ROUTE</type>
    
		
    <name>AddReturnBalanceSettleAccGMF</name>
    
		
    <serviceStatus>1</serviceStatus>
    
		
    <serviceListCMP>
      
			
      <name>AddReturnBalanceSettleAccGMF</name>
      
			
      <queueName>MQINP.RTNBALANCESETTLEACC.ORCH.REQ</queueName>
      
			
      <precall>
        
				
        <name>SrvReturnBalanceSettleAccGMF</name>
        
				
        <protocol>JMS</protocol>
        
				
        <nameProvider>FLEXCUBE</nameProvider>
        
				
        <queueName>MQINP.RTNBALANCESETTLEACC.FC.REQ</queueName>
        
			
      </precall>
      
			
      <poscall>
        
				
        <name>SrvReturnBalanceSettleAccGMFAST</name>
        
				
        <protocol>WS</protocol>
        
				
        <nameProvider>AST</nameProvider>
        
				
        <queueName>MQINP.RTNBALANCESETTLEACC.AST.REQ</queueName>
        
				
        <baseURL>https://10.213.130.25:55654</baseURL>
        
				
        <timeOut>10</timeOut>
        
			
      </poscall>
      
			
      <callOnlFcRev>
        
				
        <name>SrvReturnBalanceSettleAccGMFRev</name>
        
				
        <protocol>JMS</protocol>
        
				
        <nameProvider>FLEXCUBE</nameProvider>
        
				
        <queueName>MQINP.RTNBALANCESETTLEACCREV.FC.REQ</queueName>
        				
			
      </callOnlFcRev>
      
		
    </serviceListCMP>
    
		
    <notificationEmail>
      
			
      <to>notificacionESB@bancopopular.com.co</to>
      
			
      <cc>notificacionESB@bancopopular.com.co</cc>
      
			
      <subject>Notificacion por ❌ **> ⚠️ **ERROR**** en servicio - operacion AddReturnBalanceSettleAccGMF</subject>
      
			
      <body>❌ **> ⚠️ **ERROR**** en Transaccion de servicio - operacion AddReturnBalanceSettleAccGMF</body>
      
			
      <numPerHours>1</numPerHours>
      
		
    </notificationEmail>
    
		
    <priority>8</priority>
    
		
    <attemps>
      
			
      <maxNum>2</maxNum>
      
			
      <time>1</time>
      
		
    </attemps>
    
		
    <maskMessageAct>1</maskMessageAct>
    
		
    <maskMessage>
      
			
      <log1>
        
				
        <fields>
          
					
          <field>
            
						
            <idService>SrvReturnBalanceSettleAccGMFFcd</idService>
            
						
            <type>XML</type>
            
						
            <path>AccountNumber</path>
            
						
            <method>accountNumber</method>
            
					
          </field>
          
				
        </fields>
        
			
      </log1>
      
			
      <log2>
        
				
        <fields>
          
					
          <field>
            
						
            <idService>SrvReturnBalanceSettleAccGMF|AdapterJMSFC_CORE_REQ</idService>
            
						
            <type>XML</type>
            
						
            <path>TXNACC</path>
            
						
            <method>accountNumber</method>
            
					
          </field>
          
				
        </fields>
        
			
      </log2>
      
			
      <log3>
        
				
        <fields>
          
					
          <field>
            
						
            <idService>SrvReturnBalanceSettleAccGMF|AdapterJMSFC_CORE_RES</idService>
            
						
            <type>XML</type>
            
						
            <path>TXNACC</path>
            
						
            <method>accountNumber</method>
            
					
          </field>
          
				
        </fields>
        
			
      </log3>
      
		
    </maskMessage>
    
	
  </service>
  

</srvConfiguration>

```
```

## Reglas a Validar
```
📄 4.1 Los documentos .mq mencionados en la sección "Configuración de Objetos MQ" deben estar presentes en la estructura de directorios. Los documentos mencionados en la sección "Confugiración Base de Datos" deben estar presentes en la estructura de directorios. El documento .xml mencionado en la sección "Despliegue de Componentes de Configuración en WSRR", en la primera tabla, en el campo name, debe estar presente en la estructura de directorios. Los documentos .mq mencionados en la sección "Restauración de Objetos MQ" deben estar presentes en la estructura de directorios. El documento .sql mencionado en la sección "Restauración Base de Datos" debe estar presente en la estructura de directorios.
📄 4.4 En la sección "Descripción de Entrega o Cambio" debe incluirse una descripción detallada de la entrega o cambio realizado. La descripción debe ser similar a la del documento de Especificacion
📄 4.6 En la sección "Prerrequisitos" deben incluirse las condiciones necesarias para realizar el despliegue del servicio. Las librerías referenciadas deben ser las mismas que están en el .project. Si la librería Commons está también deben estar las librerías GlobalCacheJava y GlobalCache. > ⚠️ **No se debe** utilizar la librería ESB_Common_Lib_BPP_MFW
📄 4.7 Debe especificarse el grupo de ejecución donde será desplegado el servicio.
📄 4.8 En el script deben incluirse los objetos MQ correspondientes y en el paso de MQ deben especificarse los nombres de los scripts respectivos. Se deben validar los nodos ComIbmMQInput en los .msgflow, el valor del atributo quename de estos nodos debe estar presente en los .mq. Se deben validar los nodos COmIbmMQGet en los .msgflow, el valor del atributo quename de estos nodos debe estar presente en los .mq. Se debe validar en los .mq que los nombres de las colas no sean superiores a 48 caracteres cada uno y que la estructura del código de los .mq sea correcta de acuerdo al siguiente esquema:

DEFINE QLOCAL ('nombrecola') +
	BOQNAME('SYSTEM.DEAD.LETTER.QUEUE') +
	BOTHRESH(1) +
	MAXDEPTH(5000) +
	REPLACE
DEFINE QLOCAL ('nombrecola') +
	BOQNAME('SYSTEM.DEAD.LETTER.QUEUE') +
	BOTHRESH(1) +
	MAXDEPTH(5000) +
	REPLACE
DEFINE QLOCAL ('nombrecola') +
	BOQNAME('SYSTEM.DEAD.LETTER.QUEUE') +
	BOTHRESH(1) +
	MAXDEPTH(5000) +
	REPLACE

Verificacion:
DISPLAY QLOCAL ('nombrecola')
DISPLAY QLOCAL ('nombrecola')
DISPLAY QLOCAL ('nombrecola')

Eliminacion:
DELETE QLOCAL ('nombrecola') PURGE
DELETE QLOCAL ('nombrecola') PURGE
DELETE QLOCAL ('nombrecola') PURGE
📄 4.10  Revisar sección "Despliegue de Componente de Configuración en WSRR". En el artefacto XML de configuración del servicio debe verificarse que contenga toda la información requerida (nombres de colas, endpoint, ofuscamiento de campos, etc.) y, en caso de cambios de propiedades, debe incluirse la configuración entre ambientes. Debe haber una tabla con columnas "Ambiente" y "Propiedad" por cada etiqueta "endpoint" que se encuentre en el archivo de configuración .xml, el valor de la etiqueta debe estar en el campo "Desarrollo" de la tabla. En el xml debe existir una etiqueta <serviceListCMP> o <serviceParams> en la cual  se dejan todos los direccionamientos de la aplicación los valores estos valores pueden ser posibles de modificar. Si existe el atributo endpoint para cada endpoint que encuentre en el .xml debera presentar su respectiva tabla con los MPG o WSP correspondiente y el endpoint de Dev que debera ser el mismo que se encuenta en el .xml. Validar que en la ip el .xml presente en vez de la ip los valores {ENDPOINT-INT} para la ip 10.213.130.25 y {ENDPOINT-EXT} para la ip 10.213.81.69
📄 4.12 Los pasos de reverso deben corresponder exactamente a los pasos de instalación e incluir los respectivos insumos o nombres de los elementos a reversar.
📄 4.13 En el guión de instalación de BUS no deben incluirse configuraciones de DataPower (actualización de conceptos, creación de WSP o MPG), las cuales deben estar en un guión de instalación específico de DataPower.
📄 4.15 Si el servicio requiere configuración de properties, debe detallarse en el guión de instalación. Si se requiere la modificación de un archivo .bar, debe validarse que en la carpeta Resource/Properties exista un archivo .properties. Las configuraciones de properties deben detallarse en el punto "Despliegue de los Componentes de la Solución".
📄 4.16 Para fachadas **REST**, el guión de instalación debe incluir comandos CORS y listeners HTTPS embebidos, sin habilitar HTTP. Para los servicios **REST** se debe especificar que tenga siempre esta configuracion la cual se encuentra en el paso Configuración Consumo de Servicios **REST**
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