import uuid
from edd.core.eobject import EObject
from edd.core.eattribute import EAttribute


class ENodeHandle(EObject):

    # Messages
    kMessageAttributeMarked = EObject()
    kMessageAttributeAdded = EObject()
    kMessageAttributeRemoved = EObject()

    EProperty = type('EProperty', (EObject,), {'kTypeInt': EAttribute.kTypeInt,
                                               'kTypeFloat': EAttribute.kTypeFloat,
                                               'kTypeList': EAttribute.kTypeList,
                                               'kTypeString': EAttribute.kTypeString})

    kTypeInputAttribute = EObject()
    kTypeOutputAttribute = EObject()

    def __init__(self):
        EObject.__init__(self)

        self.kNodeTypeName = None

        self.IsStatic = False
        self.IsContainer = False

        self.__attributes = {}
        self.__inputAttributes = []
        self.__outputAttributes = []

        self.__connections = {}

        self.__attributeLinks = {}

        self.__propertyIndexList = {}

        return

    def __messageFilter(self, message):

        if message.matches(EAttribute.kMessageAttributeSet) and self.IsStatic:
            self.compute()
            return

        """
        if message.matches(EAttribute.kMessageAttributeGet):
            if message.sender().Type.matches(EAttribute.kTypeGenericOutput):
                self.compute()
        """

    @property
    def NodeType(self):
        return self.__class__.__name__

    def compute(self):
        return None

    def hasAttribute(self, eAttribute):
        return

    def hasAttributeOfType(self, eAttributeType):
        return

    def addInputAttribute(self, attrName, attrValue=None):
        attr = EAttribute(self).create(EAttribute.kTypeGeneric, attrName, attrValue)

        self.__inputAttributes.append(attr.Id)

        self.addAttribute(attr)
        return attr

    def addOutputAttribute(self, attrName, attrValue=None):
        attr = EAttribute(self).create(EAttribute.kTypeGeneric, attrName, attrValue)

        self.__outputAttributes.append(attr.Id)

        self.addAttribute(attr)
        return attr

    def addProperty(self, propType, propName, propValue):

        attr = EAttribute(self).create(propType, propName, propValue)

        if propType.matches(EAttribute.kTypeList):
            for item in propValue:
                pAttr = EAttribute(self).create(EAttribute.kTypeFloat, str(uuid.uuid1()), item)

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

        if self.getAttributeByName(eAttribute.Name):
            raise AttributeError("Attribute name is not unique! <%s.%s>" % (self.Name, eAttribute.Name))

        self.__attributes[eAttribute.Id] = eAttribute
        eAttribute.Handle = self

        eAttribute.Message.connect(self.__messageFilter)

        self.Message.emit(self.kMessageAttributeAdded.setData(eAttribute))

    def delAttribute(self, attribute):

        if isinstance(attribute, basestring):
            attribute = self.getAttributeByName(attribute)

        if attribute is not None:
            self.__attributes.pop(attribute.Id, None)
            self.Message.emit(ENodeHandle.kMessageAttributeRemoved.setData(attribute))

    def getAttributeById(self, attributeId):

        if self.__attributeLinks.has_key(attributeId):
            return self.__attributeLinks[attributeId]

        if self.__attributes.has_key(attributeId):
            return self.__attributes[attributeId]

        return None

    def getAttributeByName(self, attributeName):

        for attr in self.__attributes.itervalues():
            if attributeName == attr.Name:
                return attr

        return None

    def addConnection(self, connectionId):
        self.__connections[connectionId] = True

    def delConnection(self, connectionId):
        if self.__connections.has_key(connectionId):
            self.__connections.pop(connectionId, None)

    def getConnections(self):
        return self.__connections.keys()

    def hasConnections(self):
        if len(self.__connections.keys()):
            return True

        return False

    def lsAttributes(self):
        return [eAttribute for eAttribute in self.__attributes.itervalues()]

    def isInput(self, attributeId):
        if attributeId in self.__inputAttributes:
            return True

        return False

    def lsInputAttributes(self):
        result = []

        for attrId, attr in self.__attributes.iteritems():
            if attrId in self.__inputAttributes:
                result.append(attr)

        return result

    def lsOutputAttributes(self):
        result = []

        for attrId, attr in self.__attributes.iteritems():
            if attrId in self.__outputAttributes:
                result.append(attr)

        return result

    def lsProperties(self):

        result = []

        for index in sorted(self.__propertyIndexList.keys()):
            result.append(self.__attributes[self.__propertyIndexList[index]])

        return result





        




























