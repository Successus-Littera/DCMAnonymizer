from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeWidget(QTreeWidget):
    def __init__(self, parent, dcmGroup):
        super(TreeWidget, self).__init__(parent)
        self.__dcmGroup = dcmGroup
        self.__dcmGroup.parsingFinished.connect(self.UpdateTree)
        self.header().setVisible(False)
        # self.setSelectionMode(self.ExtendedSelection)
        # self.setSelectionBehavior(self.SelectRows)

    def UpdateTree(self):
        self.clear()
        for patientID, patient in self.__dcmGroup.GetTopNode().GetCollection().items():
            patientNode = QTreeWidgetItem()
            patientNode.setText(0, patient.Representation)
            for studyID, study in patient.GetCollection().items():
                studyNode = QTreeWidgetItem()
                studyNode.setText(0, study.Representation)
                patientNode.addChild(studyNode)
                for seriesID, series in study.GetCollection().items():
                    seriesNode = QTreeWidgetItem()
                    seriesNode.setText(0, f"{series.SOPClass} : {series.Representation} ({len(series.GetCollection())})")
                    studyNode.addChild(seriesNode)
            self.addTopLevelItem(patientNode)
        self.expandAll()