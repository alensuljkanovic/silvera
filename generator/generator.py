"""
This module contains code generator for Talkie IDL.
"""
import os
from collections import OrderedDict

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from generator import platforms
from talkie.utils import get_root_path


class TalkieGenerator(object):
    """ Talkie IDL code generator."""
    def __init__(self, interface_def):
        self.interface_def = interface_def
        self.platforms = interface_def.langs

    def _get_environment(self):
        """Loads jinja2 Environment."""
        templates_path = os.path.join(get_root_path(), "generator",
                                      "templates")

        templates = []
        for platform in self.platforms:
            templates.append(os.path.join(templates_path, platform))

        env = Environment(loader=FileSystemLoader(templates))
        return env

    def _get_platform_data(self, platform):
        """Returns"""
        d = {"name": self.interface_def.name, "functions": []}

        for function in self.interface_def.functions:
            ret_type = platforms.convert_type(platform, function.ret_type)

            func_dict = {"ret_type": ret_type, "name": function.name}

            params_as_str = []
            params = []
            for param in function.params:
                p_type = platforms.convert_type(platform, param.p_type)
                p_name = param.p_name
                if platforms.is_dynamic(platform):
                    params_as_str.append(p_name)
                else:
                    params_as_str.append("%s %s" % (p_type, p_name))

                params.append({"p_type": p_type, "p_name": p_name})

            params_str = ", ".join(params_as_str)
            func_dict["parameters"] = params_str
            func_dict["params"] = params
            d["functions"].append(func_dict)

        return d

    def generate(self):
        """Generates code."""
        env = self._get_environment()

        src_gen_path = os.path.join(get_root_path(), "generator", "src-gen")

        for platform in self.platforms:
            d = self._get_platform_data(platform)
            file_ext = platforms.get_file_ext(platform)
            #
            # Generate interface file
            #
            interface_name = "%s_interface.template" % platform

            file_name = "%sInterface%s" % (self.interface_def.name, file_ext)
            file_path = os.path.join(src_gen_path, file_name)
            interface_tm = env.get_template(interface_name)
            interface_tm.stream(d=d).dump(file_path)
            #
            # Generate stub file
            #
            stub_name = "%s_stub.template" % platform
            file_name = "%sStub%s" % (self.interface_def.name, file_ext)
            file_path = os.path.join(src_gen_path, file_name)
            stub_tm = env.get_template(stub_name)
            stub_tm.stream(d=d).dump(file_path)
