"""This module contains exception and error definitions"""


class SilveraTypeError(TypeError):

    def __init__(self, decl_name, type_name):
        msg = "Error in '{}'. Type '{}' does not exist!".format(decl_name,
                                                                type_name)
        super().__init__(msg)