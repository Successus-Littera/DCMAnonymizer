import os
import datetime as dt

from PyQt5.QtCore import *
import pydicom


def GetSeriesTime(ds):
    string = getattr(ds, "StructureSetTime", None) or getattr(ds, "SeriesTime", None)
    if string:
        if len(string) > 6:
            return dt.datetime.strptime(string, "%H%M%S.%f").time().strftime("%H:%M:%S")
        elif len(string) == 6:
            return dt.datetime.strptime(string, "%H%M%S").time().strftime("%H:%M:%S")
    return 'N/A'


def GetSeriesDate(ds):
    string = getattr(ds, "StructureSetDate", None) or getattr(ds, "SeriesDate", None)
    if string:
        return dt.datetime.strptime(string, "%Y%m%d").date().strftime("%Y/%m/%d")
    return 'N/A'


def GetStudyDate(ds):
    string = getattr(ds, "StudyDate", None)
    if string:
        return dt.datetime.strptime(string, "%Y%m%d").date().strftime("%Y/%m/%d")
    return 'N/A'


def uid_to_name(uid):
    dic = {
        '1.2.840.10008.5.1.4.1.1.1': 'X-Ray',
        '1.2.840.10008.5.1.4.1.1.1.1': 'X-Ray',
        '1.2.840.10008.5.1.4.1.1.1.1.1': 'X-Ray',
        '1.2.840.10008.5.1.4.1.1.1.2': 'Mammo',
        '1.2.840.10008.5.1.4.1.1.1.2.1': 'Mammo',
        '1.2.840.10008.5.1.4.1.1.1.3': 'Oral',
        '1.2.840.10008.5.1.4.1.1.1.3.1': 'Oral',
        '1.2.840.10008.5.1.4.1.1.10': 'LUT',
        '1.2.840.10008.5.1.4.1.1.104.1': 'PDF',
        '1.2.840.10008.5.1.4.1.1.11': 'VOI LUT',
        '1.2.840.10008.5.1.4.1.1.12.1': 'Angio',
        '1.2.840.10008.5.1.4.1.1.12.1.1': 'XA',
        '1.2.840.10008.5.1.4.1.1.12.2': 'Fluoro',
        '1.2.840.10008.5.1.4.1.1.12.2.1': 'XRF',
        '1.2.840.10008.5.1.4.1.1.12.3': 'Angio',
        '1.2.840.10008.5.1.4.1.1.128': 'PET',
        '1.2.840.10008.5.1.4.1.1.129': 'PET',
        '1.2.840.10008.5.1.4.1.1.2': 'CT',
        '1.2.840.10008.5.1.4.1.1.2.1': 'CT',
        '1.2.840.10008.5.1.4.1.1.20': 'NM',
        '1.2.840.10008.5.1.4.1.1.3': 'US',
        '1.2.840.10008.5.1.4.1.1.3.1': 'US',
        '1.2.840.10008.5.1.4.1.1.4': 'MR',
        '1.2.840.10008.5.1.4.1.1.4.1': 'MR',
        '1.2.840.10008.5.1.4.1.1.4.2': 'MRColor',
        '1.2.840.10008.5.1.4.1.1.4.3': 'MRColor',
        '1.2.840.10008.5.1.4.1.1.481.1': 'RTIMAGE',
        '1.2.840.10008.5.1.4.1.1.481.2': 'RTDose',
        '1.2.840.10008.5.1.4.1.1.481.3': 'RTSS',
        '1.2.840.10008.5.1.4.1.1.481.4': 'RTBeam',
        '1.2.840.10008.5.1.4.1.1.481.5': 'RTPlan',
        '1.2.840.10008.5.1.4.1.1.481.6': 'Brachy',
        '1.2.840.10008.5.1.4.1.1.481.7': 'RTSUMMARY',
        '1.2.840.10008.5.1.4.1.1.481.8': 'RTIonPlan',
        '1.2.840.10008.5.1.4.1.1.481.9': 'RTIonBeam',
        '1.2.840.10008.5.1.4.1.1.5': 'NM',
        '1.2.840.10008.5.1.4.1.1.6': 'US',
        '1.2.840.10008.5.1.4.1.1.6.1': 'US',
        '1.2.840.10008.5.1.4.1.1.66': 'RAW',
        '1.2.840.10008.5.1.4.1.1.66.1': 'Registration',
        '1.2.840.10008.5.1.4.1.1.66.2': 'Fiducial',
        '1.2.840.10008.5.1.4.1.1.66.3': 'Registration',
        '1.2.840.10008.5.1.4.1.1.66.4': 'Segmentation',
        '1.2.840.10008.5.1.4.1.1.7': 'SC',
        '1.2.840.10008.5.1.4.1.1.7.1': 'SC',
        '1.2.840.10008.5.1.4.1.1.7.2': 'SC',
        '1.2.840.10008.5.1.4.1.1.7.3': 'SC',
        '1.2.840.10008.5.1.4.1.1.7.4': 'SC',
    }
    return dic.get(uid, 'NOT DEFINED')

