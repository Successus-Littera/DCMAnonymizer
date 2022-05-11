from PyQt5.QtWidgets import *
from DCMReader import DCMGroup


class AnonymizeOption:
    def __init__(self):
        self.PatientName = True
        self.PatientID = True
        self.Gender = True
        self.Age = True
        self.StudyUID = True
        self.SeriesUID = True
        self.SOPUID = True
        self.FrameUID = True
        self.InstitutionName = True
        self.PhysicianName = True
        self.AccessionNumber = True

        self.InstitutionName_value = ''
        self.PhysicianName_value = ''
        self.AccessionNumber_value = ''


def GetReadonlyLineEdit():
    le = QLineEdit()
    le.setReadOnly(True)
    return le


def GetCheckedCheckbox(label):
    cb = QCheckBox(label)
    cb.setChecked(True)
    return cb


class EditForm(QWidget):
    def __init__(self, parent, dcmGroup:DCMGroup):
        super(EditForm, self).__init__(parent)
        self.__dcmGroup = dcmGroup
        self.__layout = QVBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)

        # self.__selection = QGroupBox('Selection')
        self.__distinction = QGroupBox('Distinction')
        self.__namingRule = QGroupBox('Naming Rule')
        self.__anonymizeOption = QGroupBox('Anonymize Option')

        # self.__selection_all = QRadioButton('All')
        # self.__selection_selected = QRadioButton('Selected')

        self.__distinction_patient = QRadioButton('Patient')
        self.__distinction_study = QRadioButton('Study')
        self.__distinction_series = QRadioButton('Series')

        self.__namingRule_prefix = QLineEdit()
        self.__namingRule_prefix.textChanged.connect(self.__buildName)
        self.__namingRule_startNumber = QSpinBox()
        self.__namingRule_startNumber.valueChanged.connect(self.__buildName)
        self.__namingRule_numberOfDigit = QSpinBox()
        self.__namingRule_numberOfDigit.valueChanged.connect(self.__buildName)

        self.__anonymizeOption_patientName = GetCheckedCheckbox("Patient's Name")
        self.__anonymizeOption_patientName_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_patientID = GetCheckedCheckbox("Patient's ID (MRN)")
        self.__anonymizeOption_patientID_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_gender = QCheckBox("Patient's Gender")
        self.__anonymizeOption_gender_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_age = QCheckBox("Patient's Age")
        self.__anonymizeOption_age_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_studyInstanceUID = GetCheckedCheckbox("Study UID")
        self.__anonymizeOption_studyInstanceUID_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_seriesInstanceUID = GetCheckedCheckbox('Series UID')
        self.__anonymizeOption_seriesInstanceUID_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_sopInstanceUID = GetCheckedCheckbox('SOP UID')
        self.__anonymizeOption_sopInstanceUID_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_frameOfReferenceUID = GetCheckedCheckbox('Frame UID')
        self.__anonymizeOption_frameOfReferenceUID_preview = GetReadonlyLineEdit()
        self.__anonymizeOption_institutionName = QCheckBox('Institution Name')
        self.__anonymizeOption_institutionName_preview = QLineEdit()
        self.__anonymizeOption_referringPhysicianName = GetCheckedCheckbox('Physician Name')
        self.__anonymizeOption_referringPhysicianName_preview = QLineEdit()
        self.__anonymizeOption_accessionNumber = GetCheckedCheckbox('Accession Number')
        self.__anonymizeOption_accessionNumber_preview = QLineEdit()

        self.__anonymizeOption_patientName.clicked.connect(self.__anonymizeOption_patientName_preview.setEnabled)
        self.__anonymizeOption_patientID.clicked.connect(self.__anonymizeOption_patientID_preview.setEnabled)
        self.__anonymizeOption_gender.clicked.connect(self.__anonymizeOption_gender_preview.setEnabled)
        self.__anonymizeOption_age.clicked.connect(self.__anonymizeOption_age_preview.setEnabled)
        self.__anonymizeOption_studyInstanceUID.clicked.connect(self.__anonymizeOption_studyInstanceUID_preview.setEnabled)
        self.__anonymizeOption_seriesInstanceUID.clicked.connect(self.__anonymizeOption_seriesInstanceUID_preview.setEnabled)
        self.__anonymizeOption_sopInstanceUID.clicked.connect(self.__anonymizeOption_sopInstanceUID_preview.setEnabled)
        self.__anonymizeOption_frameOfReferenceUID.clicked.connect(self.__anonymizeOption_frameOfReferenceUID_preview.setEnabled)
        self.__anonymizeOption_institutionName.clicked.connect(self.__anonymizeOption_institutionName_preview.setEnabled)
        self.__anonymizeOption_referringPhysicianName.clicked.connect(self.__anonymizeOption_referringPhysicianName_preview.setEnabled)
        self.__anonymizeOption_accessionNumber.clicked.connect(self.__anonymizeOption_accessionNumber_preview.setEnabled)

        # self.__selectionLayout = QHBoxLayout(self.__selection)
        # self.__selectionLayout.addWidget(self.__selection_all)
        # self.__selectionLayout.addWidget(self.__selection_selected)

        self.__distinctionLayout = QHBoxLayout(self.__distinction)
        self.__distinctionLayout.addWidget(self.__distinction_patient)
        self.__distinctionLayout.addWidget(self.__distinction_study)
        self.__distinctionLayout.addWidget(self.__distinction_series)

        self.__namingRuleLayout = QGridLayout(self.__namingRule)
        self.__namingRuleLayout.addWidget(QLabel('Prefix'), 0, 0)
        self.__namingRuleLayout.addWidget(self.__namingRule_prefix, 0, 1)
        self.__namingRuleLayout.addWidget(QLabel('Start Number'), 1, 0)
        self.__namingRuleLayout.addWidget(self.__namingRule_startNumber, 1, 1)
        self.__namingRuleLayout.addWidget(QLabel('Number Of Digits'), 2, 0)
        self.__namingRuleLayout.addWidget(self.__namingRule_numberOfDigit, 2, 1)

        self.__anonymizeOptionLayout = QGridLayout(self.__anonymizeOption)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_patientName, 0, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_patientName_preview, 0, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_patientID, 1, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_patientID_preview, 1, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_gender, 2, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_gender_preview, 2, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_age, 3, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_age_preview, 3, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_studyInstanceUID, 4, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_studyInstanceUID_preview, 4, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_seriesInstanceUID, 5, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_seriesInstanceUID_preview, 5, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_sopInstanceUID, 6, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_sopInstanceUID_preview, 6, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_frameOfReferenceUID, 7, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_frameOfReferenceUID_preview, 7, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_institutionName, 8, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_institutionName_preview, 8, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_referringPhysicianName, 9, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_referringPhysicianName_preview, 9, 1)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_accessionNumber, 10, 0)
        self.__anonymizeOptionLayout.addWidget(self.__anonymizeOption_accessionNumber_preview, 10, 1)

        # self.__layout.addWidget(self.__selection)
        self.__layout.addWidget(self.__distinction)
        self.__layout.addWidget(self.__namingRule)
        self.__layout.addWidget(self.__anonymizeOption)

        # self.__selection_all.setChecked(True)
        self.__distinction_study.setChecked(True)
        
        self.__namingRule_startNumber.setValue(1)
        self.__namingRule_numberOfDigit.setValue(4)
        self.__anonymizeOption_studyInstanceUID_preview.setText('Auto Generated UUID.')
        self.__anonymizeOption_seriesInstanceUID_preview.setText('Auto Generated UUID.')
        self.__anonymizeOption_sopInstanceUID_preview.setText('Auto Generated UUID.')
        self.__anonymizeOption_frameOfReferenceUID_preview.setText('Auto Generated UUID.')

        self.__anonymizeOption_gender_preview.setEnabled(False)
        self.__anonymizeOption_age_preview.setEnabled(False)
        self.__anonymizeOption_institutionName_preview.setEnabled(False)

    def GetDistinctionRule(self):
        if self.__distinction_patient.isChecked():
            return "PATIENT"
        elif self.__distinction_study.isChecked():
            return "STUDY"
        elif self.__distinction_series.isChecked():
            return "SERIES"

    def GetNamingRule(self):
        return self.__namingRule_prefix.text(), self.__namingRule_startNumber.value(), self.__namingRule_numberOfDigit.value()

    def GetAnonymizeOption(self):
        option = AnonymizeOption()
        option.PatientName = self.__anonymizeOption_patientName.isChecked()
        option.PatientID = self.__anonymizeOption_patientID.isChecked()
        option.Gender = self.__anonymizeOption_gender.isChecked()
        option.Age = self.__anonymizeOption_age.isChecked()
        option.StudyUID = self.__anonymizeOption_studyInstanceUID.isChecked()
        option.SeriesUID = self.__anonymizeOption_seriesInstanceUID.isChecked()
        option.SOPUID = self.__anonymizeOption_sopInstanceUID.isChecked()
        option.FrameUID = self.__anonymizeOption_frameOfReferenceUID.isChecked()
        option.InstitutionName = self.__anonymizeOption_institutionName.text()
        option.InstitutionName_value = self.__anonymizeOption_institutionName_preview.text()
        option.PhysicianName = self.__anonymizeOption_referringPhysicianName.isChecked()
        option.PhysicianName_value = self.__anonymizeOption_referringPhysicianName_preview.text()
        option.AccessionNumber = self.__anonymizeOption_accessionNumber.isChecked()
        option.AccessionNumber_value = self.__anonymizeOption_accessionNumber_preview.text()
        return option

    def NumberOfNecessaryUniqueID(self):
        if self.__distinction_patient.isChecked():
            return len(self.__dcmGroup.GetTopNode().GetCollection())
        elif self.__distinction_study.isChecked():
            return sum([len(patient.GetCollection()) for patientID, patient in self.__dcmGroup.GetTopNode().GetCollection().items()])
        elif self.__distinction_series.isChecked():
            return sum([len(study.GetCollection())
                        for patientID, patient in self.__dcmGroup.GetTopNode().GetCollection().items()
                        for studyID, study in patient.GetCollection().items()
                        ])

    def __buildName(self):
        prefix = self.__namingRule_prefix.text()
        start_number_str = str(self.__namingRule_startNumber.value())
        end_number_str = str(self.__namingRule_startNumber.value() + self.NumberOfNecessaryUniqueID() - 1)
        if len(end_number_str) > self.__namingRule_numberOfDigit.value():
            self.__namingRule_numberOfDigit.setValue(len(end_number_str))
        length_zeros = self.__namingRule_numberOfDigit.value() - len(start_number_str)
        number_preview = ("0" * length_zeros) + start_number_str
        if prefix != '':
            anony_id = f'{prefix}_{number_preview}'
        else:
            anony_id = number_preview

        self.__anonymizeOption_patientName_preview.setText(anony_id)
        self.__anonymizeOption_patientID_preview.setText(anony_id)