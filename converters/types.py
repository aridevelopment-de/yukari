class SpacedString(str):
    """
    Class used to differentiate between strings without spaces and strings with spaces
    Can only be placed at the end of an argument list
    """
    pass


class EncapsulatedSpacedString(str):
    """
    Class used to differentiate between strings without spaces and strings with spaces
    Similar to SpacedString, but can be placed anywhere in an argument list except that
    the string is encapsulated in quotes
    """
    pass
