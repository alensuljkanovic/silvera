"""
This module contains code generator for Talkie IDL.
"""
from collections import defaultdict

import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from talkie.const import MVN_GENERATE, HOST_CONTAINER
from talkie.generator.platforms import JAVA, convert_complex_type, \
    get_def_ret_val
from talkie.talkie import CustomType
from talkie.utils import get_templates_path, decode_byte_str


class TalkieGenerator:
    """ Talkie IDL code generator."""
    def __init__(self, model):
        self.model = model

    def _get_environment(self, lang):
        """Loads jinja2 Environment."""
        templates_path = os.path.join(get_templates_path(), lang)

        env = Environment(loader=FileSystemLoader(templates_path))
        return env

    def generate(self, output_path):
        """Generates code."""
        compose = {
            "version": "3.6",
            "services": []
        }

        def _create_entry(obj, env=True):
            res = {
                "name": obj.name,
                "ports": ",".join(["{0}:{0}".format(obj.port)])
            }
            # res["environment"] =
            return res

        for module in self.model.modules:
            for config_serv in module.config_servers:
                self._generate_config_server(output_path, config_serv)
                if config_serv.host == HOST_CONTAINER:
                    compose["services"].append(_create_entry(config_serv))

            for serv_registry in module.service_registries:
                self._generate_serv_registry(output_path, serv_registry)
                if serv_registry.host == HOST_CONTAINER:
                    compose["services"].append(_create_entry(serv_registry))

            for service in module.service_instances:
                self._generate_service(output_path, service)
                if service.type.host == HOST_CONTAINER:
                    compose["services"].append(_create_entry(service))

        if compose["services"]:
            _generate_docker_compose(output_path, compose)

    def _generate_service(self, output_path, service):
        target_lang = service.type.lang
        if target_lang == JAVA:
            _create_java_service(output_path, service)

    def _generate_serv_registry(self, output_path, serv_registry):
        _create_eureka_serv_registry(output_path, serv_registry)

    def _generate_config_server(self, output_path, config_server):
        _create_config_server(output_path, config_server)


def _create_java_service(output_path, service):
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

    env.globals["generate_cb_annotation"] = generate_cb_annotation
    env.globals["get_default_for_cb_pattern"] = lambda x: \
        get_default_for_cb_pattern(JAVA, x)
    env.globals["get_rest_call"] = lambda x: get_rest_call(JAVA, x)

    service_name = service.name
    service_version = service.version
    service_port = service.port

    mvn_generate(output_path, service_name)
    root = os.path.join(output_path, service_name)
    res_path = os.path.join(root, "src", "main", "resources")
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("bootstrap_properties.template")
    d = {
        "service_name": service_name,
        "service_port": "${PORT:%s}" % service_port,
        "service_version": service_version,
        "use_circuit_breaker": len(service.type.dependencies) > 0
    }

    if service.type.config_server:
        d["config_server_uri"] = "http://localhost:%s" % \
                                 service.type.config_server.port

    if service.type.service_registry:
        reg = service.type.service_registry
        url = "%s:%s/eureka" % (reg.url, reg.port)
        d["service_registry_url"] = url

    bootstrap_template.stream(d).dump(os.path.join(res_path,
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
        "api": service.type.api,
        "dep_names": [s.name for s in service.type.dependencies],
        "dep_functions": service.type.dep_functions
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
        "package_name": service_name,
        "functions": service.type.api.functions
    }
    service_template = env.get_template("service.template")
    service_template.stream(service_data).dump(
        os.path.join(service_path,
                     service_name + "Service.java"))

    fns_by_service = defaultdict(list)
    for fn in service.type.dep_functions:
        fns_by_service[fn.service_name].append(fn)

    for s in service.type.dependencies:
        s_data = {
            "service_name": s.name,
            "package_name": service_name,
            "functions": fns_by_service[s.name],
            "use_circuit_breaker": True,
            "dependency_service": True
        }
        service_template = env.get_template("service.template")
        service_template.stream(s_data).dump(
            os.path.join(service_path,
                         s.name + "Service.java"))

    #
    # Generate run script
    #
    _generate_run_script(output_path, service_name, service_version,
                         service_port)

    if service.type.host == HOST_CONTAINER:
        # Generate Dockerfile
        _generate_dockerfile(output_path, service_name, service_version,
                             service_port)

        # # Copy wait-for-it.sh
        # from shutil import copy2
        # src = os.path.join(get_root_path(), "talkie", "generator", "utils",
        #                    "wait-for-it.sh")
        # copy2(src, root)


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
        "url": serv_registry.url,
        "port": "${PORT:%s}" % reg_port,
        "client_mode": "true" if serv_registry.client_mode else "false",
        "version": reg_version
    }

    reg_path = os.path.join(output_path, reg_name)
    res_path = os.path.join(reg_path, "src", "main", "resources")
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("eureka_bootstrap.template")
    bootstrap_template.stream(d).dump(os.path.join(res_path,
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

    if serv_registry.host == HOST_CONTAINER:
        # Generate Dockerfile
        _generate_dockerfile(output_path, reg_name, reg_version, reg_port)


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

    res_path = os.path.join(conf_path, "src", "main", "resources")
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("bootstrap_properties.template")
    bootstrap_template.stream(d).dump(os.path.join(res_path,
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

    if config_server.host == HOST_CONTAINER:
        # Generate Dockerfile
        _generate_dockerfile(output_path, serv_name, serv_version, serv_port)


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


def generate_cb_annotation(func):
    if not func.cb_pattern or func.cb_pattern == "fail_fast":
        return ""

    return '@HystrixCommand(fallbackMethod = "%s")' % func.cb_fallback


def get_default_for_cb_pattern(platform, func):
    if platform == JAVA:
        if func.cb_pattern in ("fail_silent", "fallback_method"):
            return get_def_ret_val(platform, func.ret_type)


def get_rest_call(platform, func):
    """Returns the REST URL towards the function of the service that current
    service depends upon"""
    if platform == JAVA:
        port = func.dep.parent.parent.port
        url = 'http://localhost:%s' % port

        rest_mapping = func.dep.rest_path
        return url + "/" + rest_mapping
        # return get_java_rest_call(url, rest_mapping)


def get_java_rest_call(url, rest_mapping):
    import re
    print(url, rest_mapping)
    placeholders = re.findall(r'\{(.*?)\}', rest_mapping)
    base_url = rest_mapping.split("/{%s}" % placeholders[0])[0]
    rest_mapping = rest_mapping.replace(base_url, "")
    for idx, p in enumerate(placeholders):
        to_replace = "/{%s}" % p
        repl_with = '+ "/" + %s' % p

        prefix, suffix = rest_mapping.split(to_replace)

        new_map = '%s %s' % (prefix, repl_with) + suffix
        rest_mapping = new_map

    return '"%s%s"%s' % (url, base_url, rest_mapping)


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


def _generate_dockerfile(output_path, app_name, app_version, app_port):
    """Generates Dockerfile for application in its root folder

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
    template = env.get_template("Dockerfile.template")

    out = os.path.join(output_path, app_name, "Dockerfile")

    d = {"app_name": app_name, "app_version": app_version, "app_port": app_port}
    template.stream(d).dump(out)


def _generate_docker_compose(output_path, d):
    """Generates docker-compose.yml which is used to start all containers at
    the same time

    Args:
        output_path (str): path where file will be generated
        d (dict): data needed for template
    """
    templates_path = os.path.join(get_templates_path(), JAVA)
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template("docker_compose.template")

    out = os.path.join(output_path, "docker-compose.yml")
    template.stream(d).dump(out)


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
