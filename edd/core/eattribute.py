from edd.core.eobject import EObject


class EAttribute(EObject):

    kTypeInt = EObject()
    kTypeFloat = EObject()
    kTypeList = EObject()
    kTypeString = EObject()
    kTypeGeneric = EObject()

    kMessageAttributeSet = EObject()
    kMessageAttributeGet = EObject()
    kMessageAttributeRenamed = EObject()

    def __init__(self, handle):
        EObject.__init__(self)

        self.__type = None
        self.__isConnected = False
        self.__isArray = False

        self.__attrName = None
        self.__attrData = None
        self.__handle = handle

        self.__childArray = []

    def create(self, attributeType, attributeName, attributeData=None):

        self.__type = attributeType
        self.__attrName = attributeName
        self.__attrData = attributeData

        if attributeType.matches(EAttribute.kTypeList):
            self.__isArray = True

        return self

    @property
    def Type(self):
        return self.__type

    @property
    def Name(self):
        return self.__attrName

    @Name.setter
    def Name(self, name):
        self.__attrName = name
        self.Message.emit(self.kMessageAttributeRenamed)

    @property
    def Handle(self):
        return self.__handle

    @Handle.setter
    def Handle(self, handle):
        self.__handle = handle

    @property
    def Data(self):
        if self.__isArray:
            self.__attrData = self.__handle.getAttributeById(self.Id)

        self.Message.emit(self.kMessageAttributeGet)

        return self.__attrData

    @Data.setter
    def Data(self, attrData):
        self.__attrData = attrData
        self.Message.emit(self.kMessageAttributeSet)

    @property
    def isArray(self):
        return self.__isArray

    @property
    def isConnected(self):
        return self.__isConnected

    @isConnected.setter
    def isConnected(self, state):
        self.__isConnected = state

    def clear(self):
        self.__attrData = None







