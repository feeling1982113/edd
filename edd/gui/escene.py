import re
import uuid
from PyQt4.QtCore import pyqtSignal, Qt, QPointF, QLineF, QRectF
from PyQt4.QtGui import *

from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute

from edd.core.econtroller import EController

from edd.gui.utils.edraw import EDraw
from edd.gui.edummy import EDummy
from edd.gui.eedge import EEdge
from edd.gui.enode import ENode
from edd.gui.epoint import EPoint


class ESceneSelection(QGraphicsItem):
    def __init__(self):
        QGraphicsItem.__init__(self)

        self.__selected = None
        self.setZValue(3.0)

        self.__mark = EDraw.Circle(10, 3, 90).translated(QPointF(0.0, -12.0))

        self.__pen = EDraw.EColor.DefaultEnterHoverPen

    def __getSelectedCenter(self):
        tLine = QLineF(self.__selected.mapToScene(self.__selected.boundingRect().topLeft()),
                       self.__selected.mapToScene(self.__selected.boundingRect().topRight()))

        return tLine.pointAt(0.5)

    def __getSelectionPolygon(self):
        return

    @property
    def Item(self):
        return self.__selected

    @Item.setter
    def Item(self, newItem):
        self.__selected = newItem
        if self.__selected:
            self.__selected.setZValue(2.0)

    def boundingRect(self):
        if self.__selected is not None:
            extra = self.__pen.width()
            return self.__mark.boundingRect().adjusted(-extra, -extra, extra, extra).translated(
                self.__getSelectedCenter())

        return QRectF()

    def shape(self):
        return QGraphicsItem.shape(self)

    def paint(self, painter, option, widget=None):

        if self.__selected is not None:

            painter.setPen(EDraw.EColor.DefaultEnterHoverPen)

            if isinstance(self.__selected, EPoint):
                painter.drawRoundedRect(self.__selected.BoundPolygon.translated(self.__selected.scenePos()), 1, 1)
            else:
                painter.drawRoundedRect(self.__selected.boundingRect().translated(self.__selected.scenePos()), 1, 1)


class EDummyData(QGraphicsObject):

    onMove = pyqtSignal()

    def __init__(self):
        QGraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        self.__polygon = QPolygonF(QRectF(-0.5, -0.5, 1, 1))

    @property
    def Polygon(self):
        return self.__polygon

    @Polygon.setter
    def Polygon(self, polygon):
        self.__polygon = polygon

    def data(self):
        return dict({ENode.kGuiAttributeId: None,
                     ENode.kGuiAttributeType: None,
                     ENode.kGuiAttributeParent: self,
                     ENode.kGuiAttributePlug: self.boundingRect().center()})

    def mapFromPoint(self, QPoint):
        return self.__polygon, self.scenePos()

    def mapFromId(self, attrId):
        return self.polygon()

    def boundingRect(self):
        return self.__polygon.boundingRect()

    def shape(self):
        return QGraphicsItem.shape(self)

    def paint(self, painter, option, widget=None):

        painter.drawPolygon(self.__polygon)


