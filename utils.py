from datetime import datetime

from fhir.resources.R4B import identifier
from fhir.resources.R4B import codeableconcept
from fhir.resources.R4B import coding
from fhir.resources.R4B import patient
from fhir.resources.R4B import humanname
from fhir.resources.R4B import fhirtypes
from fhir.resources.R4B import reference
from fhir.resources.R4B import extension
from fhir.resources.R4B.quantity import Quantity

TERMINOLOGY_CODING_SYS = "http://terminology.hl7.org/CodeSystem/v2-0203"
TERMINOLOGY_CODING_SYS_CODE_ACCESSION = "ACSN"
TERMINOLOGY_CODING_SYS_CODE_MRN = "MR"

def gen_identifier(id):
    idf = identifier.Identifier()
    idf.use = "usual"
    idf.type = codeableconcept.CodeableConcept()
    idf.type.coding = []
    case = coding.Coding()
    case.system = TERMINOLOGY_CODING_SYS
    case.code = TERMINOLOGY_CODING_SYS_CODE_ACCESSION

    idf.type.coding.append(case)
    idf.value = id
    return idf


def get_patient_resource_ids(PatientID, IssuerOfPatientID):
    idf = identifier.Identifier()
    idf.use = "usual"
    idf.value = PatientID

    idf.type = codeableconcept.CodeableConcept()
    idf.type.coding = []
    id_coding = coding.Coding()
    id_coding.system = TERMINOLOGY_CODING_SYS
    id_coding.code = TERMINOLOGY_CODING_SYS_CODE_MRN
    idf.type.coding.append(id_coding)

    if IssuerOfPatientID is not None:
        idf.assigner = reference.Reference()
        idf.assigner.display = IssuerOfPatientID

    return idf


def calc_gender(gender):
    if gender is None:
        return "unknown"
    if not gender:
        return "unknown"
    if gender.upper().lower() == "f":
        return "female"
    if gender.upper().lower() == "m":
        return "male"
    if gender.upper().lower() == "o":
        return "other"

    return "unknown"


def calc_dob(dicom_dob):
    if dicom_dob == '':
        return None

    try:
        dob = datetime.strptime(dicom_dob, '%Y%m%d')
        fhir_dob = fhirtypes.Date(
            dob.year,
            dob.month,
            dob.day
        )
    except Exception:
        return None
    return fhir_dob


def inline_patient_resource(referenceId, PatientID, IssuerOfPatientID, patientName, gender, dob):
    p = patient.Patient()
    p.id = referenceId
    p.name = []
    # p.use = "official"
    p.identifier = [get_patient_resource_ids(PatientID, IssuerOfPatientID)]
    hn = humanname.HumanName()
    hn.family = patientName.family_name
    if patientName.given_name != '':
        hn.given = [patientName.given_name]
    p.name.append(hn)
    p.gender = calc_gender(gender)
    p.birthDate = calc_dob(dob)
    p.active = True
    return p


def gen_procedurecode_array(procedures):
    if procedures is None:
        return None
    fhir_proc = []
    for p in procedures:
        concept = codeableconcept.CodeableConcept()
        c = coding.Coding()
        c.system = p["system"]
        c.code = p["code"]
        c.display = p["display"]
        concept.coding = []
        concept.coding.append(c)
        concept.text = p["display"]
        fhir_proc.append(concept)
    if len(fhir_proc) > 0:
        return fhir_proc
    return None


def gen_started_datetime(dt, tm):
    if dt is None:
        return None

    dt_pattern = '%Y%m%d'

    if tm is not None and len(tm) >= 6:
        studytm = datetime.strptime(tm[0:6], '%H%M%S')

        dt_string = dt + " " + str(studytm.hour) + ":" + \
            str(studytm.minute) + ":" + str(studytm.second)
        dt_pattern = dt_pattern + " %H:%M:%S"
    else:
        dt_string = dt

    dt_date = datetime.strptime(dt_string, dt_pattern)

    # strangely, providing the datetime.date object does not work
    fhirDtm = fhirtypes.DateTime(
        dt_date.year,
        dt_date.month,
        dt_date.day,
        dt_date.hour,
        dt_date.minute,
        dt_date.second,
        tzinfo="+01:00"
    )

    return fhirDtm


def gen_reason(reason, reasonStr):
    if reason is None and reasonStr is None:
        return None
    reasonList = []
    if reason is None or len(reason) <= 0:
        rc = codeableconcept.CodeableConcept()
        rc.text = reasonStr
        reasonList.append(rc)
        return reasonList

    for r in reason:
        rc = codeableconcept.CodeableConcept()
        rc.coding = []
        c = coding.Coding()
        c.system = r["system"]
        c.code = r["code"]
        c.display = r["display"]
        rc.coding.append(c)
        reasonList.append(rc)
    return reasonList


def gen_coding(value, system, display=None):
    if isinstance(value, list):
        raise Exception(
        "More than one code for type Coding detected")
    c = coding.Coding()
    c.system = system
    c.code = value
    c.display = display
    return c


def gen_codeable_concept(value_list: list, system, display=None):
    c = codeableconcept.CodeableConcept()
    c.coding = []
    for _l in value_list:
        m = gen_coding(_l, system, display)
        c.coding.append(m)
    return c


def gen_coding_text_only(text):
    c = coding.Coding()
    c.code = text
    c.userSelected = True
    return c

def gen_extension(url):
    e = extension.Extension()
    e.url = url
    
    return e

def add_extension_value(e, url, value, system, unit, type, display=None):

    if type == "string":
        e.valueString = value
        e.url = url

    if type == "quantity":
        e.url = url
        value_quantity = Quantity()
        value_quantity.value = value
        value_quantity.unit = unit
        value_quantity.system = system
        e.valueQuantity = value_quantity

    if type == "boolean":
        e.url = url
        e.valueBoolean = value

    if type == "reference":
        e.url = url
        e.valueReference = value
    
    if type == "datetime":
        e.url = url
        e.valueDateTime = value

    if type == "id":
        e.url = url
        e.valueId = value

    if type == "codeableconcept":
        e.url = url
        c = gen_codeable_concept([value], system, display)
        e.valueCodeableConcept = c
        
    return e