import math
from PyQt4.QtCore import Qt, QSizeF, QPointF, QLineF, QRectF
from PyQt4.QtGui import QColor, QPen, QGraphicsObject, QPainterPath, QPolygonF

from edd.core.eattribute import EAttribute
from edd.gui.enode import ENode


class EEdge(QGraphicsObject):
    def __init__(self, head, tail, uuid, arrowed=False):
        QGraphicsObject.__init__(self)

        self.__arrowed = arrowed

        if not issubclass(head.__class__, dict) and not isinstance(tail.__class__, dict):
            raise AttributeError

        self.setZValue(0.0)

        self.__kId = uuid
        self.__head = head
        self.__tail = tail

        self.__path = QPainterPath()
        self.__headPoint = QPointF(0.0, 0.0)
        self.__tailPoint = QPointF(0.0, 0.0)

        if head[ENode.kGuiAttributeType] and tail[ENode.kGuiAttributeType]:
            if head[ENode.kGuiAttributeType].matches(EAttribute.kTypeGenericInput):
                self.__head = tail
                self.__tail = head

        self.__head[ENode.kGuiAttributeParent].onMove.connect(self.update)
        self.__tail[ENode.kGuiAttributeParent].onMove.connect(self.update)

        self.__pen = QPen(QColor(43, 43, 43), 2, Qt.SolidLine)

        self.update()

    @property
    def Id(self):
        return self.__kId

    @property
    def Line(self):
        return QLineF(self.__headPoint, self.__tailPoint)

    @property
    def Head(self):
        return self.__head

    @Head.setter
    def Head(self, newHead):
        self.__head = newHead

    @property
    def Tail(self):
        return self.__tail

    @Tail.setter
    def Tail(self, newTail):
        self.__tail = newTail

    def pen(self):
        return self.__pen

    def setPen(self, pen):
        if not isinstance(pen, QPen):
            raise AttributeError

        self.__pen = pen

    def update(self):

        QGraphicsObject.prepareGeometryChange(self)

        self.__headPoint = self.mapFromItem(self.__head[ENode.kGuiAttributeParent],
                                            self.__head[ENode.kGuiAttributePlug])

        self.__tailPoint = self.mapFromItem(self.__tail[ENode.kGuiAttributeParent],
                                            self.__tail[ENode.kGuiAttributePlug])

        self.__headOffsetLine = QLineF(self.__headPoint, QPointF(self.__headPoint.x() + 15, self.__headPoint.y()))
        self.__tailOffsetLine = QLineF(self.__tailPoint, QPointF(self.__tailPoint.x() - 15, self.__tailPoint.y()))

        line = QLineF(self.__headPoint, self.__tailPoint)
        self.__line = line

    def boundingRect(self):
        extra = (self.pen().width() * 64) / 2
        return QRectF(self.__line.p1(),
                      QSizeF(self.__line.p2().x() - self.__line.p1().x(),
                             self.__line.p2().y() - self.__line.p1().y())).normalized().adjusted(-extra,
                                                                                                 -extra,
                                                                                                 extra,
                                                                                                 extra)

    def shape(self):
        if self.__arrowed:
            return QGraphicsObject.shape(self)

        return QPainterPath(self.__path)

    def getIntersectPoint(self, polygon, point1, point2):

        p1 = polygon[0] + point1
        intersectPoint = QPointF()

        for i in polygon:
            p2 = i + point2
            polyLine = QLineF(p1, p2)

            intersectType = polyLine.intersect(QLineF(point1, point2), intersectPoint)

            if intersectType == QLineF.BoundedIntersection:
                break

            p1 = p2

        return intersectPoint

    def getArrow(self, line):

        Pi = math.pi
        TwoPi = 2.0 * Pi

        arrowSize = 14

        if line.length() > 0:

            angle = math.acos(line.dx() / line.length())
            if line.dy() >= 0:
                angle = TwoPi - angle

            sourceArrowP1 = line.p1() + QPointF(math.sin(angle + Pi / 3) * arrowSize,
                                                math.cos(angle + Pi / 3) * arrowSize)
            sourceArrowP2 = line.p1() + QPointF(math.sin(angle + Pi - Pi / 3) * arrowSize,
                                                math.cos(angle + Pi - Pi / 3) * arrowSize)
            destinationArrowP1 = line.p2() + QPointF(math.sin(angle - Pi / 3) * arrowSize,
                                                     math.cos(angle - Pi / 3) * arrowSize)
            destinationArrowP2 = line.p2() + QPointF(math.sin(angle - Pi + Pi / 3) * arrowSize,
                                                     math.cos(angle - Pi + Pi / 3) * arrowSize)

            arrows = [QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]),
                      QPolygonF([line.p2(), destinationArrowP1, destinationArrowP2])]

            return arrows[0]

        return QPolygonF()

    def drawPath(self, startPoint, endPoint):
        path = QPainterPath()

        one = (QPointF(endPoint.x(), startPoint.y()) + startPoint) / 2
        two = (QPointF(startPoint.x(), endPoint.y()) + endPoint) / 2

        path.moveTo(startPoint)

        if startPoint.x() > endPoint.x():
            dist = (startPoint.x() - endPoint.x()) * 2

            tLine = QLineF((dist / 2), 0.0, -(dist / 2), 0.0).translated(QLineF(startPoint, endPoint).pointAt(0.5))

            one = tLine.p1()
            two = tLine.p2()

        path.cubicTo(one, two, endPoint)

        self.__path = path
        return path, QLineF(one, two)

    def paint(self, painter, option, widget=None):

        painter.setPen(self.pen())

        if not self.__arrowed:
            headCenter = self.mapFromItem(self.__head[ENode.kGuiAttributeParent],
                                          self.__head[ENode.kGuiAttributeParent].boundingRect().center())

            tailCenter = self.mapFromItem(self.__tail[ENode.kGuiAttributeParent],
                                          self.__tail[ENode.kGuiAttributeParent].boundingRect().center())

            centerPoint = QLineF(headCenter, tailCenter).pointAt(0.5)

            centerPoint.setX(self.__headOffsetLine.p2().x())
            centerPoint.setX(self.__tailOffsetLine.p2().x())

            painter.drawPath(self.drawPath(self.__headOffsetLine.p1(), self.__tailOffsetLine.p1())[0])

        else:

            painter.drawLine(self.__line)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(43, 43, 43))

            headCutPoint = self.getIntersectPoint(self.__head[ENode.kGuiAttributeParent].Polygon,
                                                  self.__line.p1(), self.__line.p2())

            tailCutPoint = self.getIntersectPoint(self.__tail[ENode.kGuiAttributeParent].Polygon,
                                                  self.__line.p2(), self.__line.p1())

            painter.drawPolygon(self.getArrow(QLineF(headCutPoint, tailCutPoint)))

