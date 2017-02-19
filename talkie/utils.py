import os


def get_root_path():
    """Returns project's root path."""
    path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    return path


def get_templates_path():
    """Returns the path to the templates folder."""
    return os.path.join(get_root_path(), "talkie", "generator", "templates")


def get_src_gen_path():
    """Returns the path to the src-gen folder."""
    return os.path.join(get_root_path(), "talkie", "generator", "src-gen")
