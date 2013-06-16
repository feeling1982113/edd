import uuid
import json

from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute
from edd.core.enodehandle import ENodeHandle
from edd.core.egraphhandle import EGraphHandle


class EConnection(EObject):

    def __init__(self, head, tail):
        EObject.__init__(self)

        self.__headAttr = head
        self.__tailAttr = tail

        if head.Handle.isInput(head.Id):
            self.__tailAttr = head
            self.__headAttr = tail

        self.__tailAttr.Data = self.__headAttr.Handle.getAttributeById(self.__headAttr.Id).Data

    def update(self):
        self.__headAttr.Handle.compute()
        self.__tailAttr.Handle.compute()

        self.__tailAttr.Data = self.__headAttr.Handle.getAttributeById(self.__headAttr.Id).Data

    @property
    def Head(self):
        return self.__headAttr

    @property
    def Tail(self):
        return self.__tailAttr


class EController(EObject):

    kMessageNodeAdded = EObject()
    kMessageNodeRemoved = EObject()

    kMessageNodeUpdate = EObject()

    kMessageEditBegin = EObject()
    kMessageEditEnd = EObject()

    kMessageUnknown = EObject()
    kMessageInternalError = EObject()

    kMessageConnectionMade = EObject()
    kMessageConnectionBroke = EObject()

    def __init__(self):
        EObject.__init__(self)

        self.__scene = None
        self.__regNodes = {}
        self.__graphHandle = EGraphHandle()

    @property
    def Handle(self):
        return self.__graphHandle

    @property
    def NodeTypes(self):
        return self.__regNodes.keys()

    def setScene(self, scene):
        self.__scene = scene

    def getScene(self):
        return self.__scene

    def registerNode(self, nodeName, nodeHandle):
        nodeHandle.NodeType = nodeName
        self.__regNodes[nodeName] = nodeHandle

    def getNode(self, theNode):
        if isinstance(theNode, uuid.UUID):
            return self.__scene.getNodes()[theNode].Handle

        elif isinstance(theNode, basestring):
            for nodeId, node in self.__scene.getNodes().iteritems():
                if theNode == node.Name:
                    return node.Handle

        return None

    def getTransform(self, theNode):

        node = None

        if isinstance(theNode, ENodeHandle):
            return self.__scene.getNodes()[self.getNode(theNode.Id).Id]

        if isinstance(theNode, basestring):
            return self.__scene.getNodes()[self.getNode(theNode).Id]

        return node

    def createNode(self, nodeType, nodeName=None):

        if self.__regNodes.has_key(nodeType):
            nodeHandle = self.__graphHandle.addHandle(self.__regNodes[nodeType]())

            if nodeName is None:
                nodeName = nodeHandle.NodeType

            self.Message.emit(self.kMessageNodeAdded.setData([nodeHandle, nodeName]))

            return nodeHandle

        return None

    def deleteNode(self, node):

        node = self.getNode(node)

        for conn in node.getConnections():
            self.Message.emit(self.kMessageConnectionBroke.setData(conn))

        theId = self.__graphHandle.delHandle(node.Id)

        self.Message.emit(self.kMessageNodeRemoved.setData(theId))

    def toInternal(self, data):

        if isinstance(data, EAttribute):
            return data

        if isinstance(data, basestring):
            splitResult = data.split('.')

            if len(splitResult) == 2:
                if splitResult[0] in self.ls():
                    node = self.getNode(splitResult[0])

                    if splitResult[1] in [attr.Name for attr in node.lsAttributes()]:
                        return node.getAttributeByName(splitResult[1])

            return None

        if isinstance(data, uuid.UUID):
            data = self.__graphHandle.getAttributeFromId(data)
            return data

        return None

    def fromInternal(self, data):
        return

    def connectAttr(self, attributeOne, attributeTwo):

        attrOne = self.toInternal(attributeOne)
        attrTwo = self.toInternal(attributeTwo)

        if not attrOne or not attrTwo:
            return False

        if attrOne.Handle.matches(attrTwo.Handle):
            return False

        if attrOne.Handle.isInput(attrOne.Id):
            inputAttr = attrOne
            outputAttr = attrTwo
        else:
            inputAttr = attrTwo
            outputAttr = attrOne

        if inputAttr.isConnected:
            for connId in self.__graphHandle.getConnectionsFromAttributeId(inputAttr.Id):
                conn = self.__graphHandle.getConnection(connId)
                self.disconnectAttr(conn.Head, conn.Tail)

        connection = EConnection(outputAttr, inputAttr)
        self.__graphHandle.addConnection(connection)

        self.Message.emit(self.kMessageConnectionMade.setData([outputAttr.Id, inputAttr.Id, connection.Id]))

        return True

    def disconnectAttr(self, attrOne, attrTwo):

        connections = self.__graphHandle.getConnectionsFromAttributeId(self.toInternal(attrOne).Id)
        connections.extend(self.__graphHandle.getConnectionsFromAttributeId(self.toInternal(attrTwo).Id))

        for connId in list(set([x for x in connections if connections.count(x) > 1])):
            self.__graphHandle.delConnection(self.__graphHandle.getConnection(connId))
            self.Message.emit(self.kMessageConnectionBroke.setData(connId))

        return True

    def ls(self):
        return [node.Name for node in self.__scene.getNodes().itervalues()]

    def reset(self):

        for node in self.ls():
            self.deleteNode(node)

    def __getNodeCreateCmd(self, nodeTransform):

        props = {}

        for prop in nodeTransform.Handle.lsProperties():
            if prop.Type.matches(EAttribute.kTypeFloat):
                props[prop.Name] = float(prop.Data)

            if prop.Type.matches(EAttribute.kTypeList):
                props[prop.Name] = [float(item.Data) for item in prop.Data]

            if prop.Type.matches(EAttribute.kTypeString):
                props[prop.Name] = str(prop.Data)

        return dict({'REQUEST': nodeTransform.Handle.NodeType,
                     'PX': nodeTransform.scenePos().x(),
                     'PY': nodeTransform.scenePos().y(), 'PROPS': props})

    def __getNodePropertySetCmd(self, nodeTransform):
        return

    def __getConnectionCreateCmd(self, connection):
        headNode = self.getNode(self.__graphHandle.getAttributeHandleId(connection.Head.Id))
        tailNode = self.getNode(self.__graphHandle.getAttributeHandleId(connection.Tail.Id))
        return dict({'HEAD': '%s.%s' % (self.getTransform(headNode).Name, connection.Head.Name),
                     'TAIL': '%s.%s' % (self.getTransform(tailNode).Name, connection.Tail.Name)})

    def save(self, sceneFile):
        saveData = dict({'NODES': {}, 'CONNECTIONS': []})

        for nodeName in self.ls():
            saveData['NODES'][nodeName] = self.__getNodeCreateCmd(self.getTransform(nodeName))

        for conn in self.__scene.getConnections():
            tConn = self.__graphHandle.getConnection(conn)
            saveData['CONNECTIONS'].append(self.__getConnectionCreateCmd(tConn))

        sceneFile = open(sceneFile, 'w')
        sceneFile.write(json.dumps(saveData, indent=4, separators=(',', ': ')))
        sceneFile.close()

    def load(self, sceneFile):
        loadData = json.loads(open(sceneFile).read())

        for nodeName, nodeData in loadData['NODES'].iteritems():

            node = self.createNode(nodeData['REQUEST'], nodeName)
            self.getTransform(node).setPos(nodeData['PX'], nodeData['PY'])

            for propName, propData in nodeData['PROPS'].iteritems():
                node.getAttributeByName(propName).Data = propData

        for connData in loadData['CONNECTIONS']:
            self.connectAttr(connData['HEAD'], connData['TAIL'])