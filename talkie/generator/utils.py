import re


def camelcase_to_snakecase(module_name):
    """Converts camel case to snake case. For more info, check out:
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case#1176023"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', module_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
