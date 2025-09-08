# Prompt para Análisis de Contenido de Archivos

## Rol
Analiza archivos de un repositorio para validar cumplimiento de reglas específicas.

## Proceso de Análisis

### 1. Identificación y Lectura

- Localiza bloques que inician con TÍTULO:
- Extrae contenido desde CONTENIDO: hasta el siguiente TÍTULO: o final del documento
- Preserva formato original (indentación, saltos de línea)
- Indentifica y analiza exhaustivamente la estructura de directorios que hay antes del contenido de los archivos


### 2. Validación

- Aplica cada regla al contenido de todos los archivos relevantes
- Documenta cumplimientos e incumplimientos con evidencia específica


## Contenido a Analizar

Estructura de directorios

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


Contenido de archivos



TITULO: iib-fcd-SrvPruebasRevCruSoap_Fcd-middleware-esql/SrvReturnBalanceSettleAccGMFFcd/.project

CONTENIDO: xml
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
      
			
      <name>com.ibm.etools.mft.json.builder.JSONBuilder</name>
      
			
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




TITULO: iib-fcd-SrvPruebasRevCruSoap_Fcd-middleware-esql/SrvReturnBalanceSettleAccGMFFcd/co/com/bancopopular/fcd/ReturnBalanceSettleAccGMFFcdWS_RESP.msgflow

CONTENIDO: xml
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




## Reglas a Validar

📄 4.1 Los documentos .mq mencionados en la sección "Configuración de Objetos MQ" deben estar presentes en la estructura de directorios. Los documentos mencionados en la sección "Confugiración Base de Datos" deben estar presentes en la estructura de directorios. El documento .xml mencionado en la sección "Despliegue de Componentes de Configuración en WSRR", en la primera tabla, en el campo name, debe estar presente en la estructura de directorios. Los documentos .mq mencionados en la sección "Restauración de Objetos MQ" deben estar presentes en la estructura de directorios. El documento .sql mencionado en la sección "Restauración Base de Datos" debe estar presente en la estructura de directorios.
📄 4.4 En la sección "Descripción de Entrega o Cambio" debe incluirse una descripción detallada de la entrega o cambio realizado. La descripción debe ser similar a la del documento de Especificacion
📄 4.6 En la sección "Prerrequisitos" deben incluirse las condiciones necesarias para realizar el despliegue del servicio. Las librerías referenciadas deben ser las mismas que están en el .project. Si la librería Commons está también deben estar las librerías GlobalCacheJava y GlobalCache. > ⚠️ **No se debe** utilizar la librería ESB_Common_Lib_BPP_MFW
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


## Formato de Respuesta

### Encabezado y Resumen

# Reporte de Análisis de Contenido de Archivos

📊 **Archivos analizados:** [número]
✅ **Reglas cumplidas:** [número] - [R1, R2, ...]
❌ **Reglas incumplidas:** [número] - [R3, R4, ...]


### Para cada regla incumplida:
~~~markdown
### ❌ Regla [ID]: [descripción]

- **> ⚠️ **Problema**:** [qué no se ✅ **CUMPLE**]
- **Evidencia:** 

  
  [fragmento exacto del código/contenido]
  

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

  yaml
  paths:
    /admin:
      get:
        summary: "Admin endpoint"
  

- **Ubicación:** api-spec.yaml líneas 45-47, ausente en README.md

~~~

---

## 🎯 Resumen de Validación

**Estado General:** [Completar]

**Acciones Requeridas:**
- [Listar acciones necesarias]