from fhir.resources import R4B as fr
from fhir.resources.R4B import reference
from fhir.resources.R4B import observation
from fhir.resources.R4B import identifier
from fhir.resources.R4B import quantity
from fhir.resources.R4B import diagnosticreport
from fhir.resources.R4B import codeableconcept
import get_xml_values
import get_xml_values
import utils
import hashlib

from lxml import etree

with open("befund14.xml", 'r', encoding='utf-8') as file:
    xml_string = file.read()
root = etree.fromstring(xml_string)

output_path = "C:/Users/iancuaa/Desktop/output/"
counter = 0


def create_dr():

    data = {}

    patID9 = str(get_xml_values.get_patient(root))[:9]
    patIdentifier = "https://fhir.diz.uk-erlangen.de/identifiers/patient-id|"+patID9
    hashedIdentifier = hashlib.sha256(
        patIdentifier.encode('utf-8')).hexdigest()
    patientReference = "Patient/"+hashedIdentifier
    patientRef = reference.Reference()
    patientRef.reference = patientReference
    patIdent = identifier.Identifier()
    patIdent.system = "https://fhir.diz.uk-erlangen.de/identifiers/patient-id"
    patIdent.type = utils.gen_codeable_concept(
        ["MR"], "http://terminology.hl7.org/CodeSystem/v2-0203")
    patIdent.value = patID9
    patientRef.identifier = patIdent
    data["subject"] = patientRef

    data["identifier"] = [identifier.Identifier(
        value=get_xml_values.get_id(root))]

    data["status"] = "final"

    data["category"] = [utils.gen_codeable_concept(
        ["4201000179104"], "http://snomed.info/sct", "Imaging report")]

    if get_xml_values.get_modality(root) == "MR":
        mod_code = ("4251000179103", "Magnetic resonance imaging report")
    if get_xml_values.get_modality(root) == "CT":
        mod_code = ("4261000179100", "Computed tomography imaging report")
    if get_xml_values.get_modality(root) == "MG":
        mod_code = ("4231000179109", "Mammography report")

    data["code"] = utils.gen_codeable_concept(
        [mod_code[0]], "http://snomed.info/sct", mod_code[1])

    data["effectiveDateTime"] = get_xml_values.get_datetime(root)

    observations = []

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/Analkanal", result=get_xml_values.get_analkanal(root),
                          code=("249653002", "Anal canal finding"), patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="boolean") is not None:
        analkanal = reference.Reference()
        analkanal.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/Analkanal"
        observations.append(analkanal)

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/MRF", result=get_xml_values.get_MRF(root), code=("408655002",
                                                                                                                               "Status of intactness of mesorectal specimen"), patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="boolean") is not None:
        MRF = reference.Reference()
        MRF.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/MRF"
        observations.append(MRF)

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/EMVI", result=get_xml_values.get_EMVI(root), code=("1286755009",
                                                                                                                                 "Presence of direct invasion by primary malignant neoplasm of cecum and/or colon and/or rectum to blood vessel in pericolic tissue"),
                          patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="boolean") is not None:
        EMVI = reference.Reference()
        EMVI.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/EMVI"
        observations.append(EMVI)

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/Tumor-Oberrand", result=get_xml_values.get_höhe_tumor_oberrand(root),
                          code=None, patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="quantity", text="Höhe des Tumor-Oberrandes ab ano") is not None:
        hoehe_oberrand = reference.Reference()
        hoehe_oberrand.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/Tumor-Oberrand"
        observations.append(hoehe_oberrand)

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/Tumor-Unterrand", result=get_xml_values.get_höhe_tumor_unterrand(root),
                          code=None, patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="quantity", text="Höhe des Tumor-Unterrandes ab ano", sop_instance_available=True) is not None:
        hoehe_unterrand = reference.Reference()
        hoehe_unterrand.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/Tumor-Unterrand"
        observations.append(hoehe_unterrand)

    if create_observation(ident=patID9+"/"+str(get_xml_values.get_id(root))+"/TNM", result=get_xml_values.get_TNM(root), code=("260879005",
                                                                                                                               "International Union Against Cancer stage grouping"), patientRef=patientRef, acsn=get_xml_values.get_acsn(root), type="component-codeableconcept") is not None:
        TNM = reference.Reference()
        TNM.reference = "Observation/" + \
            str(get_xml_values.get_id(root))+"/TNM"
        observations.append(TNM)

    data["result"] = observations

    imagingStudy = reference.Reference()
    imagingStudy.reference = "ImagingStudy/" + \
        str(get_xml_values.get_acsn(root))
    data["imagingStudy"] = [imagingStudy]

    dr = diagnosticreport.DiagnosticReport(**data)

    try:
        jsonfile = output_path + \
            str(get_xml_values.get_id(root)) + "_dr.json"
        with open(jsonfile, "w+") as outfile:
            outfile.write(dr.json())
    except Exception:
        print("Unable to create JSON-file")

    return dr


def create_observation(ident, result, code, patientRef, acsn, type, text=None, sop_instance_available=False):

    if result == None:
        return

    global counter

    obs_data = {}

    obs_data["identifier"] = [identifier.Identifier(value=ident)]
    obs_data["id"] = "TODO"
    obs_data["status"] = "final"
    obs_data["category"] = [utils.gen_codeable_concept(
        ["imaging"], "http://terminology.hl7.org/CodeSystem/observation-category", "Imaging")]
    
    if code is None:
         c = codeableconcept.CodeableConcept()
         c.text = text
         obs_data["code"] = c
    else:
        obs_data["code"] = utils.gen_codeable_concept([code[0]], "http://snomed.info/sct", code[1])
    obs_data["subject"] = patientRef
    derivedFrom = reference.Reference()
    derivedFrom.reference = "ImagingStudy/"+acsn
    obs_data["derivedFrom"] = [derivedFrom]

    if type == "boolean":
        obs_data["valueBoolean"] = result

    if type == "quantity":
        value_quantity = quantity.Quantity()
        value_quantity.value = result[0]
        value_quantity.unit = result[1]
        value_quantity.system = "http://unitsofmeasure.org"
        obs_data["valueQuantity"] = value_quantity

    if type == "component-codeableconcept":
        comp = []

        for r in result:

            c = observation.ObservationComponent(code=utils.gen_codeable_concept(
                ["399537006"], "http://snomed.info/sct", "Clinical TNM stage grouping"))
            c.valueCodeableConcept = utils.gen_codeable_concept(
                [r], "https://www.uicc.org/resources/tnm", display=r)
            comp.append(c)

        obs_data["component"] = comp

    sop_instance = None

    if sop_instance_available == True:
        try:
            sop_instance = get_xml_values.get_höhe_tumor_unterrand(root)[2]
        except Exception:
            pass

    if sop_instance is not None:

        e = utils.gen_extension(
            url="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-sop-instanz-uid")
        utils.add_extension_value(e, url="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-sop-instanz-uid",
                                  value=sop_instance, system=None, type="id", unit=None)
        obs_data["extension"] = [e]

    obs = observation.Observation(**obs_data)

    try:
        jsonfile = output_path + \
            str(get_xml_values.get_id(root)) + "_" + str(counter) + "_obs.json"
        with open(jsonfile, "w+") as outfile:
            outfile.write(obs.json())
    except Exception:
        print("Unable to create JSON-file")

    counter += 1

    return obs


create_dr()
