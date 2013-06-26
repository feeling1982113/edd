from edd.core.eobject import EObject


class EAttribute(EObject):

    kTypeInt = EObject()
    kTypeFloat = EObject()

    kTypeVector2d = EObject()
    kTypeVector3d = EObject()

    kTypeList = EObject()
    kTypeEnum = EObject()
    kTypePath = EObject()
    kTypeString = EObject()
    kTypeGeneric = EObject()

    def __init__(self, handle):
        EObject.__init__(self)

        self.__isConnected = False
        self.__isArray = False
        self.__isDirty = False

        self.__attrType = None
        self.__attrName = None
        self.__attrData = None

        self.__minValue = None
        self.__maxValue = None

        self.__attrHandle = handle

    def create(self, attributeType, attributeName, attributeData=None):

        self.__attrType = attributeType
        self.__attrName = attributeName
        self.__attrData = attributeData

        if any([attributeType.matches(EAttribute.kTypeList),
                attributeType.matches(EAttribute.kTypeVector2d),
                attributeType.matches(EAttribute.kTypeVector3d)]):

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

        return self.__attrData

    @Data.setter
    def Data(self, attrData):
        self.__attrData = attrData
        self.__isDirty = True

    @property
    def IsArray(self):
        return self.__isArray

    @property
    def IsConnected(self):
        return self.__isConnected

    @IsConnected.setter
    def IsConnected(self, state):
        self.__isConnected = state

    @property
    def IsDirty(self):
        return self.__isDirty

    def setMinValue(self, minValue):
        self.__minValue = minValue

        if self.__isArray:
            for attr in self.__attrHandle.getAttributeById(self.Id):
                attr.setMinValue(self.__minValue)

    def getMinValue(self):
        return self.__minValue

    def setMaxValue(self, maxValue):
        self.__maxValue = maxValue

        if self.__isArray:
            for attr in self.__attrHandle.getAttributeById(self.Id):
                attr.setMaxValue(self.__maxValue)

    def getMaxValue(self):
        return self.__maxValue







