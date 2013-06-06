from PyQt4.QtCore import pyqtSignal, Qt, QRectF, QPoint
from PyQt4.QtGui import QPainter, QGraphicsView

from edd.gui.escene import EScene

class EView(QGraphicsView):

    onVisibleRectChanged = pyqtSignal(QRectF)

    def __init__(self, controller):
        QGraphicsView.__init__(self)

        self.setRenderHints( QPainter.Antialiasing  | QPainter.TextAntialiasing )
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)            
        
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )

        self.horizontalScrollBar().valueChanged.connect(self.viewScrollBarsValueChanged) 
        self.verticalScrollBar().valueChanged.connect(self.viewScrollBarsValueChanged)

        self.__controller = controller

        self.setScene(EScene(self, self.__controller))
        self.Scene.setSceneRect(QRectF(-10000, -10000, 20000, 20000))

        return

    @property
    def Controller(self):
        return self.__controller

    @property
    def Scene(self):
        return self.scene()

    @property
    def VisibleRect(self):
        invertedMatrix = self.matrix().inverted()
        visibleRect = invertedMatrix[0].mapRect(self.viewport().rect())           
        visibleRect.moveTopLeft( invertedMatrix[0].map( QPoint( self.horizontalScrollBar().value(), self.verticalScrollBar().value()  ) ) )
        visibleRect.setWidth( visibleRect.width()  )
        visibleRect.setHeight( visibleRect.height() )

        return visibleRect

    def viewScrollBarsValueChanged(self):
        try:
            self.onVisibleRectChanged.emit(QRectF( self.VisibleRect ))

        except Exception, err:
            print "EddView.viewScrollBarsValueChanged: ", err
        
    def resizeEvent(self, event):
        self.viewScrollBarsValueChanged()
        QGraphicsView.resizeEvent(self, event)
        
        