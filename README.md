# Structured Report xml to FHIR

## These scripts are a proof-of-concept to include data from diagnostic reports (from Mint Lesion) in FHIR resources. They are meant to conform to the profiles defined in the [KDS imaging module](https://simplifier.net/medizininformatik-initiative-modul-bildgebung) by the [Medizininformatik-Initiative](https://www.medizininformatik-initiative.de/en/start).

For each XML file as input, a [DiagnosticReport](https://hl7.org/fhir/R4/diagnosticreport.html) resource is created, which can in turn reference multiple [Observation](https://hl7.org/fhir/R4/observation.html) resources, all of which are also created. Currently, these scripts support the use case of retum carcinoma and up to six different Observation resources per DiagnosticReport. The scripts are highly tailored to the XML format exported by [Mint Lesion](https://mint-medical.com/de/mint-lesion/) and are not meant to replace a proper definition of FHIR resources from this data.