class EScene(QGraphicsScene):

    onSelectionChanged = pyqtSignal(type)

    def __init__(self, view, controller, parent=None):
        QGraphicsScene.__init__(self, parent)

        self.__view = view
        self.__controller = controller
        self.__controller.setScene(self)
        self.__controller.Handle.Message.connect(self.__messageFilter)
        self.__controller.Message.connect(self.__messageFilter)

        self.__gridSize = 35

        self.__isEditMode = False

        self.__isGridActive = True
        self.__isAltModifier = False
        self.__isControlModifier = False
        self.__isNodePressed = False

        self.__kDummy = EDummy()
        self.__kDummy.setGridSize(self.__gridSize)
        self.__kDummy.onMouseClick.connect(self.__onDummyMouseClick)
        self.__kDummy.onMouseGesture.connect(self.__onDummyMouseGesture)

        self.__kDummy.hide()

        self.addItem(self.__kDummy)

        self.__kSelected = ESceneSelection()

        self.addItem(self.__kSelected)

        self.__kCutLine = QGraphicsLineItem()
        self.__kCutLine.hide()

        self.__dummyHead = EDummyData()
        self.__dummyTail = EDummyData()
        self.__dummyHead.hide()
        self.__dummyTail.hide()

        self.__kConnectionDummy = EEdge(self.__dummyHead.data(), self.__dummyTail.data(), uuid.uuid1(), True)
        self.__kConnectionDummy.hide()

        self.addItem(self.__kConnectionDummy)
        self.addItem(self.__kCutLine)
        self.addItem(self.__dummyHead)
        self.addItem(self.__dummyTail)

        self.__nodes = {}
        self.__namespace = {}
        self.__nodeNames = []
        self.__connections = {}

        self.__pressedAttributes = None
        self.__kSelected.Item = None

    def __isNode(self, EObject):
        return isinstance(EObject, ENode)

    def __isEdge(self, EObject):
        return isinstance(EObject, EEdge)

    def __onDummyMouseClick(self):

        if self.__isNode(self.sender()):

            pressedId, pressedPlug = self.sender().mapFromPoint(self.__kDummy.scenePos())

            if not self.__nodes.has_key(pressedId):

                self.__pressedAttributes = pressedId

                self.sender().setFlag(QGraphicsItem.ItemIsMovable, False)

                self.__dummyHead.setPos(pressedPlug)

                if self.sender().Handle.IsContainer:
                    self.__dummyTail.Polygon = self.sender().Polygon

                    self.__kConnectionDummy.Head = self.__dummyHead.data()
                    self.__kConnectionDummy.Tail = self.__dummyTail.data()

                    if self.__controller.Handle.getAttributeFromId(pressedId).Handle.isInput(pressedId):
                        self.__kConnectionDummy.Tail = self.__dummyHead.data()
                        self.__kConnectionDummy.Head = self.__dummyTail.data()

                #self.sender().mute(pressedId)

                self.__kConnectionDummy.update()
                self.__kConnectionDummy.show()

            self.__kSelected.Item = self.sender()

            dataBlock = type("EData", (EObject,), {'nodeName': self.__kSelected.Item.Name,
                                                   'nodeProperties': self.__kSelected.Item.Handle.lsProperties()})
            self.onSelectionChanged.emit(dataBlock)

    def __onDummyMouseGesture(self, line):

        if self.__isNode(self.itemAt(line.p1())) and self.__isNode(self.itemAt(line.p2())):
            return

        self.__kCutLine.setLine(line)

        data = [item for item in self.__kCutLine.collidingItems() if isinstance(item, EEdge) or isinstance(item, ENode)]

        if len(data):
            self.__isEditMode = True

            for item in data:
                if isinstance(item, EEdge):
                    if self.__kCutLine.collidesWithPath(item.shape()):
                        self.__controller.disconnectAttr(item.Head[ENode.kGuiAttributeId], item.Tail[ENode.kGuiAttributeId])

                elif isinstance(item, ENode):
                    self.__controller.deleteNode(item.Id)
        else:
            self.__isEditMode = False

    def __getDataFromId(self, theId):
        handle = self.__controller.Handle.getAttributeHandleId(theId)

        if handle:
            return self.__nodes[handle].mapFromId(theId)

        return None

    def getValidName(self, name):
        if name not in [node.Name for node in self.getNodes().values()]:
            return self.__updateNamespace(name)

        return None

    def __updateNamespace(self, name, remove=False):

        name = name.replace(" ", "_")
        result = re.search('(\d+)$', r"%s" % name)

        if result:
            self.__nodeNames.append(re.sub('(\d+)$', "", name))
            return name

        self.__nodeNames.append("%s_" % name)
        return "%s_%s" % (name, self.__nodeNames.count('%s_' % name))

    def __messageFilter(self, message):

        if message.matches(EController.kMessageNodeAdded):

            handle, name = message.getData()

            if handle.IsContainer:
                newNode = EPoint(handle)
            else:
                newNode = ENode(handle)

            newNode.setPos(self.__kDummy.scenePos())
            newNode.Name = self.__updateNamespace(name)

            self.addItem(newNode)

            self.__kSelected.Item = newNode

        if message.matches(EController.kMessageNodeRemoved):

            self.__kSelected.Item = None
            self.onSelectionChanged.emit(type("EData", (EObject,), {'nodeName': '', 'nodeProperties': []}))

            node = self.__nodes[message.getData()]

            self.removeItem(node)
            self.__nodes.pop(message.getData(), None)

            return

        if message.matches(EController.kMessageConnectionMade):

            if not len(message.getData()):
                return

            dataOne = self.__getDataFromId(message.getData()[0])
            dataTwo = self.__getDataFromId(message.getData()[1])

            if dataOne and dataTwo:
                if any([isinstance(dataOne[ENode.kGuiAttributeParent], EPoint),
                        isinstance(dataTwo[ENode.kGuiAttributeParent], EPoint)]):

                    conn = EEdge(dataOne, dataTwo, message.getData()[2], True)
                    conn.Tail[ENode.kGuiAttributeParent].togglePlug(conn.Tail[ENode.kGuiAttributeId])

                else:
                    conn = EEdge(dataOne, dataTwo, message.getData()[2])

                self.__connections[conn.Id] = conn
                self.addItem(conn)

            return

        if message.matches(EController.kMessageConnectionBroke):
            if message.getData() in self.__connections.keys():

                connTail = self.__connections[message.getData()].Tail

                if isinstance(connTail[ENode.kGuiAttributeParent], EPoint):
                    connTail[ENode.kGuiAttributeParent].togglePlug(connTail[ENode.kGuiAttributeId])

                self.removeItem(self.__connections[message.getData()])

                self.__connections.pop(message.getData(), None)

                self.update()
            return

    @property
    def IsEditMode(self):
        return self.__isEditMode

    def getNodes(self):
        return self.__nodes

    def getConnections(self):
        return self.__connections

    def addItem(self, graphicsItem):

        if self.__isNode(graphicsItem):
            graphicsItem.setZValue(1.0)
            graphicsItem.onPress.connect(self.__onDummyMouseClick)

            self.__nodes[graphicsItem.Id] = graphicsItem

        QGraphicsScene.addItem(self, graphicsItem)

    def drawBackground(self, painter, rect):
        self.update()

        if self.__isGridActive:

            painter.setPen(Qt.NoPen)
            painter.fillRect(rect, EDraw.EColor.DefaultSceneFillColor)

            left = int(rect.left()) - (int(rect.left()) % self.__gridSize)
            top = int(rect.top()) - (int(rect.top()) % self.__gridSize)
            lines = []
            right = int(rect.right())
            bottom = int(rect.bottom())
            for x in range(left, right, self.__gridSize):
                lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            for y in range(top, bottom, self.__gridSize):
                lines.append(QLineF(rect.left(), y, rect.right(), y))

            painter.setPen(QPen(EDraw.EColor.DefaultSceneGridColor, 1, Qt.SolidLine))
            painter.drawLines(lines)
            return

        painter.fillRect(rect, EDraw.EColor.DefaultSceneFillColor)

    def contextMenuEvent(self, mouseEvent):
        QGraphicsScene.contextMenuEvent(self, mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        QGraphicsScene.mouseMoveEvent(self, mouseEvent)

        self.__kDummy.setPos(mouseEvent.scenePos())

        if self.__kDummy.IsSnapMode:
            if self.__kSelected.Item:
                #self.__kSelected.Item.setPos(self.__kDummy.Position)
                #self.__kSelected.Item.onMove.emit()
                pass

        self.__dummyTail.setPos(mouseEvent.scenePos())
        self.__kConnectionDummy.update()

        self.update()

    def mousePressEvent(self, mouseEvent):

        for node in self.__nodes.itervalues():
            node.setZValue(1.0)

        if self.__isControlModifier:
            return

        if self.__isAltModifier:
            self.__kDummy.ToggleEditMode()
            return

        if not self.itemAt(mouseEvent.scenePos()):
            self.__kSelected.Item = None
            self.onSelectionChanged.emit(type("EData", (EObject,), {'nodeName': '', 'nodeProperties': []}))

        if mouseEvent.button() == Qt.RightButton:
            if self.__isNode(self.itemAt(mouseEvent.scenePos())):
                self.__isNodePressed = True
                self.__kDummy.ToggleEditMode()
                return

        QGraphicsScene.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):

        if self.__isAltModifier:
            self.__kDummy.ToggleEditMode()
            self.update()
            return

        if mouseEvent.button() == Qt.RightButton:
            if self.__isNodePressed:
                self.__isNodePressed = False
                self.__kDummy.ToggleEditMode()
                return

        if self.__kSelected.Item:
            self.__kSelected.Item.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.__kConnectionDummy.hide()
            self.__kSelected.Item.mute(None)

            if isinstance(self.itemAt(mouseEvent.scenePos()), ENode):
                if self.__pressedAttributes:
                    hitId, hitPoint = self.itemAt(mouseEvent.scenePos()).mapFromPoint(mouseEvent.scenePos())
                    self.__controller.connectAttr(self.__pressedAttributes, hitId)
                    self.__pressedAttributes = None

        self.update()

        QGraphicsScene.mouseReleaseEvent(self, mouseEvent)

    def keyPressEvent(self, keyEvent):
        QGraphicsScene.keyPressEvent(self, keyEvent)

        if keyEvent.key() == Qt.Key_Control:
            self.__view.setDragMode(QGraphicsView.ScrollHandDrag)
            self.__isControlModifier = True

        if keyEvent.key() == Qt.Key_Alt:
            self.__isAltModifier = True

        if keyEvent.key() == 88:
            self.__kDummy.IsSnapMode = True
            self.__kDummy.show()

        if keyEvent.key() == Qt.Key_Tab:
            print 'Tab, Tab..'

    def keyReleaseEvent(self, keyEvent):
        QGraphicsScene.keyReleaseEvent(self, keyEvent)

        if keyEvent.key() == Qt.Key_Control:
            self.__view.setDragMode(QGraphicsView.NoDrag)
            self.__isControlModifier = False

        if keyEvent.key() == Qt.Key_Alt:
            self.__isAltModifier = False

        if keyEvent.key() == 88:
            self.__kDummy.IsSnapMode = False
            self.__kDummy.hide()

        if keyEvent.key() == Qt.Key_Tab:
            print 'Tab, Tab..'



        
        

