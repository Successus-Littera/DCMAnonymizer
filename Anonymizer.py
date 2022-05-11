import os
import csv

from PyQt5.QtCore import pyqtSignal, QThread
import pydicom
import uuid
from DCMReader import DCMGroup, uid_to_name

# base = r'E:\dicom_parsed\NONCON_ABD'
# base = 'D:/dicom_parsed/HUTOM_TEST_30'
# DEST = r'E:\dicom_parsed\NONCON_ABD_ANONY'
# DEST = 'D:/dicom_parsed/HUTOM_ANONY_TEST_30'
# PID = 1
# prefix = 'NCABD_P'
# workbook = openpyxl.open('NONCON_ABD_MATCHING_TABLE.xlsx')
# worksheet = workbook.worksheets[0]
# mapper = {}
# for row in worksheet.rows:
#     values = [column.internal_value for column in row]
#     mapper[str(values[0])] = str(values[1])

class Anonymizer(QThread):
    progressed = pyqtSignal(float, int, int)
    finished = pyqtSignal()
    def __init__(self, parent, dcmGroup:DCMGroup, destinationDirectory, distinctionRule, prefix, startNumber, numberOfDigits, anonymizeOption):
        super(Anonymizer, self).__init__(parent)
        self.dcmGroup = dcmGroup
        self.destinationDirectory = destinationDirectory
        self.distinctionRule = distinctionRule
        self.prefix = prefix
        self.startNumber = startNumber
        self.numberOfDigits = numberOfDigits
        self.anonymizeOption = anonymizeOption

        self.anonyStudyID = {}
        self.anonySeriesID = {}
        self.anonyFrameID = {}
        self.anonySOPID = {}
        if self.anonymizeOption.FrameUID or self.anonymizeOption.SOPUID or self.anonymizeOption.StudyUID or self.anonymizeOption.SeriesUID:
            for patientID, patient in self.dcmGroup.GetTopNode().GetCollection().items():
                for studyID, study in patient.GetCollection().items():
                    for seriesID, series in study.GetCollection().items():
                        for sopID, sop in series.GetCollection().items():
                            ds = sop.GetDataset()
                            if studyID not in self.anonyStudyID:
                                self.anonyStudyID[studyID] = str(uuid.uuid4())
                            if seriesID not in self.anonySeriesID:
                                self.anonySeriesID[seriesID] = str(uuid.uuid4())
                            try:
                                frameID = str(ds.FrameOfReferenceUID)
                            except:
                                frameID = str(ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID)
                            if frameID not in self.anonyFrameID:
                                self.anonyFrameID[frameID] = str(uuid.uuid4())
                            self.anonySOPID[sopID] = str(uuid.uuid4())

    def run(self):
        count = 1
        currentNumber = self.startNumber
        numberOfds = sum([len(series.GetCollection())
                          for patientID, patient in self.dcmGroup.GetTopNode().GetCollection().items()
                          for studyID, study in patient.GetCollection().items()
                          for seriesID, series in study.GetCollection().items()
                         ])
        fh = open(os.path.join(self.destinationDirectory, 'matching_table.csv'), 'w', newline='')
        writer = csv.writer(fh)
        if self.distinctionRule == "PATIENT":
            writer.writerow(['NO', 'NEW_PATIENT_ID', 'OLD_PATIENT_ID'])
            for patientID, patient in self.dcmGroup.GetTopNode().GetCollection().items():
                fps = [sop.GetFilePath()
                       for study in patient.GetCollection().values()
                       for series in study.GetCollection().values()
                       for sop in series.GetCollection().values()]
                for fp in fps:
                    self.AnonymizeDataset(fp, self.__buildNewID(currentNumber))
                    self.progressed.emit(count / numberOfds, count, numberOfds)
                    count += 1
                writer.writerow([currentNumber, self.__buildNewID(currentNumber), patientID])
                currentNumber += 1
        elif self.distinctionRule == "STUDY":
            writer.writerow(['NO', 'NEW_PATIENT_ID', 'OLD_PATIENT_ID', 'STUDY_DESCRIPTION'])
            for patientID, patient in self.dcmGroup.GetTopNode().GetCollection().items():
                for studyID, study in patient.GetCollection().items():
                    fps = [sop.GetFilePath()
                           for series in study.GetCollection().values()
                           for sop in series.GetCollection().values()]
                    for fp in fps:
                        self.AnonymizeDataset(fp, self.__buildNewID(currentNumber))
                        self.progressed.emit(count / numberOfds, count, numberOfds)
                        count += 1
                    writer.writerow([currentNumber, self.__buildNewID(currentNumber), patientID, study.Representation])
                    currentNumber += 1
        elif self.distinctionRule == "SERIES":
            writer.writerow(['NO', 'NEW_PATIENT_ID', 'OLD_PATIENT_ID', 'STUDY_DESCRIPTION', 'SERIES_DESCRIPTION'])
            for patientID, patient in self.dcmGroup.GetTopNode().GetCollection().items():
                for studyID, study in patient.GetCollection().items():
                    for seriesID, series in study.GetCollection().items():
                        fps = [sop.GetFilePath() for sop in series.GetCollection().values()]
                        for fp in fps:
                            self.AnonymizeDataset(fp, self.__buildNewID(currentNumber))
                            self.progressed.emit(count / numberOfds, count, numberOfds)
                            count += 1
                        writer.writerow(
                            [currentNumber, self.__buildNewID(currentNumber), patientID, study.Representation, series.Representation])
                        currentNumber += 1
        fh.close()
        self.finished.emit()

    def __buildNewID(self, currentNumber):
        current_number_str = str(currentNumber)
        length_zeros = self.numberOfDigits - len(current_number_str)
        numbering = ("0" * length_zeros) + current_number_str
        if self.prefix != '':
            newID = f"{self.prefix}_{numbering}"
        else:
            newID = numbering
        return newID

    def AnonymizeDataset(self, fp, newID):
        ds = pydicom.read_file(fp, force=True)
        ds.ensure_file_meta()
        ds.fix_meta_info()

        newStudyID = self.anonyStudyID[str(ds.StudyInstanceUID)]
        newSeriesID = self.anonySeriesID[(str(ds.SeriesInstanceUID))]
        newInstanceID = self.anonySOPID[str(ds.SOPInstanceUID)]

        if self.anonymizeOption.PatientID:
            ds.PatientID = newID
        if self.anonymizeOption.PatientName:
            ds.PatientName = newID
        if self.anonymizeOption.StudyUID:
            ds.StudyInstanceUID = str(newStudyID)
        if self.anonymizeOption.SeriesUID:
            ds.SeriesInstanceUID = str(newSeriesID)
        if self.anonymizeOption.SOPUID:
            ds.SOPInstanceUID = str(newInstanceID)

        ds.file_meta.MediaStorageSOPInstanceUID = str(newInstanceID)
        if self.anonymizeOption.InstitutionName:
            ds.InstitutionName = self.anonymizeOption.InstitutionName_value
        if self.anonymizeOption.PhysicianName:
            ds.ReferringPhysicianName = self.anonymizeOption.PhysicianName_value
        # ds.StudyDate = "20220406"
        # ds.SeriesDate = "20220406"
        if self.anonymizeOption.AccessionNumber:
            ds.AccessionNumber = self.anonymizeOption.AccessionNumber_value

        if ds.SOPClassUID == "1.2.840.10008.5.1.4.1.1.481.3":
            for rfrs in ds.ReferencedFrameOfReferenceSequence:
                if self.anonymizeOption.FrameUID:
                    rfrs.FrameOfReferenceUID = str(self.anonyFrameID[str(rfrs.FrameOfReferenceUID)])
                rtrss = rfrs.RTReferencedStudySequence
                for s in rtrss:
                    if self.anonymizeOption.StudyUID:
                        s.ReferencedSOPInstanceUID = str(self.anonyStudyID[str(s.ReferencedSOPInstanceUID)])
                    for rs in s.RTReferencedSeriesSequence:
                        if self.anonymizeOption.SeriesUID:
                            rs.SeriesInstanceUID = str(self.anonySeriesID[str(rs.SeriesInstanceUID)])
                        for cis in rs.ContourImageSequence:
                            if self.anonymizeOption.SOPUID:
                                cis.ReferencedSOPInstanceUID = str(
                                    self.anonySOPID[str(cis.ReferencedSOPInstanceUID)])
            if self.anonymizeOption.FrameUID:
                for ssrs in ds.StructureSetROISequence:
                    ssrs.ReferencedFrameOfReferenceUID = str(
                        self.anonyFrameID[str(ssrs.ReferencedFrameOfReferenceUID)])
            if self.anonymizeOption.SOPUID:
                for rcs in ds.ROIContourSequence:
                    for cs in rcs.ContourSequence:
                        for cis in cs.ContourImageSequence:
                            cis.ReferencedSOPInstanceUID = str(self.anonySOPID[cis.ReferencedSOPInstanceUID])

            destDirPath = f"{self.destinationDirectory}/{newID}"
            destination = os.path.join(destDirPath, uid_to_name(ds.SOPClassUID))
            if not os.path.exists(destination):
                os.makedirs(destination, exist_ok=True)
            ds.save_as(os.path.join(destination, str(newInstanceID) + ".dcm"))
        else:
            if self.anonymizeOption.FrameUID:
                newFrameUID = str(self.anonyFrameID[str(ds.FrameOfReferenceUID)])
                ds.FrameOfReferenceUID = newFrameUID
            destDirPath = f"{self.destinationDirectory}/{newID}"
            destination = os.path.join(destDirPath, uid_to_name(ds.SOPClassUID))
            if not os.path.exists(destination):
                os.makedirs(destination, exist_ok=True)
            ds.save_as(os.path.join(destination, str(newInstanceID) + ".dcm"))
