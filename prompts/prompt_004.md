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



TITULO: int-iib-fcd-SrvReturnBalanceSettleAccGMFFcd-middleware-esql/Pruebas-‐-AddReturnBalanceSettleAccGMF.md

CONTENIDO: ```text
## CP01 - EXITOSO SE

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – Exitoso</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
   &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
      &lt;soapenv:Header/&gt;
      &lt;soapenv:Body&gt;
         &lt;v1:addRtnBcSettleAccGMFRequest&gt;
            &lt;v1:RtnBcSettleAccGMFRq&gt;
            &lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;202504021589640&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
               &lt;ifx:ProductId&gt;
                  &lt;ifx:Concept&gt;SE&lt;/ifx:Concept&gt;
                  &lt;ifx:AccountNumber&gt;500800124811&lt;/ifx:AccountNumber&gt;
                  
                  &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
               &lt;/ifx:ProductId&gt;
            &lt;/v1:RtnBcSettleAccGMFRq&gt;
         &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
      &lt;/soapenv:Body&gt;
   &lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;
               &lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;03&lt;/ifx:StatusCode&gt;
                  &lt;ifx:StatusDesc&gt;GW-SAV-03::La transacción ha finalizado correctamente&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;202504021589640&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2025-04-15T09:48:27.868004-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:MsgRsHdr&gt;
               &lt;ifx:TxCostAmt&gt;
                  &lt;ifx:CurAmt&gt;
                     &lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;
                     &lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;
                  &lt;/ifx:CurAmt&gt;
               &lt;/ifx:TxCostAmt&gt;
               &lt;ifx:EffDt&gt;2025-04-15T09:48:27.868004-05:00&lt;/ifx:EffDt&gt;
               &lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;
            &lt;/ifx:MsgRsHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:CommisionValue&gt;0&lt;/ifx:CommisionValue&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
</details>
</td>
      <td rowspan="2">Funciona</td>
      <td rowspan="2"></td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;202504021589640&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;202504021589640&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;202504021589640&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;202504021589640&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;202504021589640&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc830&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;202504021589640&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;202504021589640&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;202504021589640&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc830&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6251050008751928&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;202504021589640&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;202504021589640&lt;/XREF&gt;&lt;FCCREF&gt;025A2BEO2R004002&lt;/FCCREF&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D86&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D86&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 09:48:27 AM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 09:48:27 AM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCIÓN SALDO GMF DB CLIENTE&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35229801.58&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100337024.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;202504021589640&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc830&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6251050008751928&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;202504021589640&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;202504021589640&lt;/XREF&gt;&lt;FCCREF&gt;025A2BEO2R004002&lt;/FCCREF&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D86&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D86&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 09:48:27 AM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 09:48:27 AM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCIÓN SALDO GMF DB CLIENTE&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35229801.58&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100337024.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;&lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;03&lt;/ifx:StatusCode&gt;&lt;ifx:StatusDesc&gt;GW-SAV-03::La transacción ha finalizado correctamente&lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;202504021589640&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-15T09:48:27.868004-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:MsgRsHdr&gt;&lt;ifx:TxCostAmt&gt;&lt;ifx:CurAmt&gt;&lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;&lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;&lt;/ifx:CurAmt&gt;&lt;/ifx:TxCostAmt&gt;&lt;ifx:EffDt&gt;2025-04-15T09:48:27.868004-05:00&lt;/ifx:EffDt&gt;&lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;&lt;/ifx:MsgRsHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;ifx:ProductId&gt;&lt;ifx:CommisionValue&gt;0&lt;/ifx:CommisionValue&gt;&lt;/ifx:ProductId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP01 - EXITOSO DD

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – Exitoso</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
   &lt;soapenv:Header/&gt;
   &lt;soapenv:Body&gt;
      &lt;v1:addRtnBcSettleAccGMFRequest&gt;
         &lt;v1:RtnBcSettleAccGMFRq&gt;
           &lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;${=java.lang.System.currentTimeMillis()}&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
					&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:Concept&gt;DD&lt;/ifx:Concept&gt;
               &lt;ifx:AccountNumber&gt;500800124811&lt;/ifx:AccountNumber&gt;               
               &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRq&gt;
      &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;
               &lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;01&lt;/ifx:StatusCode&gt;
                  &lt;ifx:StatusDesc&gt;GW-REV-01::La transacción se ha revertido correctamente&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;1743628057674&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2025-04-02T16:07:39.644639-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
</details>
</td>
      <td rowspan="2">No Funciona</td>
      <td rowspan="2"></td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743628057674&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;DD&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746257&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35244970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100352164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746257&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35244970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100352164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;{"body":{"codOficina":"025","idRegistro":"1743628057674","nomOficina":"BPOP","usuario":"79641609B"},"trace":{"branchId":"025","channel":"CNL","ipAddr":"1","reverse":false,"rqUID":"1743628057674","userId":"79641609B","workingDay":"20240308 100000"}} {"ResponseFault":{"faultcode":"env:Server","errorCode":"0x02130008","errorMessage":"404 or , Invalid JSON format Response."}}&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;ReverseTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;ReverseTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746258&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;REVERSE&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;V&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35245970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100353164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-REV-01&lt;/WCODE&gt;&lt;WDESC&gt;La transacción se ha revertido correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746258&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;REVERSE&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;500800124811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;V&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35245970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100353164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-REV-01&lt;/WCODE&gt;&lt;WDESC&gt;La transacción se ha revertido correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;&lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;01&lt;/ifx:StatusCode&gt;&lt;ifx:StatusDesc&gt;GW-REV-01::La transacción se ha revertido correctamente&lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;1743628057674&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-02T16:07:39.644639-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP01 - EXITOSO REVERSO DD

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – Reverso Exitoso</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
   &lt;soapenv:Header/&gt;
   &lt;soapenv:Body&gt;
      &lt;v1:addRtnBcSettleAccGMFRequest&gt;
         &lt;v1:RtnBcSettleAccGMFRq&gt;
           &lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;${=java.lang.System.currentTimeMillis()}&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
					&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:Concept&gt;DD&lt;/ifx:Concept&gt;
               &lt;ifx:AccountNumber&gt;500800124811&lt;/ifx:AccountNumber&gt;               
               &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRq&gt;
      &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;
               &lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;01&lt;/ifx:StatusCode&gt;
                  &lt;ifx:StatusDesc&gt;GW-REV-01::La transacción se ha revertido correctamente&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;1743628057674&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2025-04-02T16:07:39.644639-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
</details>
</td>
      <td rowspan="2">No Funciona</td>
      <td rowspan="2">❌ **FALLA** peticion contra AST y se ejecuta reverso</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743628057674&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:Pr oductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;DD&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746257&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35244970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100352164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743628057674&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc80f&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746257&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:38 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;A&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;ACTAMT&gt;1000&lt;/ACTAMT&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35244970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100352164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-SAV-03&lt;/WCODE&gt;&lt;WDESC&gt;La transacción ha finalizado correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;{"body":{"codOficina":"025","idRegistro":"1743628057674","nomOficina":"BPOP","usuario":"79641609B"},"trace":{"branchId":"025","channel":"CNL","ipAddr":"1","reverse":false,"rqUID":"1743628057674","userId":"79641609B","workingDay":"20240308 100000"}} {"ResponseFault":{"faultcode":"env:Server","errorCode":"0x02130008","errorMessage":"404 or , Invalid JSON format Response."}}&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;ReverseTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;ReverseTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;XREF&gt;1743628057674&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746258&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;REVERSE&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;V&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35245970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100353164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-REV-01&lt;/WCODE&gt;&lt;WDESC&gt;La transacción se ha revertido correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;74362805767439254280&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc60e&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;ReverseTransaction&lt;/OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MUltITRIPID&gt;6250920008746258&lt;/MUltITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;REVERSE&lt;/ACTION&gt;&lt;MSGSTAT&gt;🎉 **SUCCESS**&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743628057674&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;FCCREF&gt;025A2BDO2R002038&lt;/FCCREF&gt;&lt;PRD&gt;A2BD&lt;/PRD&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;TXNBRN&gt;025&lt;/TXNBRN&gt;&lt;TXNACC&gt;500800124811&lt;/TXNACC&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNTRN&gt;D85&lt;/TXNTRN&gt;&lt;OFFSETBRN&gt;025&lt;/OFFSETBRN&gt;&lt;OFFSETACC&gt;110505001&lt;/OFFSETACC&gt;&lt;OFFSETCCY&gt;COP&lt;/OFFSETCCY&gt;&lt;OFFSETAMT&gt;1000&lt;/OFFSETAMT&gt;&lt;OFFSETTRN&gt;D85&lt;/OFFSETTRN&gt;&lt;XRATE&gt;1&lt;/XRATE&gt;&lt;LCYAMT&gt;1000&lt;/LCYAMT&gt;&lt;TXNDATE&gt;2025-03-28&lt;/TXNDATE&gt;&lt;VALDATE&gt;2025-03-28&lt;/VALDATE&gt;&lt;RELCUST&gt;000069946&lt;/RELCUST&gt;&lt;TCYTOTCHGAMT&gt;0&lt;/TCYTOTCHGAMT&gt;&lt;MAKERID&gt;CHNLUSER1&lt;/MAKERID&gt;&lt;MAKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/MAKERSTAMP&gt;&lt;CHECKERID&gt;CHNLUSER1&lt;/CHECKERID&gt;&lt;CHECKERSTAMP&gt;2025-03-28 16:07:39 PM&lt;/CHECKERSTAMP&gt;&lt;RECSTAT&gt;V&lt;/RECSTAT&gt;&lt;AUTHSTAT&gt;A&lt;/AUTHSTAT&gt;&lt;DRACC&gt;TXN&lt;/DRACC&gt;&lt;TXNDRCR&gt;D&lt;/TXNDRCR&gt;&lt;BOOKDATE&gt;2025-03-28&lt;/BOOKDATE&gt;&lt;FT&gt;N&lt;/FT&gt;&lt;LCYTOTCHGAMT&gt;0&lt;/LCYTOTCHGAMT&gt;&lt;DENMCCY1&gt;COP&lt;/DENMCCY1&gt;&lt;DENMAMT1&gt;1000&lt;/DENMAMT1&gt;&lt;DENMAMT2&gt;0&lt;/DENMAMT2&gt;&lt;ACCTITLE1&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE1&gt;&lt;ACCTITLE2&gt;EFECTIVO&lt;/ACCTITLE2&gt;&lt;CUSTNAME&gt;SEBASTIAN&lt;/CUSTNAME&gt;&lt;ACCTITLE23&gt;PAOLO  GUERRERO TIRADO&lt;/ACCTITLE23&gt;&lt;INSTR_TYPE&gt;DEVOLUCION SALDOS GMF EFECTIVO&lt;/INSTR_TYPE&gt;&lt;PRDDESC&gt;SEBASTIAN&lt;/PRDDESC&gt;&lt;CIFNAME&gt;80748977&lt;/CIFNAME&gt;&lt;ACCDESC&gt;PAOLO  GUERRERO TIRADO&lt;/ACCDESC&gt;&lt;ACCLASS&gt;582&lt;/ACCLASS&gt;&lt;ACYAVLBAL&gt;35245970.14&lt;/ACYAVLBAL&gt;&lt;ACYTOTBAL&gt;100353164.8&lt;/ACYTOTBAL&gt;&lt;ACYUNCOLLECTED&gt;0&lt;/ACYUNCOLLECTED&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_WARNING_RESP&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;ST-ACC-BRN&lt;/WCODE&gt;&lt;WDESC&gt;025&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;⚠️ **> ⚠️ **WARNING****&gt;&lt;WCODE&gt;GW-REV-01&lt;/WCODE&gt;&lt;WDESC&gt;La transacción se ha revertido correctamente&lt;/WDESC&gt;&lt;/⚠️ **> ⚠️ **WARNING****&gt;&lt;/FCUBS_WARNING_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;0&lt;/ifx:StatusCode&gt;&lt;ifx:Severity&gt;Info&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;Transaccion Exitosa&lt;/ifx:StatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;01&lt;/ifx:StatusCode&gt;&lt;ifx:StatusDesc&gt;GW-REV-01::La transacción se ha revertido correctamente&lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;1743628057674&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-02T16:07:39.644639-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP02 - ❌ **> ⚠️ **ERROR**** NEGOCIO

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – ❌ **> ⚠️ **ERROR**** de Negocio</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI: <br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
   &lt;soapenv:Header/&gt;
   &lt;soapenv:Body&gt;
      &lt;v1:addRtnBcSettleAccGMFRequest&gt;
         &lt;v1:RtnBcSettleAccGMFRq&gt;
            &lt;ifx:RqUID&gt;${=java.lang.System.currentTimeMillis()}&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:Concept&gt;SE&lt;/ifx:Concept&gt;
               &lt;ifx:AccountNumber&gt;500a800124811&lt;/ifx:AccountNumber&gt;
               &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRq&gt;
      &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;2323&lt;/ifx:StatusCode&gt;
               &lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;❌ **> ⚠️ **ERROR**** al validar numero de cuenta.&lt;/ifx:StatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;18&lt;/ifx:StatusCode&gt;
                  &lt;ifx:StatusDesc&gt;ST-ACC-318::❌ **> ⚠️ **ERROR**** al validar número de cuenta.&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;1743540767439&lt;/ifx:RqUID&gt;
            &lt;NS3:MsgRqHdr xmlns:NS3="urn://grupoaval.com/xsd/ifx/"&gt;
               &lt;NS3:ClientApp&gt;
                  &lt;NS3:Org&gt;BPOP&lt;/NS3:Org&gt;
                  &lt;NS3:Name&gt;CANALES&lt;/NS3:Name&gt;
                  &lt;NS3:Version&gt;1&lt;/NS3:Version&gt;
               &lt;/NS3:ClientApp&gt;
               &lt;NS4:Channel xmlns:NS4="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/NS4:Channel&gt;
               &lt;NS3:BankInfo&gt;
                  &lt;NS3:BankId&gt;0002&lt;/NS3:BankId&gt;
                  &lt;NS3:Name&gt;BPOP&lt;/NS3:Name&gt;
                  &lt;NS3:BranchId&gt;025&lt;/NS3:BranchId&gt;
               &lt;/NS3:BankInfo&gt;
               &lt;NS5:ClientDt xmlns:NS5="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/NS5:ClientDt&gt;
               &lt;NS6:IPAddr xmlns:NS6="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/NS6:IPAddr&gt;
               &lt;NS3:UserId&gt;
                  &lt;NS3:GovIssueIdent&gt;
                     &lt;NS3:GovIssueIdentType&gt;CC&lt;/NS3:GovIssueIdentType&gt;
                     &lt;NS3:IdentSerialNum&gt;79641609B&lt;/NS3:IdentSerialNum&gt;
                  &lt;/NS3:GovIssueIdent&gt;
               &lt;/NS3:UserId&gt;
               &lt;NS7:Reverse xmlns:NS7="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/NS7:Reverse&gt;
               &lt;NS8:Language xmlns:NS8="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/NS8:Language&gt;
               &lt;NS9:NextDay xmlns:NS9="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-01T15:52:47.817512-05:00&lt;/NS9:NextDay&gt;
            &lt;/NS3:MsgRqHdr&gt;
            &lt;ifx:MsgRsHdr&gt;
               &lt;ifx:TxCostAmt&gt;
                  &lt;ifx:CurAmt&gt;
                     &lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;
                     &lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;
                  &lt;/ifx:CurAmt&gt;
               &lt;/ifx:TxCostAmt&gt;
               &lt;ifx:EffDt&gt;2025-04-01T15:52:47.817512-05:00&lt;/ifx:EffDt&gt;
               &lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;
            &lt;/ifx:MsgRsHdr&gt;
            &lt;NS10:CustId xmlns:NS10="urn://grupoaval.com/xsd/ifx/"&gt;
               &lt;NS10:GovIssueIdent&gt;
                  &lt;NS10:GovIssueIdentType&gt;1&lt;/NS10:GovIssueIdentType&gt;
                  &lt;NS10:IdentSerialNum&gt;79641609&lt;/NS10:IdentSerialNum&gt;
               &lt;/NS10:GovIssueIdent&gt;
            &lt;/NS10:CustId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
</details>
</td>
      <td rowspan="2">Funciona</td>
      <td rowspan="2">Se envia numero de cuenta incorrecto</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio:<br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;NS2:RqUID xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;1743540767439&lt;/NS2:RqUID&gt;&lt;NS3:MsgRqHdr xmlns:NS3="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS3:ClientApp&gt;&lt;NS3:Org&gt;BPOP&lt;/NS3:Org&gt;&lt;NS3:Name&gt;CANALES&lt;/NS3:Name&gt;&lt;NS3:Version&gt;1&lt;/NS3:Version&gt;&lt;/NS3:ClientApp&gt;&lt;NS4:Channel xmlns:NS4="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/NS4:Channel&gt;&lt;NS3:BankInfo&gt;&lt;NS3:BankId&gt;0002&lt;/NS3:BankId&gt;&lt;NS3:Name&gt;BPOP&lt;/NS3:Name&gt;&lt;NS3:BranchId&gt;025&lt;/NS3:BranchId&gt;&lt;/NS3:BankInfo&gt;&lt;NS5:ClientDt xmlns:NS5="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/NS5:ClientDt&gt;&lt;NS6:IPAddr xmlns:NS6="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/NS6:IPAddr&gt;&lt;NS3:UserId&gt;&lt;NS3:GovIssueIdent&gt;&lt;NS3:GovIssueIdentType&gt;CC&lt;/NS3:GovIssueIdentType&gt;&lt;NS3:IdentSerialNum&gt;79641609B&lt;/NS3:IdentSerialNum&gt;&lt;/NS3:GovIssueIdent&gt;&lt;/NS3:UserId&gt;&lt;NS7:Reverse xmlns:NS7="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/NS7:Reverse&gt;&lt;NS8:Language xmlns:NS8="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/NS8:Language&gt;&lt;NS9:NextDay xmlns:NS9="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/NS9:NextDay&gt;&lt;/NS3:MsgRqHdr&gt;&lt;NS10:CustId xmlns:NS10="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS10:GovIssueIdent&gt;&lt;NS10:GovIssueIdentType&gt;1&lt;/NS10:GovIssueIdentType&gt;&lt;NS10:IdentSerialNum&gt;79641609&lt;/NS10:IdentSerialNum&gt;&lt;/NS10:GovIssueIdent&gt;&lt;/NS10:CustId&gt;&lt;NS11:ProductId xmlns:NS11="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS11:Concept&gt;SE&lt;/NS11:Concept&gt;&lt;NS11:AccountNumber&gt;*********4811&lt;/NS11:AccountNumber&gt;&lt;NS11:Amt&gt;1000&lt;/NS11:Amt&gt;&lt;/NS11:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743540767439&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743540767439&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;*********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743540767439&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743540767439&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12ce77c03&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743540767439&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;*********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743540767439&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;9250910009488449&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12ce77c03&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;MODULEID/&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MULTITRIPID&gt;6250910008746183&lt;/MULTITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;FAILURE&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743540767439&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;*********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743540767439&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_ERROR_RESP&gt;&lt;❌ **> ⚠️ **ERROR****&gt;&lt;ECODE&gt;&lt;![CDATA[ST-ACC-318]]&gt;&lt;/ECODE&gt;&lt;EDESC&gt;&lt;![CDATA[❌ **> ⚠️ **ERROR**** al validar número de cuenta.]]&gt;&lt;/EDESC&gt;&lt;/❌ **> ⚠️ **ERROR****&gt;&lt;/FCUBS_ERROR_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;FLEXCUBE&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;9250910009488449&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12ce77c03&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;MODULEID/&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;DESTINATION&gt;CNL&lt;/DESTINATION&gt;&lt;MULTITRIPID&gt;6250910008746183&lt;/MULTITRIPID&gt;&lt;FUNCTIONID&gt;DEGRTTLR&lt;/FUNCTIONID&gt;&lt;ACTION&gt;NEW&lt;/ACTION&gt;&lt;MSGSTAT&gt;FAILURE&lt;/MSGSTAT&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SERVERSTAT&lt;/NAME&gt;&lt;VALUE&gt;HOST&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743540767439&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;*********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743540767439&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_ERROR_RESP&gt;&lt;❌ **> ⚠️ **ERROR****&gt;&lt;ECODE&gt;&lt;![CDATA[ST-ACC-318]]&gt;&lt;/ECODE&gt;&lt;EDESC&gt;&lt;![CDATA[❌ **> ⚠️ **ERROR**** al validar número de cuenta.]]&gt;&lt;/EDESC&gt;&lt;/❌ **> ⚠️ **ERROR****&gt;&lt;/FCUBS_ERROR_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;2323&lt;/ifx:StatusCode&gt;&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;❌ **> ⚠️ **ERROR**** al validar numero de cuenta.&lt;/ifx:StatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;18&lt;/ifx:StatusCode&gt;&lt;ifx:StatusDesc&gt;ST-ACC-318::❌ **> ⚠️ **ERROR**** al validar número de cuenta.&lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;1743540767439&lt;/ifx:RqUID&gt;&lt;NS3:MsgRqHdr xmlns:NS3="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS3:ClientApp&gt;&lt;NS3:Org&gt;BPOP&lt;/NS3:Org&gt;&lt;NS3:Name&gt;CANALES&lt;/NS3:Name&gt;&lt;NS3:Version&gt;1&lt;/NS3:Version&gt;&lt;/NS3:ClientApp&gt;&lt;NS4:Channel xmlns:NS4="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/NS4:Channel&gt;&lt;NS3:BankInfo&gt;&lt;NS3:BankId&gt;0002&lt;/NS3:BankId&gt;&lt;NS3:Name&gt;BPOP&lt;/NS3:Name&gt;&lt;NS3:BranchId&gt;025&lt;/NS3:BranchId&gt;&lt;/NS3:BankInfo&gt;&lt;NS5:ClientDt xmlns:NS5="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/NS5:ClientDt&gt;&lt;NS6:IPAddr xmlns:NS6="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/NS6:IPAddr&gt;&lt;NS3:UserId&gt;&lt;NS3:GovIssueIdent&gt;&lt;NS3:GovIssueIdentType&gt;CC&lt;/NS3:GovIssueIdentType&gt;&lt;NS3:IdentSerialNum&gt;79641609B&lt;/NS3:IdentSerialNum&gt;&lt;/NS3:GovIssueIdent&gt;&lt;/NS3:UserId&gt;&lt;NS7:Reverse xmlns:NS7="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/NS7:Reverse&gt;&lt;NS8:Language xmlns:NS8="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/NS8:Language&gt;&lt;NS9:NextDay xmlns:NS9="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-01T15:52:47.817512-05:00&lt;/NS9:NextDay&gt;&lt;/NS3:MsgRqHdr&gt;&lt;ifx:MsgRsHdr&gt;&lt;ifx:TxCostAmt&gt;&lt;ifx:CurAmt&gt;&lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;&lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;&lt;/ifx:CurAmt&gt;&lt;/ifx:TxCostAmt&gt;&lt;ifx:EffDt&gt;2025-04-01T15:52:47.817512-05:00&lt;/ifx:EffDt&gt;&lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;&lt;/ifx:MsgRsHdr&gt;&lt;NS10:CustId xmlns:NS10="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS10:GovIssueIdent&gt;&lt;NS10:GovIssueIdentType&gt;1&lt;/NS10:GovIssueIdentType&gt;&lt;NS10:IdentSerialNum&gt;79641609&lt;/NS10:IdentSerialNum&gt;&lt;/NS10:GovIssueIdent&gt;&lt;/NS10:CustId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP03 - ❌ **> ⚠️ **ERROR**** VALIDACION ESTRUCTURA

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – ❌ **> ⚠️ **ERROR**** Validacion De Estructura</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.213.130.25:55544/services/fiduciaria</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
   &lt;soapenv:Header/&gt;
   &lt;soapenv:Body&gt;
      &lt;v1:addRtnBcSettleAccGMFRequest&gt;
         &lt;v1:RtnBcSettleAccGMFRq&gt;
               &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:Concept&gt;SE&lt;/ifx:Concept&gt;
               &lt;ifx:AccountNumber&gt;500a800124811&lt;/ifx:AccountNumber&gt;
               &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRq&gt;
      &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI:<br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;env:Envelope xmlns:mgmt="http://www.datapower.com/schemas/management" xmlns:date="http://exslt.org/dates-and-times" xmlns:dpquery="http://www.datapower.com/param/query" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;env:Body&gt;
      &lt;env:Fault&gt;
         &lt;faultcode&gt;env:Server&lt;/faultcode&gt;
         &lt;faultstring&gt;0x00230001: https://10.213.130.25:55544/services/fiduciaria: cvc-particle 3.1: in element {urn://grupoaval.com/inquiries/v1/}RtnBcSettleAccGMFRq of type {urn://grupoaval.com/accounts/v1/}RtnBcSettleAccGMFRq_Type, found &lt;ifx:MsgRqHdr&gt; (in namespace urn://grupoaval.com/xsd/ifx/), but next item should be {urn://grupoaval.com/xsd/ifx/}RqUID&lt;/faultstring&gt;
         &lt;detail&gt;
            &lt;errorCode&gt;0x00230001&lt;/errorCode&gt;
            &lt;errorMessage&gt;https://10.213.130.25:55544/services/fiduciaria: cvc-particle 3.1: in element {urn://grupoaval.com/inquiries/v1/}RtnBcSettleAccGMFRq of type {urn://grupoaval.com/accounts/v1/}RtnBcSettleAccGMFRq_Type, found &lt;ifx:MsgRqHdr&gt; (in namespace urn://grupoaval.com/xsd/ifx/), but next item should be {urn://grupoaval.com/xsd/ifx/}RqUID&lt;/errorMessage&gt;
            &lt;RqUID/&gt;
         &lt;/detail&gt;
      &lt;/env:Fault&gt;
   &lt;/env:Body&gt;
&lt;/env:Envelope&gt;
  </details>
  </td>
      <td rowspan="2">No Funciona, puesto que no deja trazabilidad</td>
      <td rowspan="2">Se elimiina campo ✅ **OBLIGATORIO**</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio:<br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;Sin Traza&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP04 - ❌ **> ⚠️ **ERROR**** TIMEOUT BACKEND

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – ❌ **> ⚠️ **ERROR**** Timeout Backend</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
   &lt;soapenv:Header/&gt;
   &lt;soapenv:Body&gt;
      &lt;v1:addRtnBcSettleAccGMFRequest&gt;
         &lt;v1:RtnBcSettleAccGMFRq&gt;
           &lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;${=java.lang.System.currentTimeMillis()}&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;					
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
            &lt;ifx:ProductId&gt;
               &lt;ifx:Concept&gt;SE&lt;/ifx:Concept&gt;
               &lt;ifx:AccountNumber&gt;500800124811&lt;/ifx:AccountNumber&gt;
               
               &lt;ifx:Amt&gt;1000&lt;/ifx:Amt&gt;
            &lt;/ifx:ProductId&gt;
         &lt;/v1:RtnBcSettleAccGMFRq&gt;
      &lt;/v1:addRtnBcSettleAccGMFRequest&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;
               &lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;TIEMPO RESPUESTA EXPIRADO&lt;/ifx:StatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;
                  &lt;ifx:StatusDesc&gt;91::❌ **> ⚠️ **ERROR**** de Timeout Procesando Mensaje en FlexCube - Srv CORE&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;1743629410142&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2025-04-02T16:30:16.669278-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:MsgRsHdr&gt;
               &lt;ifx:TxCostAmt&gt;
                  &lt;ifx:CurAmt&gt;
                     &lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;
                     &lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;
                  &lt;/ifx:CurAmt&gt;
               &lt;/ifx:TxCostAmt&gt;
               &lt;ifx:EffDt&gt;2025-04-02T16:30:16.669278-05:00&lt;/ifx:EffDt&gt;
               &lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;
            &lt;/ifx:MsgRsHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
  </details>
  </td>
      <td rowspan="2">Funciona</td>
      <td rowspan="2"> Se elimina el campo de oficina</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
    &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743629410142&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743629410142&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743629410142&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743629410142&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743629410142&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc813&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743629410142&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743629410142&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743629410142&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc813&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743629410142&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;MSGSTAT&gt;FAILURE&lt;/MSGSTAT&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743629410142&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_ERROR_RESP&gt;&lt;❌ **> ⚠️ **ERROR****&gt;&lt;ECODE&gt;91&lt;/ECODE&gt;&lt;EDESC&gt;❌ **> ⚠️ **ERROR**** de Timeout Procesando Mensaje en FlexCube - Srv CORE&lt;/EDESC&gt;&lt;/❌ **> ⚠️ **ERROR****&gt;&lt;/FCUBS_ERROR_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_RES_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743629410142&lt;/MSGID&gt;&lt;CORRELID&gt;414d5120574d4244455642502020202067a98be12d0cc813&lt;/CORRELID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743629410142&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;MSGSTAT&gt;FAILURE&lt;/MSGSTAT&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743629410142&lt;/XREF&gt;&lt;/Transaction-Details&gt;&lt;FCUBS_ERROR_RESP&gt;&lt;❌ **> ⚠️ **ERROR****&gt;&lt;ECODE&gt;91&lt;/ECODE&gt;&lt;EDESC&gt;❌ **> ⚠️ **ERROR**** de Timeout Procesando Mensaje en FlexCube - Srv CORE&lt;/EDESC&gt;&lt;/❌ **> ⚠️ **ERROR****&gt;&lt;/FCUBS_ERROR_RESP&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_RES_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;TIEMPO RESPUESTA EXPIRADO&lt;/ifx:StatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;&lt;ifx:StatusDesc&gt;91::❌ **> ⚠️ **ERROR**** de Timeout Procesando Mensaje en FlexCube - Srv CORE&lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;1743629410142&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2025-04-02T16:30:16.669278-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:MsgRsHdr&gt;&lt;ifx:TxCostAmt&gt;&lt;ifx:CurAmt&gt;&lt;ifx:Amt&gt;0&lt;/ifx:Amt&gt;&lt;ifx:CurCode&gt;COP&lt;/ifx:CurCode&gt;&lt;/ifx:CurAmt&gt;&lt;/ifx:TxCostAmt&gt;&lt;ifx:EffDt&gt;2025-04-02T16:30:16.669278-05:00&lt;/ifx:EffDt&gt;&lt;ifx:RemainRec&gt;false&lt;/ifx:RemainRec&gt;&lt;/ifx:MsgRsHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP05 - ❌ **> ⚠️ **ERROR**** CONEXION

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – ❌ **> ⚠️ **ERROR**** de Conexion</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br/>
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;XMLNSC&gt;
	&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
		&lt;NS1:RtnBcSettleAccGMFRq&gt;
			&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743630430592&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
					&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
			&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;
				&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;
				&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;
			&lt;/NS2:ProductId&gt;
		&lt;/NS1:RtnBcSettleAccGMFRq&gt;
	&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;
&lt;/XMLNSC&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;
	&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
		&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
			&lt;ifx:Status&gt;
				&lt;ifx:StatusCode&gt;300&lt;/ifx:StatusCode&gt;
				&lt;ifx:ServerStatusCode&gt;300&lt;/ifx:ServerStatusCode&gt;
				&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
				&lt;ifx:StatusDesc&gt;No es posible procesar la transaccion - Problemas tecnicos. Por favor intente mas tarde.&lt;/ifx:StatusDesc&gt;
				&lt;ifx:ServerStatusDesc&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:ServerStatusDesc&gt;
				&lt;ifx:AdditionalStatus&gt;
					&lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;
					&lt;ifx:ServerStatusCode&gt;91&lt;/ifx:ServerStatusCode&gt;
					&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
					&lt;ifx:StatusDesc&gt;User exception thrown by throw **node** :  - FCUBSRTService_CreateTransaction FC - TimeOut recibiendo mensaje de respuesta de Adaptador de Integracion. - &lt;/ifx:StatusDesc&gt;
				&lt;/ifx:AdditionalStatus&gt;
			&lt;/ifx:Status&gt;
			&lt;ifx:RqUID&gt;1743630430592&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
					&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
		&lt;/v1:RtnBcSettleAccGMFRs&gt;
	&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
&lt;/XMLNSC&gt;
  </details>
  </td>
      <td rowspan="2">Funciona</td>
      <td rowspan="2"> Se inhabilita el adaptador de FC</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743630430592&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;FCUBS_REQ_ENV xmlns="http://fcubs.ofss.com/service/FCUBSRTService"&gt;&lt;FCUBS_HEADER&gt;&lt;SOURCE&gt;CNL&lt;/SOURCE&gt;&lt;UBSCOMP&gt;FCUBS&lt;/UBSCOMP&gt;&lt;MSGID&gt;1743630430592&lt;/MSGID&gt;&lt;USERID&gt;CHNLUSER1&lt;/USERID&gt;&lt;BRANCH&gt;025&lt;/BRANCH&gt;&lt;SERVICE&gt;FCUBSRTService&lt;/SERVICE&gt;&lt;OPERATION&gt;CreateTransaction&lt;/OPERATION&gt;&lt;SOURCE_OPERATION&gt;CreateTransaction&lt;/SOURCE_OPERATION&gt;&lt;SOURCE_USERID&gt;79641609B&lt;/SOURCE_USERID&gt;&lt;ADDL&gt;&lt;PARAM&gt;&lt;NAME&gt;CUTOFFSTAT&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;SSUPERVISION&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;TERMINAL&lt;/NAME&gt;&lt;VALUE&gt;1&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;PARAM&gt;&lt;NAME&gt;XREF&lt;/NAME&gt;&lt;VALUE&gt;1743630430592&lt;/VALUE&gt;&lt;/PARAM&gt;&lt;/ADDL&gt;&lt;/FCUBS_HEADER&gt;&lt;FCUBS_BODY&gt;&lt;Transaction-Details&gt;&lt;TXNACC&gt;********4811&lt;/TXNACC&gt;&lt;PRD&gt;A2BE&lt;/PRD&gt;&lt;TXNAMT&gt;1000&lt;/TXNAMT&gt;&lt;TXNCCY&gt;COP&lt;/TXNCCY&gt;&lt;XREF&gt;1743630430592&lt;/XREF&gt;&lt;BRN&gt;025&lt;/BRN&gt;&lt;/Transaction-Details&gt;&lt;/FCUBS_BODY&gt;&lt;/FCUBS_REQ_ENV&gt;&lt;/XMLNSC&gt;&lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;&lt;ifx:Status&gt;&lt;ifx:StatusCode&gt;300&lt;/ifx:StatusCode&gt;&lt;ifx:ServerStatusCode&gt;300&lt;/ifx:ServerStatusCode&gt;&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;No es posible procesar la transaccion - Problemas tecnicos. Por favor intente mas tarde.&lt;/ifx:StatusDesc&gt;&lt;ifx:ServerStatusDesc&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:ServerStatusDesc&gt;&lt;ifx:AdditionalStatus&gt;&lt;ifx:StatusCode&gt;91&lt;/ifx:StatusCode&gt;&lt;ifx:ServerStatusCode&gt;91&lt;/ifx:ServerStatusCode&gt;&lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;&lt;ifx:StatusDesc&gt;User exception thrown by throw **node** :  - FCUBSRTService_CreateTransaction FC - TimeOut recibiendo mensaje de respuesta de Adaptador de Integracion. - &lt;/ifx:StatusDesc&gt;&lt;/ifx:AdditionalStatus&gt;&lt;/ifx:Status&gt;&lt;ifx:RqUID&gt;1743630430592&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;/v1:RtnBcSettleAccGMFRs&gt;&lt;/NS1:addRtnBcSettleAccGMFResponse&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

## CP06 - ❌ **> ⚠️ **ERROR**** APLICACION

<table border="1" cellspacing="0" cellpadding="5">
  <thead>
    <tr>
      <th rowspan="2">ID<br>CasoPrueba</th>
      <th colspan="3">Caso de Prueba – ❌ **> ⚠️ **ERROR**** Aplicacion</th>
      <th colspan="2">Fecha de Ejecución : 02/04/2025</th>
    </tr>
    <tr>
      <td colspan="3">
        URL de prueba:
        <a href="#">https://10.200.157.5:9023/accounts/SSL/ReturnBalanceSettleAccGMF</a>
      </td>
      <th>ESTADO PRUEBA</th>
      <th>OBSERVACIONES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">1</td>
      <td rowspan="2">
      <details>
        Mensaje inyectado por SoapUI:<br />
        <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
&lt;XMLNSC&gt;
	&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
		&lt;NS1:RtnBcSettleAccGMFRq&gt;
			&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743630430592&lt;/ifx:RqUID&gt;
			&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:ClientApp&gt;
					&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
					&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
					&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
				&lt;/ifx:ClientApp&gt;
				&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;
				&lt;ifx:BankInfo&gt;
					&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
					&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
					&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
				&lt;/ifx:BankInfo&gt;
				&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
				&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;
				&lt;ifx:UserId&gt;
					&lt;ifx:GovIssueIdent&gt;
						&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
						&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
					&lt;/ifx:GovIssueIdent&gt;
				&lt;/ifx:UserId&gt;
				&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;
				&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;
				&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
			&lt;/ifx:MsgRqHdr&gt;
			&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;ifx:GovIssueIdent&gt;
					&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
					&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
				&lt;/ifx:GovIssueIdent&gt;
			&lt;/ifx:CustId&gt;
			&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;
				&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;
				&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;
				&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;
			&lt;/NS2:ProductId&gt;
		&lt;/NS1:RtnBcSettleAccGMFRq&gt;
	&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;
&lt;/XMLNSC&gt;
        </pre>
        </details>
      </td>
      <td>Mensaje de Respuesta</td>
      <td>
      <details>
      Mensaje de Respuesta por SOAPUI: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">     
   &lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
   &lt;soapenv:Body&gt;
      &lt;NS1:addRtnBcSettleAccGMFResponse xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;
         &lt;v1:RtnBcSettleAccGMFRs xmlns:v1="urn://grupoaval.com/accounts/v1/" xmlns:ifx="urn://grupoaval.com/xsd/ifx/" xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;
            &lt;ifx:Status&gt;
               &lt;ifx:StatusCode&gt;100&lt;/ifx:StatusCode&gt;
               &lt;ifx:ServerStatusCode&gt;100&lt;/ifx:ServerStatusCode&gt;
               &lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
               &lt;ifx:StatusDesc&gt;No es posible procesar la transacción. Comuníquese con la Entidad.&lt;/ifx:StatusDesc&gt;
               &lt;ifx:ServerStatusDesc&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:ServerStatusDesc&gt;
               &lt;ifx:AdditionalStatus&gt;
                  &lt;ifx:StatusCode&gt;2667&lt;/ifx:StatusCode&gt;
                  &lt;ifx:ServerStatusCode&gt;2667&lt;/ifx:ServerStatusCode&gt;
                  &lt;ifx:Severity&gt;❌ **> ⚠️ **ERROR****&lt;/ifx:Severity&gt;
                  &lt;ifx:StatusDesc&gt;Failed to put message :  - co.com.bancopopular.fcd.ReturnBalanceSettleAccGMFFcdWS_REQ.RLGetConfigParams -  - Caught exception and rethrowing -  - co.com.bancopopular.fcd.ReturnBalanceSettleAccGMFFcdWS_REQ.MQOUT.GENERIC.SRV.REQ -  - Single ❌ **> ⚠️ **ERROR**** whilst putting to a queue -  - co.com.bancopopular.fcd.ReturnBalanceSettleAccGMFFcdWS_REQ.MQOUT.GENERIC.SRV.REQ -  - Failed to put message -  - -1 -  - MQW102 -  - 2051 -  - WMBDEVBP -  - MQINP.RTNBALANCESETTLEACC.ORCH.REQ -  - co.com.bancopopular.fcd.ReturnBalanceSettleAccGMFFcdWS_REQ.MQOUT.GENERIC.SRV.REQ -&lt;/ifx:StatusDesc&gt;
               &lt;/ifx:AdditionalStatus&gt;
            &lt;/ifx:Status&gt;
            &lt;ifx:RqUID&gt;1743631141714&lt;/ifx:RqUID&gt;
            &lt;ifx:MsgRqHdr&gt;
               &lt;ifx:ClientApp&gt;
                  &lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;
                  &lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;
                  &lt;ifx:Version&gt;1&lt;/ifx:Version&gt;
               &lt;/ifx:ClientApp&gt;
               &lt;v2:Channel&gt;CANALES&lt;/v2:Channel&gt;
               &lt;ifx:BankInfo&gt;
                  &lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;
                  &lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;
                  &lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;
               &lt;/ifx:BankInfo&gt;
               &lt;v2:ClientDt&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;
               &lt;v2:IPAddr&gt;1&lt;/v2:IPAddr&gt;
               &lt;ifx:UserId&gt;
                  &lt;ifx:GovIssueIdent&gt;
                     &lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;
                     &lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;
                  &lt;/ifx:GovIssueIdent&gt;
               &lt;/ifx:UserId&gt;
               &lt;v2:Reverse&gt;false&lt;/v2:Reverse&gt;
               &lt;v2:Language&gt;ES&lt;/v2:Language&gt;
               &lt;v2:NextDay&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;
            &lt;/ifx:MsgRqHdr&gt;
            &lt;ifx:CustId&gt;
               &lt;ifx:GovIssueIdent&gt;
                  &lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;
                  &lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;
               &lt;/ifx:GovIssueIdent&gt;
            &lt;/ifx:CustId&gt;
         &lt;/v1:RtnBcSettleAccGMFRs&gt;
      &lt;/NS1:addRtnBcSettleAccGMFResponse&gt;
   &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
</details>
</td>
      <td rowspan="2">Funciona</td>
      <td rowspan="2">Se inhibe objeto MQ</td>
    </tr>
    <tr>
      <td>Trazabilidad</td>
      <td>
      <details>
      Traza del Servicio: <br/>
      <pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 11px;">
      &lt;XMLNSC&gt;&lt;NS1:addRtnBcSettleAccGMFRequest xmlns:NS1="urn://grupoaval.com/accounts/v1/"&gt;&lt;NS1:RtnBcSettleAccGMFRq&gt;&lt;ifx:RqUID xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;1743631141714&lt;/ifx:RqUID&gt;&lt;ifx:MsgRqHdr xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:ClientApp&gt;&lt;ifx:Org&gt;BPOP&lt;/ifx:Org&gt;&lt;ifx:Name&gt;CANALES&lt;/ifx:Name&gt;&lt;ifx:Version&gt;1&lt;/ifx:Version&gt;&lt;/ifx:ClientApp&gt;&lt;v2:Channel xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;CANALES&lt;/v2:Channel&gt;&lt;ifx:BankInfo&gt;&lt;ifx:BankId&gt;0002&lt;/ifx:BankId&gt;&lt;ifx:Name&gt;BPOP&lt;/ifx:Name&gt;&lt;ifx:BranchId&gt;025&lt;/ifx:BranchId&gt;&lt;/ifx:BankInfo&gt;&lt;v2:ClientDt xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2024-03-08T10:00:00&lt;/v2:ClientDt&gt;&lt;v2:IPAddr xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;1&lt;/v2:IPAddr&gt;&lt;ifx:UserId&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;CC&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609B&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:UserId&gt;&lt;v2:Reverse xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;false&lt;/v2:Reverse&gt;&lt;v2:Language xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;ES&lt;/v2:Language&gt;&lt;v2:NextDay xmlns:v2="urn://grupoaval.com/xsd/ifx/v2/"&gt;2021-07-16T17:14:59.489-05:00&lt;/v2:NextDay&gt;&lt;/ifx:MsgRqHdr&gt;&lt;ifx:CustId xmlns:ifx="urn://grupoaval.com/xsd/ifx/"&gt;&lt;ifx:GovIssueIdent&gt;&lt;ifx:GovIssueIdentType&gt;1&lt;/ifx:GovIssueIdentType&gt;&lt;ifx:IdentSerialNum&gt;79641609&lt;/ifx:IdentSerialNum&gt;&lt;/ifx:GovIssueIdent&gt;&lt;/ifx:CustId&gt;&lt;NS2:ProductId xmlns:NS2="urn://grupoaval.com/xsd/ifx/"&gt;&lt;NS2:Concept&gt;SE&lt;/NS2:Concept&gt;&lt;NS2:AccountNumber&gt;********4811&lt;/NS2:AccountNumber&gt;&lt;NS2:Amt&gt;1000&lt;/NS2:Amt&gt;&lt;/NS2:ProductId&gt;&lt;/NS1:RtnBcSettleAccGMFRq&gt;&lt;/NS1:addRtnBcSettleAccGMFRequest&gt;&lt;/XMLNSC&gt;
      </details>
      </td>
    </tr>
  </tbody>
</table>

```
```

## Reglas a Validar
```
📄 6.2 En el documento de pruebas deben existir 6 escenarios. El código de esatus de los casos exitosos debe ser 0. El código de estatus del ❌ **> ⚠️ **ERROR**** de timeout debe ser 91. El código de estatus del ❌ **> ⚠️ **ERROR**** de conexión debe ser 300. En el ❌ **> ⚠️ **ERROR**** de aplicación en la trama del mensaje de respuesta debe estar presente la representación de la estructura de carpetas de la aplicación: co.com.bancopopular.[nombre de carpeta segun el servicio]
📄 6.3 Las url's de prueba deben coincidir con las url's de las etiquetas endpoint del documento xml de soapui
📄 6.4 Debe incluirse la traza completa de la transacción, generando logs en la tabla de excepciones solo para errores de timeout, conexión y aplicación, pero no para escenarios exitosos ni errores de negocio. En cada uno de los casos el mensaje de respuesta debe estar presente en la trazabilidad y el RqUID debe coincidir.
📄 6.6 Deben especificarse los pasos ejecutados para obtener cada escenario y su respectivo RQUID.
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