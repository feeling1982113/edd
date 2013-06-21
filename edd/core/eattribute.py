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

        self.__isConnected = False
        self.__isArray = False

        self.__attrType = None
        self.__attrName = None
        self.__attrData = None

        self.__attrHandle = handle

    def create(self, attributeType, attributeName, attributeData=None):

        self.__attrType = attributeType
        self.__attrName = attributeName
        self.__attrData = attributeData

        if attributeType.matches(EAttribute.kTypeList):
            self.__isArray = True

        return self

    @property
    def Type(self):
        return self.__attrType

    @property
    def Name(self):
        return self.__attrName

    @Name.setter
    def Name(self, name):
        self.__attrName = name
        self.Message.emit(self.kMessageAttributeRenamed.setData(self.Id))

    @property
    def Handle(self):
        return self.__attrHandle

    @Handle.setter
    def Handle(self, handle):
        self.__attrHandle = handle

    @property
    def Data(self):
        if self.__isArray:
            self.__attrData = self.__attrHandle.getAttributeById(self.Id)

        self.Message.emit(self.kMessageAttributeGet.setData(self.Id))

        return self.__attrData

    @Data.setter
    def Data(self, attrData):
        self.__attrData = attrData
        self.Message.emit(self.kMessageAttributeSet.setData(self.Id))

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