class DCMInstance(QObject):
    def __init__(self, ds, fp):
        super(DCMInstance, self).__init__()
        self.__ds = ds
        self.__fp = fp

    def GetFilePath(self):
        return self.__fp

    def GetDataset(self) -> pydicom.Dataset:
        return self.__ds

    def GetSOPInstanceUID(self):
        return self.__ds.SOPInstanceUID

    def Clear(self):
        del self.__ds


class DCMNode(QObject):
    def __init__(self, ID):
        super(DCMNode, self).__init__()
        self.__collection = {}
        self.__ID = ID
        self.Representation = None
        self.SOPClass = None

    def GetCollection(self):
        return self.__collection

    def GetElement(self, ElementID, Representation=None):
        if ElementID in self.__collection:
            element = self.__collection[ElementID]
        else:
            element = DCMNode(ElementID)
            element.Representation = Representation
            self.__collection[ElementID] = element
        return element

    def Clear(self):
        for _, element in self.__collection.items():
            element.Clear()
        self.__collection.clear()


class DCMGroup(QObject):
    progressed = pyqtSignal(float, int, int)
    parsingFinished = pyqtSignal()
    def __init__(self):
        super(DCMGroup, self).__init__()
        self.__patients = DCMNode(None)

    def GetTopNode(self):
        return self.__patients

    def __readFile(self, fp):
        try:
            ds = pydicom.read_file(fp, force=True)
            ds.ensure_file_meta()
            ds.fix_meta_info()
        except:
            return
        seriesDate = GetSeriesDate(ds)
        seriesTime = GetSeriesTime(ds)
        studyDate = GetStudyDate(ds)
        studyDescription = ds.StudyDescription if hasattr(ds, 'StudyDescription') and ds.StudyDescription else 'N/A'
        seriesDescription = ds.SeriesDescription if hasattr(ds, 'SeriesDescription') and ds.SeriesDescription else 'N/A'
        sopClass = uid_to_name(ds.SOPClassUID)

        dcmInstance = DCMInstance(ds, fp)
        patient = self.__patients.GetElement(ds.PatientID, f"{ds.PatientName} ({ds.PatientID})")

        study = patient.GetElement(ds.StudyInstanceUID, f"{studyDescription} ({studyDate})")
        series = study.GetElement(ds.SeriesInstanceUID, f"{seriesDescription} ({seriesDate} {seriesTime})")
        series.SOPClass = sopClass
        if not dcmInstance.GetSOPInstanceUID() in series.GetCollection():
            series.GetCollection()[dcmInstance.GetSOPInstanceUID()] = dcmInstance

    def SetRootDirectory(self, directoryPath):
        self.__patients.Clear()
        fps = [os.path.join(root, file) for root, subdirs, files in os.walk(directoryPath) for file in files]
        length = len(fps)
        for i, fp in enumerate(fps):
            self.__readFile(fp)
            self.progressed.emit((i + 1) / length, i + 1, length)
        self.parsingFinished.emit()

#
# class Test(QObject):
#     def __init__(self):
#         super(Test, self).__init__()
#         self.__dcmGroup = DCMGroup()
#         self.__dcmGroup.progressed.connect(self.__printProgress)
#         self.__dcmGroup.parsingFinished.connect(self.__printFinish)
#
#     def __printProgress(self, progress, processed, length):
#         print(progress, processed, length)
#
#     def __printFinish(self):
#         print('FINISHED')
#
#     def run(self):
#         self.__dcmGroup.SetRootDirectory(r'C:\Users\MSG\Desktop\test')

#
#
# for patientID, patient in dcmGroup.GetTopNode().GetCollection().items():
#     print(patientID)
#     for studyID, study in patient.GetCollection().items():
#         print('\t', studyID)
#         for seriesID, series in study.GetCollection().items():
#             print('\t\t', seriesID)
#             for instanceID, instance in series.GetCollection().items():
#                 print('\t\t\t', instanceID)
