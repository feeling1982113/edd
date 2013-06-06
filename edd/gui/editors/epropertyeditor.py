from PyQt4.QtCore import *
from PyQt4.QtGui import *
from edd.core.eattribute import EAttribute


class EPropertyEditor(QTabWidget):

    def __init__(self, controller):
        QTabWidget.__init__(self)

        self.__scene = controller.getScene()

        self.__scene.onSelectionChanged.connect(self.rebuild)

    def __processLineEdit(self):
        self.__controller.Handle.updateAttribute(self.sender().kInternalId, self.sender().text())

    def rebuild(self, data):

        self.clear()

        grid = QGridLayout()
        grid.setContentsMargins(1, 1, 1, 1)
        grid.addWidget(self.__createControls(data.nodeName, data.nodeProperties), 0, 0)

        paramWidget = QWidget()
        paramWidget.setLayout(grid)

        self.addTab(paramWidget, 'Parameters')

        return

    def __getControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(0, 0, 0, 0)

        lineEdit = QLineEdit('%s' % prop.Data)
        # TODO: Add internal data (Need interface :))
        lineEdit.kInternalId = prop.Id
        lineEdit.editingFinished.connect(self.__processLineEdit)

        propLayout.addWidget(lineEdit, 0, 0)
        propLayout.addWidget(QSlider(Qt.Horizontal), 1, 0)

        theLayout.setLayout(propLayout)

        return theLayout

    def __getVectorControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)
        theLayout.setContentsMargins(1, 1, 1, 1)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(1, 1, 1, 1)

        for index, propItem in enumerate(prop.Data):
            lineEdit = QLineEdit()
            #lineEdit.setAlignment(Qt.AlignRight)

            lineEdit.setText("%s" % propItem.Data)
            lineEdit.kInternalId = propItem.Id
            lineEdit.editingFinished.connect(self.__processLineEdit)
            propLayout.addWidget(lineEdit, 0, index)

        theLayout.setLayout(propLayout)

        return theLayout

    def __createControls(self, nodeName, nodeProperties):

        groupBox = QGroupBox(" %s " % nodeName)
        groupBox.setContentsMargins(1, 1, 1, 1)
        groupBox.setAlignment(Qt.AlignCenter)

        theLayout = QVBoxLayout()
        theLayout.setContentsMargins(1, 1, 1, 1)

        for prop in nodeProperties:
            if prop.Type.matches(EAttribute.kTypeList):
                theLayout.addWidget(self.__getVectorControl(prop))
                continue

            theLayout.addWidget(self.__getControl(prop))

        #theLayout.addWidget(QSlider())
        theLayout.addStretch(0)
        groupBox.setLayout(theLayout)

        return groupBox