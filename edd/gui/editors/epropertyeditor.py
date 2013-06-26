import functools
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from edd.core.eattribute import EAttribute


class EPropertyEditor(QTabWidget):

    def __init__(self, controller):
        QTabWidget.__init__(self)

        self.__controller = controller
        self.__scene = controller.getScene()

        self.__minValue = -100000000
        self.__maxValue = 100000000

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

    def __processSlider(self, propHandleId, propId, propData):
        pushData = self.sender().value() * 0.1

        node = self.__controller.getNode(propHandleId)
        node.setAttribute(node.getAttribute(propId), pushData)

    def __processLineEdit(self, propHandleId, propId, propData):

        self.sender().clearFocus()

        pushData = self.sender().text()

        if isinstance(self.sender().validator(), QDoubleValidator):
            pushData = float(self.sender().text())

        if isinstance(self.sender().validator(), QIntValidator):
            pushData = int(self.sender().text())

        node = self.__controller.getNode(propHandleId)
        node.setAttribute(node.getAttribute(propId), pushData)

        self.sender().setText(str(pushData))

    def __setValidator(self, control, prop):

        if prop.Type.matches(EAttribute.kTypeInt):
            control.setValidator(QIntValidator(self.__minValue, self.__maxValue, self))

        if prop.Type.matches(EAttribute.kTypeFloat):
            control.setValidator(QDoubleValidator(self.__minValue, self.__maxValue, 4, self))

    def __getControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(0, 0, 0, 0)

        lineEdit = QLineEdit('%s' % prop.Data)
        self.__setValidator(lineEdit, prop)

        lineEdit.returnPressed.connect(functools.partial(self.__processLineEdit, prop.Handle.Id, prop.Id, prop.Data))

        propLayout.addWidget(lineEdit, 0, 0)

        theLayout.setLayout(propLayout)

        return theLayout

    def __updateAttrGroup(self, groupItem):
        if isinstance(self.sender(), QLineEdit):
            self.sender().clearFocus()
            pushData = float(self.sender().text()) * 10
            groupItem.setValue(pushData)
            self.sender().setText(str(pushData * 0.1))
            return

        groupItem.setText(str(self.sender().value() * 0.1))

    def __getListControl(self, prop):

        theLayout = QGroupBox('Items')
        theLayout.setContentsMargins(1, 1, 1, 1)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(1, 1, 1, 1)

        for index, item in enumerate(prop.Data):
            lineEdit = QLineEdit()
            lineEdit.setText("%s" % item.Name)
            #self.__setValidator(lineEdit, propItem)
            #lineEdit.returnPressed.connect(functools.partial(self.__processLineEdit, propItem.Handle.Id,
            #                                                 propItem.Id, propItem.Data))
            propLayout.addWidget(lineEdit, index, 0)

        theLayout.setLayout(propLayout)
        return theLayout

    def __getVectorControl(self, prop):

        theLayout = QGroupBox('%s' % prop.Name)
        theLayout.setContentsMargins(1, 1, 1, 1)

        propLayout = QGridLayout()
        propLayout.setContentsMargins(1, 1, 1, 1)

        for index, propItem in enumerate(prop.Data):
            slider = QSlider(Qt.Horizontal)

            if propItem.getMinValue() is not None and propItem.getMaxValue() is not None:
                slider.setRange(propItem.getMinValue() * 10, propItem.getMaxValue() * 10)
            else:
                slider.setRange(-100.0 * 10, 100.0 * 10)

            slider.setSingleStep(10)

            slider.setValue(propItem.Data * 10)

            slider.valueChanged.connect(functools.partial(self.__processSlider, propItem.Handle.Id,
                                                          propItem.Id, propItem.Data))

            lineEdit = QLineEdit()
            lineEdit.setFixedWidth(60)
            lineEdit.setText("%s" % propItem.Data)
            self.__setValidator(lineEdit, propItem)

            lineEdit.returnPressed.connect(functools.partial(self.__updateAttrGroup, slider))
            slider.valueChanged.connect(functools.partial(self.__updateAttrGroup, lineEdit))

            propLayout.addWidget(QLabel(' X:'), index, 0)
            propLayout.addWidget(slider, index, 1)
            propLayout.addWidget(lineEdit, index, 2)

        theLayout.setLayout(propLayout)

        return theLayout

    def __createControls(self, nodeName, nodeProperties):

        groupBox = QGroupBox(" %s " % nodeName)
        groupBox.setContentsMargins(1, 1, 1, 1)
        groupBox.setAlignment(Qt.AlignCenter)

        theLayout = QVBoxLayout()
        theLayout.setContentsMargins(1, 1, 1, 1)

        for prop in nodeProperties:
            if any([prop.Type.matches(EAttribute.kTypeVector3d),
                    prop.Type.matches(EAttribute.kTypeVector2d)]):

                theLayout.addWidget(self.__getVectorControl(prop))
                continue

            if prop.Type.matches(EAttribute.kTypeList):
                theLayout.addWidget(self.__getListControl(prop))
                continue

            theLayout.addWidget(self.__getControl(prop))

        theLayout.addStretch(0)
        groupBox.setLayout(theLayout)

        return groupBox