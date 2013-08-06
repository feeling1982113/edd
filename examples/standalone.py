import os
import sys
import functools

sys.path.append(os.getcwd().replace("examples", ''))

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from edd.core.eattribute import EAttribute
from edd.core.enodehandle import ENodeHandle

from edd.ewidget import EWidget
from edd.gui.editors.epropertyeditor import EPropertyEditor


class MyCollection(ENodeHandle):
    def __init__(self):
        ENodeHandle.__init__(self)

        self.IsContainer = True

        self.addPropertyAttribute("Param 1", EAttribute.kTypeFloat, 10.0)
        self.addPropertyAttribute("Param 2", EAttribute.kTypeList, [10.0, 20.0, 30.0])
        self.addPropertyAttribute("Param 3", EAttribute.kTypeString, '<path_to_file>'.upper())

        self.__inputAttrA = self.addInputAttribute("InputA")
        self.__inputAttrB = self.addInputAttribute("InputB")
        self.__outputAttr = self.addOutputAttribute("Output")

    def compute(self):
        print self, 'computed...'


class MyNodeOne(ENodeHandle):
    def __init__(self):
        ENodeHandle.__init__(self)

        self.addPropertyAttribute("Param 1", EAttribute.kTypeFloat, 10.0)
        self.addPropertyAttribute("Param 2", EAttribute.kTypeVector2d, [10.0, 20.0])
        self.addPropertyAttribute("Param 3", EAttribute.kTypeVector3d, [10.0, 20.0, 30.0])
        self.addPropertyAttribute("Param 4", EAttribute.kTypeString, '<path_to_file>'.upper())

        self.__inputAttr = self.addInputAttribute("Input")
        self.__outputAttr = self.addOutputAttribute("Output")

    def compute(self):
        pass


class MyNodeTwo(ENodeHandle):
    def __init__(self):
        ENodeHandle.__init__(self)

        self.addPropertyAttribute("Param 1", EAttribute.kTypeFloat, 10.0)
        self.addPropertyAttribute("Param 2", EAttribute.kTypeVector3d, [10.0, 20.0])

        self.__inputAttrA = self.addInputAttribute("InputA")
        self.__inputAttrB = self.addInputAttribute("InputB")

        self.__outputAttrA = self.addOutputAttribute("OutputA")
        self.__outputAttrB = self.addOutputAttribute("OutputB")

    def compute(self):
        pass


class EWorkspace(EWidget):
    def __init__(self):
        EWidget.__init__(self)

        self.__nodes = {'MyNodeOne': MyNodeOne, 'MyNodeTwo': MyNodeTwo, 'MyPoint': MyCollection}

        for name, node in self.__nodes.iteritems():
            self.View.Controller.registerNode(name, node)

        return

    def createNode(self, nodeName):
        self.View.Controller.createNode(nodeName)

    def contextMenuEvent(self, mouseEvent):
        menu = QMenu()

        action_1 = QAction("Create Node A", menu, triggered=functools.partial(self.createNode, 'MyNodeOne'))
        action_2 = QAction("Create Node B", menu, triggered=functools.partial(self.createNode, 'MyNodeTwo'))
        action_3 = QAction("Create Point", menu, triggered=functools.partial(self.createNode, 'MyPoint'))

        menu.addAction(action_1)
        menu.addAction(action_2)
        menu.addSeparator()
        menu.addAction(action_3)

        menu.exec_(QCursor.pos())

    def mouseDoubleClickEvent(self, mouseEvent):
        self.dump()


class EMainWindow(QMainWindow):
    def __init__(self):
        super(EMainWindow, self).__init__()

        self.setWindowTitle('EDD - Standalone (Example)')

        kResourceTabs = QTabWidget()
        kResourceTabs.setObjectName('kMainTab')

        eddWidget = EWorkspace()

        kResourceTabs.addTab(eddWidget, "Node Graph")

        self.setCentralWidget(kResourceTabs)

        self.createMenus()

        self.createPropertyEditor(eddWidget.View.Controller)
        self.createLister()

    def foo(self):
        print 'foo'

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addSeparator()

        self.createMenu = self.menuBar().addMenu("&Create")
        nodeCreate = QAction("Create Node", self.createMenu, triggered=self.foo)
        self.createMenu.addAction(nodeCreate)

        self.createMenu = self.menuBar().addMenu("&View")

    def createPropertyEditor(self, controller):
        dock = QDockWidget("Properties", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)

        foo = EPropertyEditor(controller)

        scrollArea.setWidget(foo)
        scrollArea.setMinimumWidth(256)

        dock.setWidget(scrollArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createLister(self):

        dock = QDockWidget("Lister", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        lister = QTreeView()

        lister.setModel(QDirModel())

        dock.setWidget(lister)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)


if __name__ == '__main__':

    import edd.resources.resource_rc

    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create("plastique"))

    sheetContent = open('%s/edd.stylesheet' % str(os.getcwd()).replace("examples", 'edd/resources'), 'r').read()
    app.setStyleSheet(sheetContent)

    mainWin = EMainWindow()
    mainWin.show()
    sys.exit(app.exec_())
