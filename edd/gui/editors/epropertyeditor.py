import functools
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from edd.core.eattribute import EAttribute


class EPropertyEditor(QTabWidget):

    def __init__(self, controller):
        QTabWidget.__init__(self)

        self.__controller = controller
        self.__scene = controller.getScene()

        self.__scene.onSelectionChanged.connect(self.rebuild)

    def rebuild(self, data):

        self.clear()

        grid = QGridLayout()
        grid.setContentsMargins(1, 1, 1, 1)
        grid.addWidget(self.__createControls(data.nodeName, data.nodeProperties), 0, 0)

        paramWidget = QWidget()
        paramWidget.setLayout(grid)

        self.addTab(paramWidget, 'Parameters')

        return

    def __processLineEdit(self, propHandleId, propId, propData):
        print propData
        node = self.__controller.getNode(propHandleId)
        node.setAttribute(node.getAttribute(propId), self.sender().text())

    def __setValidator(self, control, prop):

        if prop.Type.matches(EAttribute.kTypeInt):
            control.setValidator(QIntValidator(0, 10000000, self))

        if prop.Type.matches(EAttribute.kTypeFloat):
            control.setValidator(QDoubleValidator(0, 100000000, 6, self))

    def __getControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(0, 0, 0, 0)

        lineEdit = QLineEdit('%s' % prop.Data)
        self.__setValidator(lineEdit, prop)

        lineEdit.editingFinished.connect(functools.partial(self.__processLineEdit, prop.Handle.Id,
                                                           prop.Id, prop.Data))

        propLayout.addWidget(lineEdit, 0, 0)
        #propLayout.addWidget(QSlider(Qt.Horizontal), 1, 0)

        theLayout.setLayout(propLayout)

        return theLayout

    def __getVectorControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)
        theLayout.setContentsMargins(1, 1, 1, 1)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(1, 1, 1, 1)

        for index, propItem in enumerate(prop.Data):
            lineEdit = QLineEdit()

            self.__setValidator(lineEdit, propItem)

            lineEdit.setText("%s" % propItem.Data)
            lineEdit.editingFinished.connect(functools.partial(self.__processLineEdit, propItem.Handle.Id,
                                                               propItem.Id, propItem.Data))
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