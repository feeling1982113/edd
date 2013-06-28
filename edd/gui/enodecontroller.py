from PyQt4 import QtGui
from edd.core.eattribute import EAttribute


class ENodeController(QtGui.QVBoxLayout):

    def __init__(self, nodeHandle):
        QtGui.QVBoxLayout.__init__(self)

        self.setContentsMargins(1, 1, 1, 1)

        self.__nodeHandle = nodeHandle

        return

    def addVector2d(self, valueV, valueU):
        #self.addPropertyAttribute(EAttribute.kTypeVector2d, name, [valueV, valueU])
        return

    def addVector3d(self, name, valueX, valueY, valueZ):
        #self.addPropertyAttribute(EAttribute.kTypeVector3d, name, [valueX, valueY, valueZ])
        return