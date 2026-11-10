<?xml version="1.0" encoding="UTF-8"?>
<SCL xmlns="http://www.iec.ch/61850/2003/SCL" version="2007" revision="B">
  <Substation name="TBA110_DEMO">
    <PowerTransformer name="T1" type="PTR">
      <TransformerWinding name="W1" type="PTW"/><TransformerWinding name="W2" type="PTW"/>
      <LNode iedName="MON_T1" ldInst="CM" lnClass="SIML" lnInst="1"/>
    </PowerTransformer>
    <VoltageLevel name="E1"><Voltage unit="V" multiplier="k">110</Voltage>
      <Bay name="E131"><ConductingEquipment name="QA1" type="CBR"><LNode iedName="BCU_E131" ldInst="CTRL" lnClass="XCBR" lnInst="1"/></ConductingEquipment>
        <ConductingEquipment name="QB1" type="DIS"/></Bay>
    </VoltageLevel>
  </Substation>
  <IED name="MON_T1" manufacturer="VTI"><AccessPoint name="AP1"><Server><LDevice inst="CM">
    <LN0 lnClass="LLN0" inst=""/><LN lnClass="SIML" inst="1"/><LN prefix="HS" lnClass="STMP" inst="1"/><LN lnClass="SPDC" inst="1"/>
  </LDevice></Server></AccessPoint></IED>
</SCL>
