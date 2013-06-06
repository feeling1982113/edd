import sys
import functools

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from edd.core.econtroller import EController
from edd.gui.eview import EView

from edd.gui.utils.ehighlighter import EHighlighter
from edd.gui.editors.econsole import EConsole


class EWidget(QSplitter):

    Message = pyqtSignal()

    def __init__(self):
        QSplitter.__init__(self, Qt.Vertical)

        self.__view = EView(EController())

        self.__console = EConsole()
        EHighlighter(self.__console.document(), ['cwd'], ['createNode',
                                                          'getNode',
                                                          'deleteNode',
                                                          'connectAttr',
                                                          'getTransform',
                                                          'setPos',
                                                          'NodeTypes'])

        self.__console.updateNamespace({'cwd': self.__view.Controller,
                                        'history': self.__console.getHistory})

        self.addWidget(self.__view)
        self.addWidget(self.__console)

    @property
    def View(self):
        return self.__view

    @property
    def Console(self):
        return self.__console

    def processMenuItem(self, data):
        print '...Data from menu: < %s >' % data

    def contextMenuEvent(self, mouseEvent):
        menu = QMenu()

        action_1 = QAction("Create Node A", menu, triggered=functools.partial(self.processMenuItem, 'MyNodeOne'))
        action_2 = QAction("Create Node B", menu, triggered=functools.partial(self.processMenuItem, 'MyNodeTwo'))

        menu.addAction(action_1)
        menu.addAction(action_2)

        menu.exec_(QCursor.pos())


if __name__ == '__main__':
    import os

    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create("plastique"))

    sheetContent = open(os.path.join(os.getcwd(), 'resources/edd.stylesheet'), 'r').read()
    app.setStyleSheet(sheetContent)

    mainWin = QMainWindow()
    mainWin.setCentralWidget(EWidget())
    mainWin.show()
    sys.exit(app.exec_())