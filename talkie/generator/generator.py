"""
This module contains code generator for Talkie IDL.
"""
import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from talkie.const import MVN_GENERATE
from talkie.generator.platforms import JAVA, convert_complex_type
from talkie.talkie import CustomType
from talkie.utils import get_templates_path, decode_byte_str


class TalkieGenerator:
    """ Talkie IDL code generator."""
    def __init__(self, module):
        self.module = module

    def _get_environment(self, lang):
        """Loads jinja2 Environment."""
        templates_path = os.path.join(get_templates_path(), lang)

        env = Environment(loader=FileSystemLoader(templates_path))
        return env

    def generate(self, output_path):
        """Generates code."""

        for config_serv in self.module.config_servers:
            self._generate_config_server(output_path, config_serv)

        for serv_registry in self.module.service_registries:
            self._generate_serv_registry(output_path, serv_registry)

        for service in self.module.service_instances:
            self._generate_service(output_path, service)

    def _generate_service(self, output_path, service):
        target_lang = service.type.lang
        if target_lang == JAVA:
            _create_java_project(output_path, service)

    def _generate_serv_registry(self, output_path, serv_registry):
        _create_eureka_serv_registry(output_path, serv_registry)

    def _generate_config_server(self, output_path, config_server):
        _create_config_server(output_path, config_server)


