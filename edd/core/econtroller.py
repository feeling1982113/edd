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

        if head.Type.matches(EAttribute.kTypeInput):
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
    def Model(self):
        return self.__graphHandle.Data

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

    def connectAttr(self, attributeOne, attributeTwo):

        attrOne = self.toInternal(attributeOne)
        attrTwo = self.toInternal(attributeTwo)

        if attrOne.Type.matches(attrTwo.Type):
            return []

        if attrOne.Handle.matches(attrTwo.Handle):
            return []

        if attrOne.Type.matches(EAttribute.kTypeInput):
            inputAttr = attrOne
        else:
            inputAttr = attrTwo

        if inputAttr.isConnected:
            conn = self.__graphHandle.getConnection(self.__graphHandle.getConnectionIdFromAttributeId(inputAttr.Id))
            self.disconnectAttr(conn.Head, conn.Tail)

        connection = EConnection(attrOne, attrTwo)
        self.__graphHandle.addConnection(connection)

        self.Message.emit(self.kMessageConnectionMade.setData([attrOne.Id, attrTwo.Id, connection.Id]))
        return True

    def disconnectAttr(self, attrOne, attrTwo):

        attrOne = self.toInternal(attrOne)
        attrTwo = self.toInternal(attrTwo)

        connOne = self.__graphHandle.getConnection(self.__graphHandle.getConnectionIdFromAttributeId(attrOne.Id))
        connTwo = self.__graphHandle.getConnection(self.__graphHandle.getConnectionIdFromAttributeId(attrTwo.Id))

        if connOne.matches(connTwo):
            connId = self.__graphHandle.delConnection(connOne.Id)
            self.Message.emit(self.kMessageConnectionBroke.setData(connId))
            return True

        return False

    def ls(self):
        return [node.Name for node in self.__scene.getNodes().itervalues()]

    def reset(self):

        for node in self.ls():
            self.deleteNode(node)

        print self.__graphHandle.Data

    def __getNodeCreateCmd(self, nodeTransform):

        props = {}

        for prop in nodeTransform.Handle.lsProperties():
            if prop.Type.matches(EAttribute.kTypeFloat):
                props[prop.Name] = float(prop.Data)

            if prop.Type.matches(EAttribute.kTypeList):
                props[prop.Name] = [float(item.Data) for item in prop.Data]

            if prop.Type.matches(EAttribute.kTypeString):
                props[prop.Name] = str(prop.Data)

        return dict({'TYPE': nodeTransform.Handle.NodeType,
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
            node = self.createNode(nodeData['TYPE'], nodeName)
            self.getTransform(node).setPos(nodeData['PX'], nodeData['PY'])

            for propName, propData in nodeData['PROPS'].iteritems():
                node.getAttributeByName(propName).Data = propData

        for connData in loadData['CONNECTIONS']:
            self.connectAttr(connData['HEAD'], connData['TAIL'])