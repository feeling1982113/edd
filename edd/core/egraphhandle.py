import uuid
from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute
from edd.core.enodehandle import ENodeHandle


class EGraphHandle(EObject):

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

    def isHandle(self, internalId):
        return self.__nodes.has_key(internalId)

    def isAttribute(self, internalId):
        return self.__attributes.has_key(internalId)

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

        for conn in self.__nodes[nodeId].getConnections():
            self.delConnection(conn)

        for attr in self.__nodes[nodeId].lsAttributes():
            self.__attributes.pop(attr.Id, None)

        self.__nodes.pop(nodeId, None)

        return nodeId

    def addConnection(self, connection):
        self.__connections[connection.Id] = connection

        connection.Source.IsConnected = True
        connection.Destination.IsConnected = True

        connection.Source.Handle.addConnection(connection.Id)
        connection.Destination.Handle.addConnection(connection.Id)

    def getConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            return self.__connections[connectionId]

        return None

    def __disconnectAttribute(self, attribute):

        if isinstance(attribute, EAttribute):
            attrId = attribute.Id

        if self.__attributes.has_key(attrId):

            for conn in self.getConnectionsFromAttributeId(attrId):
                attribute.Handle.delConnection(conn)
                self.__connections.pop(conn, None)

                attribute.IsConnected = False

        return None

    def delConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            attrOne, attrTwo = self.__connections[connectionId].Source, self.__connections[connectionId].Destination

            if attrOne.Handle.isInput(attrOne.Id):
                self.__disconnectAttribute(attrOne)
            else:
                self.__disconnectAttribute(attrTwo)

        return connectionId

    def getAttributeFromId(self, attrId):
        if not isinstance(attrId, uuid.UUID):
            raise AttributeError

        if self.__attributes.has_key(attrId):
            return self.__nodes[self.__attributes[attrId]].getAttributeById(attrId)

        return None

    def getAttributeHandleId(self, attrId):
        if not isinstance(attrId, uuid.UUID):
            raise AttributeError

        if self.__attributes.has_key(attrId):
            return self.__nodes[self.__attributes[attrId]].Id

        return None

    def getConnectionsFromAttributeId(self, attrId):

        result = []

        for key, value in self.__connections.iteritems():
            if attrId in [value.Source.Id, value.Destination.Id]:
                result.append(key)

        return result

    def updateConnections(self):
        for conn in self.__connections.values():
            conn.update()

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






