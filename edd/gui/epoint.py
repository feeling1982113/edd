from PyQt4.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt4.QtGui import QPolygonF, QGraphicsItem, QFontMetrics, QGraphicsItemGroup, QGraphicsPolygonItem

from edd.core.eattribute import EAttribute
from edd.gui.utils.edraw import EDraw
from edd.gui.enode import ENode


class EPoint(ENode):

    def __init__(self, ENodeHandle):
        ENode.__init__(self, ENodeHandle)

        self.__polygon = QPolygonF(QRectF(-50, -15, 100, 30))

        self.__updateShape()

        self.__attributes = {}
        self.__hiddenAttributes = {}

        self.__group = QGraphicsItemGroup()
        self.__group.addToGroup(QGraphicsPolygonItem(self.__polygon))

        self.__buildAttributes(self.Handle.lsInputAttributes())
        self.__buildAttributes(self.Handle.lsOutputAttributes(), True)

        self.__muted = None

    def __updateShape(self):

        fBBox = QFontMetrics(self.Font).boundingRect(self.Name)

        if self.__polygon.boundingRect().width() < fBBox.width():
            self.__polygon = QPolygonF(QRectF(fBBox).normalized().adjusted(-fBBox.width() / 4,
                                                                           -fBBox.height() / 4,
                                                                           fBBox.height(),
                                                                           fBBox.height() / 2))

    def __buildAttributes(self, attributes, opposite=False):

        rotation = 90

        for index, point in enumerate(self.getPoints(len(attributes), opposite)):

            switch = {0: point.y() - (8 + self.pen().width()), 1: point.y() + (5 + self.pen().width())}

            connSlot = EDraw.Circle(8, 3, rotation).translated(QPointF(point.x(), switch[opposite]))

            self.__group.addToGroup(QGraphicsPolygonItem(connSlot))

            self.__attributes[connSlot] = dict({self.kGuiAttributeId: attributes[index].Id,
                                               self.kGuiAttributeType: attributes[index].Type,
                                               self.kGuiAttributeParent: self,
                                               self.kGuiAttributePlug: self.Polygon.boundingRect().center(),
                                               self.kGuiAttributeLongName: attributes[index].Name})

        return

    @property
    def Polygon(self):
        return self.__polygon

    @property
    def BoundPolygon(self):
        return self.__polygon.boundingRect()

    def mute(self, uuid):
        self.__muted = uuid

    def togglePlug(self, plugId):

        hiddenId = self.mapFromId(plugId)[ENode.kGuiAttributeId]

        if self.__hiddenAttributes.has_key(hiddenId):
            self.__hiddenAttributes.pop(hiddenId, None)
            return

        self.__hiddenAttributes[self.mapFromId(plugId)[ENode.kGuiAttributeId]] = []

    def mapFromPoint(self, QPoint):

        for attrRect, attrValues in self.__attributes.iteritems():
            if attrRect.boundingRect().contains(self.mapFromScene(QPoint)):
                return attrValues[self.kGuiAttributeId], self.scenePos()

        return self.Handle.Id, None

    def mapFromId(self, attrId):

        for attrValue in self.__attributes.itervalues():
            if attrValue[self.kGuiAttributeId] == attrId:
                return attrValue

        return None

    def boundingRect(self):
        extra = self.pen().width()

        return self.__group.boundingRect().normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        return QGraphicsItem.shape(self)

    def getLines(self, count, opposite=False):

        angleOffset = 25

        inputLines = []

        startAngle = QLineF(QPointF(0.0, 0.0), self.boundingRect().topRight()).angle() + angleOffset
        endAngle = QLineF(QPointF(0.0, 0.0), self.boundingRect().topLeft()).angle() - angleOffset

        if opposite:
            startAngle = QLineF(QPointF(0.0, 0.0), self.boundingRect().bottomLeft()).angle() + angleOffset
            endAngle = QLineF(QPointF(0.0, 0.0), self.boundingRect().bottomRight()).angle() - angleOffset

        step = (endAngle - startAngle) / (count - 1)

        for x in range(0, count):
            tLine = QLineF(QPointF(0.0, 0.0), QPointF(0, 100))
            tLine.setAngle(startAngle)
            inputLines.append(tLine)

            startAngle += step

        return inputLines

    def getPoints(self, count, opposite=False):
        result = []

        line = QLineF(self.__polygon.boundingRect().topLeft(), self.__polygon.boundingRect().topRight())

        if opposite:
            line = QLineF(self.__polygon.boundingRect().bottomLeft(), self.__polygon.boundingRect().bottomRight())

        step = 1.0 / (count + 1)
        currentStep = step

        for x in range(0, count):
            result.append(line.pointAt(currentStep))
            currentStep += step

        return result

    def paint(self, painter, option, widget=None):

        painter.setPen(self.pen())
        painter.setBrush(EDraw.EColor.DefaultTitleColor)

        painter.drawRoundedRect(self.__polygon.boundingRect(), 3, 3)

        painter.setPen(EDraw.EColor.DefaultTitleTextColor)
        painter.drawText(self.__polygon.boundingRect(), Qt.AlignCenter, self.Name)

        for connSlot, connData in self.__attributes.iteritems():
            if connData[self.kGuiAttributeId] != self.__muted and connData[self.kGuiAttributeId] not in self.__hiddenAttributes.keys():
                painter.drawPolygon(connSlot)

        painter.setBrush(Qt.NoBrush)



