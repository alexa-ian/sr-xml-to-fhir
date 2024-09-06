import datetime

def get_patient(root):

    patid = root.xpath('//Patient/@PatientID')

    return patid[0]

def get_id(root):

    id = root.xpath('//Task/@AssessmentID')

    return int(id[0])

def get_modality(root):

    path = root.xpath('//MeasurementRecord/@Modality')

    for mod in path:
        if len(mod)>0:
            return mod
    path = root.xpath('//DicomSeries/@Modality')

    for mod in path:
        if len(mod)>0:
            return mod

def get_acsn(root):

    path = root.xpath('//MeasurementRecord/@AccessionNumber')

    for number in path:
        if len(number)>0:
            return number

    path = root.xpath('//DicomStudy/@AccessionNumber')

    for number in path:
        if len(number)>0:
            return number

def get_datetime(root):

    date_time = root.xpath('//Assessment/@AssessmentDate')

    date = date_time[0].split("T")[0]
    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]

    time = date_time[0].split("T")[1]
    hour = time.split(":")[0]
    minutes = time.split(":")[1]
    seconds = time.split(":")[2]

    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds))