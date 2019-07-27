import os
import locale


def get_root_path():
    """Returns project's root path."""
    path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    return path


def get_templates_path():
    """Returns the path to the templates folder."""
    return os.path.join(get_root_path(), "silvera", "generator", "templates")


def get_src_gen_path():
    """Returns the path to the src-gen folder."""
    return os.path.join(get_root_path(), "silvera", "generator", "src-gen")


def decode_byte_str(byte_str):
    """
    Decodes byte string into unicode string.

    Args:
        byte_str(byte): Byte string.

    Returns:
        Unicode string.
    """

    # first try to decode with utf-8 and if that fails try with system default
    for encoding in ("utf-8", locale.getpreferredencoding()):
        try:
            res = byte_str.decode(encoding)
            return res
        except Exception:
            continue
    else:
        return str(byte_str)
