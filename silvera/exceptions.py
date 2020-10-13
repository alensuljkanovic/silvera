"""This module contains exception and error definitions"""


class SilveraTypeError(TypeError):

    def __init__(self, decl_name, type_name, line_col):
        msg = "Error in '{}' {}. Type '{}' does not exist!".format(
            decl_name, line_col, type_name)
        super().__init__(msg)


class SilveraLoadError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)