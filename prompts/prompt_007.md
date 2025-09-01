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



TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Resource/Contract/ReturnBalanceSettleAccGMF.wsdl

CONTENIDO: ```text
<?xml version="1.0" encoding="UTF-8"?><wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" name="ReturnBalanceSettleAccGMF" targetNamespace="urn://grupoaval.com/accounts/v1/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <wsdl:types>
    <xsd:schema>
      <xsd:import namespace="urn://grupoaval.com/accounts/v1/"/>
    </xsd:schema>

    <xsd:schema xmlns="http://www.w3.org/2001/XMLSchema" xmlns:aval="urn://grupoaval.com/xsd/ifx/" xmlns:avalv2="urn://grupoaval.com/xsd/ifx/v2/" attributeFormDefault="unqualified" elementFormDefault="unqualified" targetNamespace="urn://grupoaval.com/xsd/ifx/">
      <xsd:import namespace="urn://grupoaval.com/xsd/ifx/v2/"/>
      <xsd:simpleType name="City_Type">
		<xsd:restriction base="xsd:string"/>
	  </xsd:simpleType>
      <xsd:element name="City" type="aval:City_Type"/>
      <xsd:element name="TransactionNumber" type="xsd:string"/>
      <xsd:element name="StatusCode" type="xsd:long"/>
      <xsd:element name="GovOrg" type="aval:OpenEnum_Type"/>
      <xsd:element name="OrgDt" type="xsd:dateTime"/>
      <xsd:element name="AddrType" type="aval:OpenEnum_Type"/>
      <xsd:element name="ExpDt" type="xsd:dateTime"/>
      <xsd:element name="RefId" type="aval:Identifier_Type"/>
      <xsd:element name="ServerStatusDesc" type="xsd:string"/>
      <xsd:element name="Message" type="xsd:string"/>
      <xsd:element name="PhoneNumber" type="xsd:string"/>
      <xsd:element name="StatusDesc" type="xsd:string"/>
      <xsd:element name="RemainRec" type="xsd:boolean"/>
      <xsd:element name="Version" type="xsd:string"/>
      <xsd:element name="BranchName" type="xsd:string"/>
      <xsd:element name="Brand" type="aval:OpenEnum_Type"/>
      <xsd:element name="CurCode" type="xsd:string"/>
      <xsd:element name="Desc" type="xsd:string"/>
      <xsd:element name="Channel" type="xsd:string"/>
      <xsd:element name="StartDt" type="xsd:string"/>
	  <xsd:element name="EffDt" type="xsd:string"/>
      <xsd:element name="ServiceCode" type="xsd:string"/>
      <xsd:element name="GovIssueIdentType" type="aval:OpenEnum_Type"/>
      <xsd:element name="CustLoginId" type="xsd:string"/>
      <xsd:element name="Environment" type="aval:OpenEnum_Type"/>
      <xsd:element name="Name" type="xsd:string"/>
      <xsd:element name="Rate" type="xsd:decimal"/>
      <xsd:element name="CreatedDt" type="xsd:dateTime"/>
      <xsd:element name="Amt" type="xsd:decimal"/>
	  <xsd:element name="AvailableAmt" type="xsd:decimal"/>
	  <xsd:element name="AccountNumber" type="xsd:string"/>
	  <xsd:element name="AccountName" type="xsd:string"/>
      <xsd:element name="CurAmt" type="aval:CurrencyAmount_Type"/>
      <xsd:element name="CurConvertRule" type="aval:OpenEnum_Type"/>
      <xsd:element name="CryptType" type="aval:OpenEnum_Type"/>
      <xsd:element name="EndDt" type="xsd:string"/>
      <xsd:element name="Count" type="xsd:long"/>	  
      <xsd:element name="RqUID" type="aval:UUID_Type"/>
      <xsd:element name="ApprovalId" type="xsd:string"/>	  
      <xsd:element name="ContentType" type="aval:OpenEnum_Type"/>
      <xsd:element name="CurRate" type="xsd:decimal"/>
      <xsd:element name="AcctType" type="aval:OpenEnum_Type"/>
      <xsd:element name="AcctId" type="xsd:string"/>	  
      <xsd:element name="Token" type="aval:Identifier_Type"/>
      <xsd:element name="PaidDt" type="xsd:dateTime"/>
      <xsd:element name="BinLength" type="xsd:long"/>
      <xsd:element name="BalType" type="aval:OpenEnum_Type"/>
      <xsd:element name="ClosedDt" type="xsd:dateTime"/>
      <xsd:element name="IdentType" type="aval:OpenEnum_Type"/>
      <xsd:element name="BranchId" type="xsd:string"/>
      <xsd:element name="Org" type="xsd:string"/>
      <xsd:element name="ClientDt" type="xsd:string"/>
      <xsd:element name="BankId" type="xsd:string"/>
      <xsd:element name="CustPermId" type="xsd:string"/>
      <xsd:element name="Phone" type="xsd:string"/>
      <xsd:element name="IssDt" type="xsd:dateTime"/>
      <xsd:element name="BankIdType" type="aval:OpenEnum_Type"/>
      <xsd:element name="ServerStatusCode" type="xsd:string"/>
      <xsd:element name="OpenDt" type="xsd:dateTime"/>
      <xsd:element name="CityId" type="xsd:string"/>
	  <xsd:element name="CommisionValue" type="xsd:string"/>
	  <xsd:element name="Concept" type="xsd:string"/>
      <xsd:element name="PostedDt" type="xsd:dateTime"/>
      <xsd:element name="UUID" type="aval:UUID_Type"/>

	  <xsd:element name="ClientID" type="xsd:string"/>
	  <xsd:element name="AccountClass" type="xsd:string"/>
	  <xsd:element name="XferId" type="xsd:string"/>
	  <xsd:element name="Category" type="xsd:string"/>

      <xsd:simpleType name="UUID_Type">
		<xsd:restriction base="xsd:string">
		  <xsd:annotation>
			<xsd:documentation>UUID elements are Narrow Character with a maximum length of 36.</xsd:documentation>
		  </xsd:annotation>
		  <xsd:maxLength value="36"/>
		</xsd:restriction>
	  </xsd:simpleType>
      <xsd:element name="OpenEnum" type="aval:OpenEnum_Type"/>
      <xsd:simpleType name="OpenEnum_Type">
		<xsd:restriction base="xsd:string"/>
	  </xsd:simpleType>
      <xsd:complexType name="CurrencyAmount_Type">
		<xsd:sequence>
		  <xsd:element minOccurs="1" ref="aval:Amt"/>
		  <xsd:element minOccurs="0" ref="aval:CurCode"/>
		  <xsd:sequence minOccurs="0">
			<xsd:element minOccurs="0" ref="aval:CurRate"/>
			<xsd:element minOccurs="0" ref="aval:CurConvertRule"/>
		  </xsd:sequence>
		</xsd:sequence>
	  </xsd:complexType>
      <xsd:element name="CurrencyAmount" type="aval:CurrencyAmount_Type"/>
      <xsd:simpleType name="Identifier_Type">
    <xsd:annotation>
      <xsd:documentation>Object identifiers in the IFX Specification are of the
				data type "Identifier." This is a Narrow Character data
				type with a maximum length of 200.</xsd:documentation>
    </xsd:annotation>
    <xsd:restriction base="xsd:string">
      <xsd:maxLength value="200"/>
    </xsd:restriction>
  </xsd:simpleType>
      <xsd:element name="Identifier" type="aval:Identifier_Type"/>
      <xsd:simpleType name="URL_Type">
    <xsd:restriction base="xsd:string">
      <xsd:maxLength value="1024"/>
    </xsd:restriction>
  </xsd:simpleType>
      <xsd:element name="URL" type="aval:URL_Type"/>
      <xsd:element name="Binary" type="aval:Binary_Type"/>
      <xsd:complexType name="Binary_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:ContentType"/>
      <xsd:element ref="aval:BinLength"/>
      <xsd:element ref="aval:BinData"/>
      <xsd:element minOccurs="0" ref="aval:CryptType"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:simpleType name="BinData_Type">
    <xsd:restriction base="xsd:base64Binary"/>
  </xsd:simpleType>
      <xsd:element name="BinData" type="aval:BinData_Type"/>
     <xsd:complexType name="GenericAcctId_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:AcctId"/>
      <xsd:element minOccurs="1" ref="aval:AcctType"/>
      <xsd:element minOccurs="0" ref="aval:BankInfo"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:AcctCur"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="AcctCur" type="aval:AcctCur_Type"/>
      <xsd:simpleType name="AcctCur_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="BankInfo" type="aval:BankInfo_Type"/>
      <xsd:complexType name="BankInfo_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:BankIdType"/>
      <xsd:element ref="aval:BankId"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:RefInfo"/>
      <xsd:element minOccurs="0" ref="aval:Name"/>
      <xsd:element minOccurs="0" ref="aval:BranchId"/>
      <xsd:element minOccurs="0" ref="aval:BranchName"/>
      <xsd:element minOccurs="0" ref="aval:City"/>
      <xsd:element minOccurs="0" ref="aval:StateProv"/>
      <xsd:element minOccurs="0" ref="aval:PostalCode"/>
      <xsd:element minOccurs="0" ref="aval:Country"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="RefInfo" type="aval:RefInfo_Type"/>
      <xsd:complexType name="RefInfo_Type">
    <xsd:sequence>
      <xsd:element ref="aval:RefType"/>
      <xsd:element ref="aval:RefId"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="RefType" type="aval:RefType_Type"/>
      <xsd:simpleType name="RefType_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="PostAddr" type="aval:PostAddr_Type"/>
      <xsd:complexType name="PostAddr_Type">
    <xsd:sequence>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:Addr"/>
      <xsd:element minOccurs="0" ref="aval:CityId"/>
      <xsd:element minOccurs="0" ref="aval:City"/>
      <xsd:element minOccurs="0" ref="aval:StateProv"/>
      <xsd:element minOccurs="0" ref="aval:PostalCode"/>
      <xsd:element minOccurs="0" ref="aval:Country"/>
      <xsd:element minOccurs="0" ref="aval:AddrType"/>
      <xsd:element minOccurs="0" ref="aval:StartDt"/>
      <xsd:element minOccurs="0" ref="aval:EndDt"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:simpleType name="Addr_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="Addr" type="aval:Addr_Type"/>
      <xsd:element name="StateProv" type="aval:StateProv_Type"/>
      <xsd:simpleType name="StateProv_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:simpleType name="PostalCode_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="PostalCode" type="aval:PostalCode_Type"/>
      <xsd:element name="Country" type="aval:Country_Type"/>
      <xsd:simpleType name="Country_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:complexType name="CustName_Type">
    <xsd:sequence>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:LastName"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:FirstName"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:Nickname"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:LegalName"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="CustName" type="aval:CustName_Type"/>
      <xsd:element name="Nickname" type="aval:Nickname_Type"/>
      <xsd:simpleType name="Nickname_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:simpleType name="FirstName_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="FirstName" type="aval:FirstName_Type"/>
      <xsd:simpleType name="LastName_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="LastName" type="aval:LastName_Type"/>
      <xsd:element name="LegalName" type="aval:LegalName_Type"/>
      <xsd:simpleType name="LegalName_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="MsgRsHdr" type="aval:MsgRsHdr_Type"/>
      <xsd:complexType name="MsgRsHdr_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:TxCostAmt"/>
      <xsd:element minOccurs="0" ref="aval:EffDt"/>
      <xsd:element minOccurs="0" ref="aval:RemainRec"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:complexType name="TxCostAmt_Type">
    <xsd:sequence>
      <xsd:element minOccurs="1" ref="aval:CurAmt"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="TxCostAmt" type="aval:TxCostAmt_Type"/>
      <xsd:simpleType name="DateTime_Type">
    <xsd:restriction base="xsd:string">
      <xsd:pattern value="[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2}(\.[0-9]{6})?((-|\+)[0-9]{2}:[0-9]{2})?)?)?"/>
    </xsd:restriction>
  </xsd:simpleType>
      <xsd:element name="DateTime" type="aval:DateTime_Type"/>
      <xsd:simpleType name="GovOrgName_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="GovOrgName" type="aval:GovOrgName_Type"/>
      <xsd:element name="ClientApp" type="aval:ClientApp_Type"/>
      <xsd:complexType name="ClientApp_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:Org"/>
      <xsd:element minOccurs="0" ref="aval:Name"/>
      <xsd:element minOccurs="0" ref="aval:Version"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="IdentSerialNum" type="aval:IdentSerialNum_Type"/>
      <xsd:simpleType name="IdentSerialNum_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:complexType name="CustId_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:CustPermId"/>
      <xsd:element minOccurs="0" ref="aval:CustLoginId"/>
      <xsd:element minOccurs="0" ref="aval:GovIssueIdent"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="aval:CustName"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="CustId" type="aval:CustId_Type"/>
      <xsd:complexType name="GovIssueIdent_Type">
    <xsd:sequence>
      <xsd:element ref="aval:GovIssueIdentType"/>
      <xsd:element ref="aval:IdentSerialNum"/>
      <xsd:element minOccurs="0" ref="aval:GovOrg"/>
      <xsd:element minOccurs="0" ref="aval:GovOrgName"/>
      <xsd:element minOccurs="0" ref="aval:GovRank"/>
      <xsd:element minOccurs="0" ref="aval:StateProv"/>
      <xsd:element minOccurs="0" ref="aval:Country"/>
      <xsd:element minOccurs="0" ref="aval:Desc"/>
      <xsd:element minOccurs="0" ref="aval:IssDt"/>
      <xsd:element minOccurs="0" ref="aval:ExpDt"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:element name="GovIssueIdent" type="aval:GovIssueIdent_Type"/>
      <xsd:element name="GovRank" type="aval:GovRank_Type"/>
      <xsd:simpleType name="GovRank_Type">
    <xsd:restriction base="xsd:string"/>
  </xsd:simpleType>
      <xsd:element name="AdditionalStatus" type="aval:AdditionalStatus_Type"/>
      <xsd:complexType name="AdditionalStatus_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:StatusCode"/>
      <xsd:element minOccurs="0" ref="aval:ServerStatusCode"/>
      <xsd:element minOccurs="0" ref="aval:Severity"/>
      <xsd:element minOccurs="0" ref="aval:StatusDesc"/>
    </xsd:sequence>
  </xsd:complexType>
      <xsd:simpleType name="Severity_Type">
    <xsd:restriction base="xsd:string">
      <xsd:enumeration value="❌ **> ⚠️ **ERROR****"/>
      <xsd:enumeration value="Info"/>
      <xsd:enumeration value="Warn"/>
    </xsd:restriction>
  </xsd:simpleType>
      <xsd:element name="Severity" type="aval:Severity_Type"/>
      <xsd:element name="Status" type="aval:Status_Type"/>
      <xsd:complexType name="Status_Type">
    <xsd:sequence>
      <xsd:element minOccurs="1" ref="aval:StatusCode"/>
      <xsd:element minOccurs="0" ref="aval:ServerStatusCode"/>
      <xsd:element minOccurs="0" ref="aval:Severity"/>
      <xsd:element minOccurs="0" ref="aval:StatusDesc"/>
      <xsd:element minOccurs="0" ref="aval:ServerStatusDesc"/>
      <xsd:element maxOccurs="unbounded" minOccurs="0" ref="aval:AdditionalStatus"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="UserId_Type">
    <xsd:complexContent>
      <xsd:extension base="aval:CustId_Type">
        <xsd:sequence/>
      </xsd:extension>
    </xsd:complexContent>
  </xsd:complexType>
      <xsd:element name="UserId" type="aval:UserId_Type"/>
      <xsd:element name="MsgRqHdr" type="aval:MsgRqHdr_Type"/>
  <xsd:complexType name="MsgRqHdr_Type">
    <xsd:sequence>
      <xsd:element minOccurs="0" ref="aval:ClientApp"/>
      <xsd:element minOccurs="0" ref="avalv2:Channel"/>
      <xsd:element minOccurs="0" ref="aval:BankInfo"/>
      <xsd:element minOccurs="0" ref="avalv2:ClientDt"/>
      <xsd:element minOccurs="0" ref="avalv2:IPAddr"/>
      <xsd:element minOccurs="0" ref="avalv2:SessKey"/>
      <xsd:element minOccurs="0" ref="aval:UserId"/>
      <xsd:element minOccurs="0" ref="avalv2:KeyAcctId"/>
      <xsd:element ref="avalv2:Reverse"/>
      <xsd:element ref="avalv2:Language"/>
      <xsd:element minOccurs="0" ref="avalv2:NextDay"/>
    </xsd:sequence>
  </xsd:complexType>

  <xsd:element name="ProductId" type="aval:ProductId_Type"/>
  <xsd:complexType name="ProductId_Type">
	<xsd:sequence>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="aval:Concept"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="aval:AccountNumber"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="aval:Amt"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="aval:BranchId"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="aval:CommisionValue"/>
	</xsd:sequence>
  </xsd:complexType>
  </xsd:schema>

  <xsd:schema attributeFormDefault="unqualified" elementFormDefault="unqualified" targetNamespace="urn://grupoaval.com/xsd/ifx/v2/">
	  <xsd:element name="Language" type="xsd:string"/>
	  <xsd:element name="IPAddr" type="xsd:string"/>
	  <xsd:element name="ClientDt" type="xsd:dateTime"/>
	  <xsd:element name="Reverse" type="xsd:boolean"/>
	  <xsd:element name="Channel" type="xsd:string"/>
	  <xsd:element name="KeyAcctId" type="xsd:string"/>
	  <xsd:element name="NextDay" type="xsd:dateTime"/>
	  <xsd:element name="SessKey" type="xsd:string"/>
  </xsd:schema>

  <xsd:schema attributeFormDefault="unqualified" elementFormDefault="unqualified" targetNamespace="urn://grupoaval.com/accounts/v1/" xmlns:Q1="urn://grupoaval.com/xsd/ifx/">
      <xsd:import namespace="urn://grupoaval.com/xsd/ifx/"/>
  <xsd:complexType name="addRtnBcSettleAccGMFRequest_Type">
    <xsd:sequence>
      <xsd:element ref="v1:RtnBcSettleAccGMFRq"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="addRtnBcSettleAccGMFResponse_Type">
    <xsd:sequence>
      <xsd:element ref="v1:RtnBcSettleAccGMFRs"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="RtnBcSettleAccRq_Type">
    <xsd:sequence>
      <xsd:element maxOccurs="1" minOccurs="1" ref="Q1:RqUID"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:MsgRqHdr"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:CustId"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:ProductId"/>
    </xsd:sequence>
  </xsd:complexType>
  <xsd:complexType name="RtnBcSettleAccRs_Type">
    <xsd:sequence>
      <xsd:element maxOccurs="1" minOccurs="1" ref="Q1:Status"/>
	  <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:ApprovalId"/>
      <xsd:element maxOccurs="1" minOccurs="1" ref="Q1:RqUID"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:MsgRqHdr"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:MsgRsHdr"/>
      <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:CustId"/>   
	  <xsd:element maxOccurs="1" minOccurs="0" ref="Q1:ProductId"/>	  
	</xsd:sequence>
  </xsd:complexType>
  <xsd:element name="RtnBcSettleAccGMFRq" type="v1:RtnBcSettleAccRq_Type"/>
  <xsd:element name="RtnBcSettleAccGMFRs" type="v1:RtnBcSettleAccRs_Type"/>
  <xsd:element name="addRtnBcSettleAccGMFRequest" type="v1:addRtnBcSettleAccGMFRequest_Type"/>
  <xsd:element name="addRtnBcSettleAccGMFResponse" type="v1:addRtnBcSettleAccGMFResponse_Type"/>
  </xsd:schema>
  </wsdl:types>

  <wsdl:message name="addRtnBcSettleAccGMFRequest">
    <wsdl:part element="v1:addRtnBcSettleAccGMFRequest" name="parameters"/>
  </wsdl:message>
  <wsdl:message name="addRtnBcSettleAccGMFResponse">
    <wsdl:part element="v1:addRtnBcSettleAccGMFResponse" name="parameters"/>
  </wsdl:message>
  <wsdl:portType name="ReturnBalanceSettleAccGMF">
    <wsdl:operation name="AddReturnBalanceSettleAccGMF">
      <wsdl:input message="v1:addRtnBcSettleAccGMFRequest"/>
      <wsdl:output message="v1:addRtnBcSettleAccGMFResponse"/>
    </wsdl:operation>
  </wsdl:portType>
  <wsdl:binding name="ReturnBalanceSettleAccGMF" type="v1:ReturnBalanceSettleAccGMF">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
    <wsdl:operation name="AddReturnBalanceSettleAccGMF">
      <soap:operation soapAction="urn://grupoaval.com/accounts/v1/AddReturnBalanceSettleAccGMF"/>
      <wsdl:input>
        <soap:body use="literal"/>
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal"/>
      </wsdl:output>
    </wsdl:operation>
  </wsdl:binding>
  <wsdl:service name="ReturnBalanceSettleAccGMF">
    <wsdl:port binding="v1:ReturnBalanceSettleAccGMF" name="ReturnBalanceSettleAccGMF">
      <soap:address location="https://brokerbpop:7800/accounts/SSL/ReturnBalanceSettleAccGMF"/>
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>
```
```

## Reglas a Validar
```
📄 1.1 Para cada operación extraída, verifica que existe al menos un archivo .md en las estructuras de directorios que contenga: la palabra "Especificacion", el nombre de la operación (contenido, no necesariamente exacto, y la extensión .md. La correspondencia es flexible: basta con que la operación esté contenida en el nombre del archivo de especificación. No evalues los caracteres extraños en el nombre del archivo de Especificacion, ignoralos. El nombre del documento debe ser "Especificacion" obligatoriamente si hay alguna otra palabra o una variante de la correcta el documento será tomado como errado, no importan los caracteres que estén después del primer termino. La extensión ".md" es obligatoria si el documento tiene otra distinta o que se le parezca será tomado como errado.
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

## 🎯 Resumen de Validación

**Estado General:** [Completar]

**Acciones Requeridas:**
- [Listar acciones necesarias]