def _create_java_project(output_path, service):
    """Creates Java project with following folder structure:

    {{ServiceName}}:
        - src
            - main
                - java
                    - impl
                        - {{ServiceName}}
                            - controller
                            - domain
                            - service
                - resources
            - test
        - bootstrap.properties
        - pom.xml
    """
    templates_path = os.path.join(get_templates_path(), JAVA, "service")

    env = Environment(loader=FileSystemLoader(templates_path))
    env.filters["firstupper"] = lambda x: x[0].upper() + x[1:]
    env.filters["firstlower"] = lambda x: x[0].lower() + x[1:]
    env.filters["converttype"] = lambda x: convert_complex_type(JAVA, x)
    env.filters["unfold_function_params"] = lambda x: unfold_function_params(
        JAVA, x, False)
    env.filters["unfold_function_params_rest"] = lambda x: unfold_function_params(
        JAVA, x)
    env.filters["param_names"] = get_param_names

    service_name = service.name
    service_version = service.version
    service_port = service.port

    mvn_generate(output_path, service_name)
    root = os.path.join(output_path, service_name)

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("bootstrap_properties.template")
    d = {
        "service_name": service_name,
        "config_server_uri": "http://localhost:%s" % service.type.config_server.port,
        "service_registry_url": service.type.service_registry.url,
        "service_port": "${PORT:%s}" % service_port,
        "service_version": service_version

    }
    bootstrap_template.stream(d).dump(os.path.join(root,
                                                   "bootstrap.properties"))

    #
    # Generate pom.xml
    #
    pom_template = env.get_template("pom_xml.template")
    pom_template.stream(d).dump(os.path.join(root, "pom.xml"))

    content_path = os.path.join(root, "src", "main", "java", "com", "talkie",
                                service_name)
    # os.mkdir(content_path)

    #
    # Generate {{ServiceName}}Application.java
    #
    app_template = env.get_template("main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate controller
    #
    controller_path = os.path.join(content_path, "controller")
    os.mkdir(controller_path)
    controller_data = {
        "service_name": service_name,
        "api": service.type.api
    }
    controller_template = env.get_template("controller.template")
    controller_template.stream(controller_data).dump(os.path.join(controller_path,
                                                                  service_name + "Controller.java"))

    #
    # Generate domain model
    #
    os.mkdir(os.path.join(content_path, "domain"))
    model_path = os.path.join(content_path, "domain", "model")
    os.mkdir(model_path)

    api = service.type.api
    for typedef in api.typedefs:
        data = {
            "service_name": service_name,
            "name": typedef.name,
            "attributes": typedef.fields
        }
        class_template = env.get_template("class.template")
        class_template.stream(data).dump(os.path.join(model_path,
                                         typedef.name + ".java"))

    #
    # Generate services
    #
    service_path = os.path.join(content_path, "service")
    os.mkdir(service_path)

    service_data = {
        "service_name": service_name,
        "api": service.type.api
    }
    service_template = env.get_template("service.template")
    service_template.stream(service_data).dump(
        os.path.join(service_path,
                     service_name + "Service.java"))

    #
    # Generate run script
    #
    _generate_run_script(output_path, service_name, service_version,
                         service_port)


def _create_eureka_serv_registry(output_path, serv_registry):
    """Creates Eureka service registry"""

    templates_path = os.path.join(get_templates_path(), JAVA, "eureka")
    env = Environment(loader=FileSystemLoader(templates_path))

    reg_name = serv_registry.name
    reg_version = serv_registry.version
    reg_port = serv_registry.port

    mvn_generate(output_path, reg_name)

    d = {
        "registry_name": reg_name,
        "uri": serv_registry.uri,
        "port": "${PORT:%s}" % reg_port,
        "client_mode": "true" if serv_registry.client_mode else "false",
        "version": reg_version
    }

    reg_path = os.path.join(output_path, reg_name)

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("eureka_bootstrap.template")
    bootstrap_template.stream(d).dump(os.path.join(reg_path,
                                                   "bootstrap.properties"))
    #
    # Generate pom.xml
    #
    pom_template = env.get_template("eureka_pom_xml.template")
    pom_template.stream(d).dump(os.path.join(reg_path, "pom.xml"))

    content_path = os.path.join(reg_path, "src", "main", "java", "com",
                                "talkie", reg_name)

    #
    # Generate {{ServiceRegistryName}}/App.java
    #
    app_template = env.get_template("eureka_main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate run script
    #
    _generate_run_script(output_path, reg_name, reg_version, reg_port)


def _create_config_server(output_path, config_server):

    templates_path = os.path.join(get_templates_path(), JAVA, "config-server")
    env = Environment(loader=FileSystemLoader(templates_path))

    serv_name = config_server.name
    serv_version = config_server.version
    serv_port = config_server.port

    conf_path = os.path.join(output_path, serv_name)
    mvn_generate(output_path, serv_name)

    d = {
        "name": serv_name,
        "port": "${PORT:%s}" % serv_port,
        "search_path": config_server.search_path,
        "version": serv_version
    }

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("bootstrap_properties.template")
    bootstrap_template.stream(d).dump(os.path.join(conf_path,
                                                   "bootstrap.properties"))
    #
    # Generate pom.xml
    #
    pom_template = env.get_template("pom_xml.template")
    pom_template.stream(d).dump(os.path.join(conf_path, "pom.xml"))

    content_path = os.path.join(conf_path, "src", "main", "java", "com",
                                "talkie", serv_name)
    #
    # Generate {{ServiceRegistryName}}/App.java
    #
    app_template = env.get_template("main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate run script
    #
    _generate_run_script(output_path, serv_name, serv_version, serv_port)


def calculate_type(platform, _type):
    """Calculates platform type for a given Talkie type"""
    try:
        convert_complex_type(platform, _type)
    except KeyError:
        if isinstance(_type, CustomType):
            return str(_type)


def unfold_function_params(platform, func, with_anotations=True):
    """Creates a string from function parameters

    Args:
        platform (str): platform identifier
        func (Function): function whole params are unfolded
        with_anotations (bool): tells whether special anotations shall be
            included in string or not
    """
    if platform == JAVA:
        params = []
        for p in func.params:
            param = ""
            if with_anotations and p.url_placeholder:
                param = "@PathVariable "

            if with_anotations and p.query_param:
                required = "true" if p.default is None else "false"
                param = '@RequestParam(value="%s", required=%s) ' % (p.name, required)

            param += convert_complex_type(JAVA, p.type) + " "
            param += p.name
            params.append(param)

        return ", ".join(params)


def get_param_names(func):
    params = [p.name for p in func.params]
    return ", ".join(params)


def _generate_run_script(output_path, app_name, app_version, app_port):
    """Generates run.sh script for application in its root folder

    Args:
        output_path (str): path to the dir where application root is located
        app_name (str): application name
        app_version (str): application version
        app_version (str): port that application uses

    Returns:
        None
    """
    templates_path = os.path.join(get_templates_path(), JAVA)
    env = Environment(loader=FileSystemLoader(templates_path))
    run_template = env.get_template("run_sh.template")

    out = os.path.join(output_path, app_name, "run.sh")

    d = {"name": app_name, "version": app_version, "port": app_port}
    run_template.stream(d).dump(out)


def mvn_generate(output_path, app_name):
    """Calls Maven which generates the project structure

    Project structure looks as follows:
    {{app_name}}
        - src
            - main
                - java
                    - com
                        - talkie
                            - {{app_name}}
                                - App.java
                - resources
            - test
        - bootstrap.properties
        - pom.xml
    """
    mvn_command = MVN_GENERATE.format(app_name=app_name)

    import subprocess
    process = subprocess.Popen(mvn_command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               shell=True,
                               cwd=output_path)
    outmsg, errmsg = process.communicate()

    errmsg = decode_byte_str(errmsg)

    if errmsg:
        raise Exception(errmsg)

    if process.returncode != 0:
        print(decode_byte_str(outmsg))
        raise Exception("Maven exception!")
