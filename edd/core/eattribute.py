from edd.core.eobject import EObject


class EAttribute(EObject):

    """

    .. glossary::

        kTypeInput
        kTypeOutput

        kTypeInt
        kTypeFloat
        kTypeList
        kTypeString

    """

    kTypeInput = EObject()
    kTypeOutput = EObject()

    kTypeInt = EObject()
    kTypeFloat = EObject()
    kTypeList = EObject()
    kTypeString = EObject()

    kMessageAttributeSet = EObject()
    kMessageAttributeGet = EObject()
    kMessageAttributeRenamed = EObject()

    def __init__(self, handle):
        EObject.__init__(self)

        self.__type = None
        self.__isConnected = False

        self.__attrName = None
        self.__attrData = None
        self.__handle = handle

    def create(self, attributeType, attributeName, attributeData=None):

        self.__type = attributeType
        self.__attrName = attributeName
        self.__attrData = attributeData

        self.__isArray = False

        if attributeType.matches(EAttribute.kTypeList):
            self.__isArray = True

        return self

    @property
    def Type(self):
        """

           :param flab_nickers: a series of under garments to process
           :param has_polka_dots: default False
           :param needs_pressing: default False, Whether the list of garments should all be pressed
           """
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

    def isInput(self):
        return self.__type.matches(EAttribute.kTypeInput)

    def isOutput(self):
        return self.__type.matches(EAttribute.kTypeOutput)

    @property
    def isArray(self):
        return self.__isArray

    @property
    def isConnected(self):
        """This function does something.

        Args:
           name (str):  The name to use.

        Kwargs:
           state (bool): Current state to be in.

        Returns:
           int.  The return code::

              0 -- Success!

        A really great idea.  A way you might use me is

        >>> print public_fn_with_googley_docstring(name='foo', state=None)
        0

        .. warning::

            BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.

        """
        return self.__isConnected

    @isConnected.setter
    def isConnected(self, state):
        self.__isConnected = state

    def clear(self):
        self.__attrData = None







