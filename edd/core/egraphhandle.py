import uuid
from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute
from edd.core.enodehandle import ENodeHandle


class EConnection(EObject):

    def __init__(self, head, tail):
        EObject.__init__(self)

        self.__headAttr = head
        self.__tailAttr = tail

        if head.Type.matches(EAttribute.kTypeInput):
            self.__tailAttr = head
            self.__headAttr = tail

        #self.__headAttr.Message.connect(self.__messageFilter)
        #self.__tailAttr.Message.connect(self.__messageFilter)

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


class EGraphHandle(EObject):

    kMessageConnectionBroke = EObject()

    def __init__(self):
        EObject.__init__(self)

        self.__nodes = {}
        self.__attributes = {}
        self.__connections = {}

    def __messageFilter(self, message):

        if message.matches(ENodeHandle.kMessageAttributeAdded):
            self.__attributes[message.getData().Id] = message.getData()

        if message.matches(ENodeHandle.kMessageAttributeRemoved):
            self.__attributes.pop(message.getData().Id, None)

    @property
    def Data(self):
        return self.__nodes, self.__attributes, self.__connections

    def reset(self):
        keys = self.__nodes.keys()
        for k in keys:
            self.delHandle(k)

        self.__nodes = {}
        self.__attributes = {}
        self.__connections = {}

        return keys

    def getAttributeFromId(self, attrId):
        if not isinstance(attrId, uuid.UUID):
            raise AttributeError

        if self.__attributes.has_key(attrId):
            return self.__nodes[self.__attributes[attrId]].getAttributeById(attrId)

        return None

    def getAttributeHandleId(self, attributeId):
        if not isinstance(attributeId, uuid.UUID):
            raise AttributeError

        if self.__attributes.has_key(attributeId):
            return self.__nodes[self.__attributes[attributeId]].Id

        return None

    def addHandle(self, handle):

        handle.Message.connect(self.__messageFilter)

        self.__nodes[handle.Id] = handle

        for attribute in handle.lsAttributes():
            self.__attributes[attribute.Id] = handle.Id

        return handle

    def getHandle(self, nodeId):
        if self.__nodes.has_key(nodeId):
            return self.__nodes[nodeId]

        return None

    def delHandle(self, nodeId):
        for attr in self.__nodes[nodeId].lsAttributes():

            if attr.isConnected:
                self.disconnectAttribute(attr)

            self.__attributes.pop(attr.Id, None)

        self.__nodes.pop(nodeId, None)

        return nodeId

    def delConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            attrOne, attrTwo = self.__connections[connectionId].Head, self.__connections[connectionId].Tail

            if attrOne.Type.matches(EAttribute.kTypeInput):
                self.disconnectAttribute(attrOne)
            else:
                self.disconnectAttribute(attrTwo)

        return

    def getConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            return self.__connections[connectionId]

        return None

    def getConnectionFromAttributeId(self, attrId):

        for key, value in self.__connections.iteritems():
            if attrId in [value.Head.Id, value.Tail.Id]:
                return key

        return None

    def updateHandle(self, handle):

        if self.__nodes.has_key(handle.Id):
            self.__nodes[handle.Id] = handle

            self.Message.emit(self.kMessageNodeUpdate)

    def updateAttribute(self, attributeId, value):

        if self.__attributes.has_key(attributeId):

            attr = self.__nodes[self.__attributes[attributeId]].getAttributeById(attributeId)
            attr.Data = value

            if attr.Handle.hasConnections():

                for conn in self.__connections.itervalues():
                    conn.update()

            return attr

    def connectAttributes(self, attributeOne, attributeTwo, silent=False):

        if isinstance(attributeOne, EAttribute):
            attributeOne = attributeOne.Id

        if isinstance(attributeTwo, EAttribute):
            attributeTwo = attributeTwo.Id

        if self.__attributes.has_key(attributeOne) and self.__attributes.has_key(attributeTwo):

            attrOne = self.__nodes[self.__attributes[attributeOne]].getAttributeById(attributeOne)
            attrTwo = self.__nodes[self.__attributes[attributeTwo]].getAttributeById(attributeTwo)

            if attrOne.Type.matches(attrTwo.Type):
                self.Message.emit(self.kMessageInternalError.setData(None))
                return False

            if attrOne.Handle.matches(attrTwo.Handle):
                self.Message.emit(self.kMessageInternalError.setData(None))
                return False

            if attrOne.Type.matches(EAttribute.kTypeInput):
                inputAttr = attrOne
            else:
                inputAttr = attrTwo

            if inputAttr.isConnected:
                self.disconnectAttribute(inputAttr)

            connection = EConnection(attrOne, attrTwo)
            self.__connections[connection.Id] = connection

            attrOne.isConnected = True
            attrTwo.isConnected = True

            attrOne.Handle.addConnection(connection.Id)
            attrTwo.Handle.addConnection(connection.Id)

            if not silent:
                connection.update()

            return attributeOne, attributeTwo, connection.Id

        return []

    def disconnectAttribute(self, attribute):

        if isinstance(attribute, EAttribute):
            attrId = attribute.Id

        if self.__attributes.has_key(attrId):

            conn = self.getConnectionFromAttributeId(attrId)

            attribute.Handle.delConnection(conn)
            self.__connections.pop(conn, None)

            attribute.isConnected = False

            self.Message.emit(self.kMessageConnectionBroke.setData(conn))

            return True

        return False




