"""This module contais code for generating project structure in target
language"""
import os


def create_if_missing(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def java_struct(output_path, app_name):
    """Generates Java project structure"""

    if not os.path.exists(output_path):
        raise Exception("Output path does not exist.")

    app_root = create_if_missing(os.path.join(output_path, app_name))
    app_src = create_if_missing(os.path.join(app_root, "src"))
    app_main = create_if_missing(os.path.join(app_src, "main"))
    _ = create_if_missing(os.path.join(app_src, "test"))

    app_java = create_if_missing(os.path.join(app_main, "java"))
    _ = create_if_missing(os.path.join(app_main, "resources"))

    app_com = create_if_missing(os.path.join(app_java, "com"))
    app_silvera = create_if_missing(os.path.join(app_com, "silvera"))
    app_name = create_if_missing(os.path.join(app_silvera, app_name))
