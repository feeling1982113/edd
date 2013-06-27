import uuid

from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute


class ENodeHandle(EObject):

    # Messages
    kMessageAttributeAdded = EObject()
    kMessageAttributeRemoved = EObject()

    kMessageAttributeSet = EObject()
    kMessageAttributeGet = EObject()
    kMessageAttributeRenamed = EObject()

    kMessageAttributeDirty = EObject()

    def __init__(self):
        EObject.__init__(self)

        self.kNodeTypeName = None

        self.IsStandAlone = False
        self.IsContainer = False

        self.__attributes = {}
        self.__inputAttributes = []
        self.__outputAttributes = []
        self.__attributesNetwork = {}

        self.__connections = {}
        self.__attributeLinks = {}
        self.__propertyIndexList = {}
        return

    def __messageFilter(self, attr):

        if self.IsStandAlone:
            self.compute()
            return

        if not self.__isConnected():
            return

        if isinstance(attr.Name, uuid.UUID):
            if self.__attributeLinks.has_key(attr.Name):
                attr = self.__attributes[attr.Name]

        affectedId = self.__getAffectedBy(attr.Id)

        if affectedId:
            self.Message.emit(self.kMessageAttributeDirty.setData(self.__attributes[affectedId]))

    def __isConnected(self):
        return any([attr.IsConnected for attr in self.__attributes.values() if attr.Id in self.__outputAttributes])

    def __getAffectedBy(self, attributeId):

        for key, value in self.__attributesNetwork.iteritems():
            if attributeId in value:
                return key

        return None

    @property
    def NodeType(self):
        return self.__class__.__name__

    def compute(self):
        return None

    def hasAttribute(self, eAttribute):
        return

    def hasAttributeOfType(self, eAttributeType):
        return

    def addInputAttribute(self, attrName, attrType=None, attrValue=None):

        if attrType is None:
            attrType = EAttribute.kTypeGeneric

        attr = EAttribute(self).create(attrType, attrName, attrValue)

        self.__inputAttributes.append(attr.Id)

        self.addAttribute(attr)
        return attr

    def addOutputAttribute(self, attrName, attrType=None, attrValue=None):

        if attrType is None:
            attrType = EAttribute.kTypeGeneric

        attr = EAttribute(self).create(attrType, attrName, attrValue)

        self.__outputAttributes.append(attr.Id)

        self.addAttribute(attr)
        return attr

    def addPropertyAttribute(self, propType, propName, propValue):

        attr = EAttribute(self).create(propType, propName, propValue)

        if any([propType.matches(EAttribute.kTypeList),
                propType.matches(EAttribute.kTypeVector2d),
                propType.matches(EAttribute.kTypeVector3d)]):

            for item in propValue:
                pAttr = EAttribute(self).create(EAttribute.kTypeFloat, attr.Id, item)

                if self.__attributeLinks.has_key(attr.Id):
                    self.__attributeLinks[attr.Id].append(pAttr)
                else:
                    self.__attributeLinks[attr.Id] = [pAttr]

                self.addAttribute(pAttr)

        self.addAttribute(attr)
        self.__propertyIndexList[len(self.__propertyIndexList.keys())] = attr.Id

        return attr

    def addAttribute(self, eAttribute):
        if not isinstance(eAttribute, EAttribute):
            raise

        if self.getAttribute(eAttribute.Name) and not isinstance(eAttribute.Name, uuid.UUID):
            raise AttributeError("Attribute name is not unique! <%s.%s>" % (self.Name, eAttribute.Name))

        self.__attributes[eAttribute.Id] = eAttribute
        eAttribute.Handle = self

        self.Message.emit(self.kMessageAttributeAdded.setData(eAttribute))

    def delAttribute(self, attribute):

        if isinstance(attribute, basestring):
            attribute = self.getAttributeByName(attribute)

        if attribute is not None:
            self.__attributes.pop(attribute.Id, None)
            self.Message.emit(ENodeHandle.kMessageAttributeRemoved.setData(attribute))

    def getAttribute(self, attribute):

        if isinstance(attribute, basestring):
            for attr in self.__attributes.itervalues():
                if attribute == attr.Name:
                    return attr

        if isinstance(attribute, EAttribute):
            return self.getAttributeById(attribute.Id)

        if isinstance(attribute, uuid.UUID):
            return self.getAttributeById(attribute)

        return None

    def setAttribute(self, attribute, value):

        attr = self.getAttribute(attribute)

        if attr:
            attr.Data = value
            self.__messageFilter(attr)
            return True

        return False

    def getAttributeById(self, attributeId):

        if self.__attributeLinks.has_key(attributeId):
            return self.__attributeLinks[attributeId]

        if self.__attributes.has_key(attributeId):
            return self.__attributes[attributeId]

        return None

    def attributeAffects(self, inputAttr, outputAttr):
        if self.__attributesNetwork.has_key(outputAttr.Id):
            self.__attributesNetwork[outputAttr.Id].append(inputAttr.Id)

        else:
            self.__attributesNetwork[outputAttr.Id] = [inputAttr.Id]

    def addConnection(self, connectionId):
        self.__connections[connectionId] = True

        if self.IsStandAlone:
            self.compute()

    def delConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            self.__connections.pop(connectionId, None)

        if self.IsStandAlone:
            if not len(self.__connections):
                for inAttr in self.lsInputAttributes():
                    inAttr.Data = None

                self.compute()

    def getConnections(self):
        return self.__connections.keys()

    def hasConnections(self):
        if len(self.__connections.keys()):
            return True

        return False

    def lsAttributes(self):
        return self.__attributes.values()

    def lsInputAttributes(self):
        result = []

        for attrId, attr in self.__attributes.iteritems():
            if attrId in self.__inputAttributes:
                result.append(attr)

        return result

    def isInput(self, attributeId):
        if attributeId in self.__inputAttributes:
            return True

        return False

    def lsOutputAttributes(self):
        result = []

        for attrId, attr in self.__attributes.iteritems():
            if attrId in self.__outputAttributes:
                result.append(attr)

        return result

    def isOutput(self, attributeId):
        if attributeId in self.__outputAttributes:
            return True

        return False

    def lsProperties(self):

        result = []

        for index in sorted(self.__propertyIndexList.keys()):
            result.append(self.__attributes[self.__propertyIndexList[index]])

        return result





        




























