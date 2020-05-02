import os
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from silvera.const import HOST_CONTAINER, HTTP_POST
from silvera.core import (CustomType, ConfigServerDecl, ServiceRegistryDecl,
                          ServiceDecl, APIGateway)
from silvera.generator.platforms import (
    JAVA, convert_complex_type, get_def_ret_val, is_collection
)
from silvera.utils import get_templates_path
from silvera.generator.gen_reg import GeneratorDesc
from silvera.generator.project_struct import java_struct, create_if_missing


def timestamp():
    return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())


def generate_config_server(config_server, output_dir):

    templates_path = os.path.join(get_templates_path(), JAVA, "config-server")
    env = Environment(loader=FileSystemLoader(templates_path))

    serv_name = config_server.name
    serv_version = config_server.version
    serv_port = config_server.port

    conf_path = os.path.join(output_dir, serv_name)
    java_struct(output_dir, serv_name)

    d = {
        "name": serv_name,
        "port": "${PORT:%s}" % serv_port,
        "search_path": config_server.search_path,
        "version": serv_version,
        "timestamp": timestamp()
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
                                "silvera", serv_name)
    #
    # Generate {{ServiceRegistryName}}/App.java
    #
    app_template = env.get_template("main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate run script
    #
    generate_run_script(output_dir, serv_name, serv_version, serv_port)

    if config_server.host == HOST_CONTAINER:
        # Generate Dockerfile
        generate_dockerfile(output_dir, serv_name, serv_version, serv_port)


def generate_service_registry(serv_registry, output_dir):
    """Creates Eureka service registry"""

    templates_path = os.path.join(get_templates_path(), JAVA, "eureka")
    env = Environment(loader=FileSystemLoader(templates_path))

    reg_name = serv_registry.name
    reg_version = serv_registry.version
    reg_port = serv_registry.port

    java_struct(output_dir, reg_name)

    d = {
        "registry_name": reg_name,
        "url": serv_registry.url,
        "port": "${PORT:%s}" % reg_port,
        "client_mode": "true" if serv_registry.client_mode else "false",
        "version": reg_version,
        "timestamp": timestamp()
    }

    reg_path = os.path.join(output_dir, reg_name)
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
                                "silvera", reg_name)

    #
    # Generate {{ServiceRegistryName}}/App.java
    #
    app_template = env.get_template("eureka_main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate run script
    #
    generate_run_script(output_dir, reg_name, reg_version, reg_port)

    if serv_registry.host == HOST_CONTAINER:
        # Generate Dockerfile
        generate_dockerfile(output_dir, reg_name, reg_version, reg_port)


def generate_api_gateway(api_gateway, output_dir):
    """Creates Zuul API Gateway"""

    templates_path = os.path.join(get_templates_path(), JAVA, "api-gateway")
    env = Environment(loader=FileSystemLoader(templates_path))

    gname = api_gateway.name

    java_struct(output_dir, gname)

    if api_gateway.service_registry:
        reg = api_gateway.service_registry
        reg_url = "%s:%s/eureka" % (reg.url, reg.port)
        user_service_registry = True
    else:
        reg_url = None
        user_service_registry = False

    d = {
        "gateway_name": gname,
        "gateway_version": api_gateway.version,
        "port": "${PORT:%s}" % api_gateway.port,
        "service_registry_url": reg_url,
        "gateway_for": [(g.service.name, g.path, g.service.port)
                        for g in api_gateway.gateway_for],
        "timestamp": timestamp(),
        "user_service_registry": user_service_registry
    }

    gt_path = os.path.join(output_dir, gname)
    res_path = os.path.join(gt_path, "src", "main", "resources")
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    #
    # Generate bootstrap.properties
    #
    bootstrap_template = env.get_template("bootstrap_properties.template")
    bootstrap_template.stream(d).dump(os.path.join(res_path,
                                                   "application.properties"))

    #
    # Generate pom.xml
    #
    pom_template = env.get_template("pom_xml.template")
    pom_template.stream(d).dump(os.path.join(gt_path, "pom.xml"))

    content_path = os.path.join(gt_path, "src", "main", "java", "com",
                                "silvera", gname)

    #
    # Generate main class: App.java
    #
    app_template = env.get_template("main.template")
    app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    #
    # Generate run script
    #
    generate_run_script(output_dir,
                        gname,
                        api_gateway.version,
                        api_gateway.port)

    if api_gateway.host == HOST_CONTAINER:
        # Generate Dockerfile
        generate_dockerfile(output_dir,
                            gname,
                            api_gateway.version,
                            api_gateway.port)


def generate_service(service, output_dir):

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
    if service.comm_style == "rpc":
        generator = RPCServiceGenerator(service)
    else:
        generator = MsgServiceGenerator(service)

    generator.generate(output_dir)


class ServiceGenerator:
    """Base class for service generators

    Attributes:
        service (Service): core service object
        _templates_path (str): path to templates used during code generation
    """
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._templates_path = os.path.join(
            get_templates_path(),
            JAVA,
            "service",
            self.service.comm_style
        )

        self.model = service.parent.model

    def _get_env(self):
        env = Environment(loader=FileSystemLoader(self._templates_path))
        env.filters["firstupper"] = lambda x: x[0].upper() + x[1:]
        env.filters["firstlower"] = lambda x: x[0].lower() + x[1:]
        env.filters["converttype"] = lambda x: convert_complex_type(JAVA, x)
        env.filters["return_type"] = lambda fnc: get_return_type(fnc)
        env.filters["unfold_function_params"] = lambda x: unfold_function_params(
            JAVA, x, False)
        env.filters["unfold_function_params_rest"] = lambda x: unfold_function_params(
            JAVA, x)
        env.filters["param_names"] = get_param_names
        env.filters["topics"] = lambda f: ", ".join(
            ['"%s"' % c for c in f.channels]
        )

        env.globals["generate_cb_annotation"] = generate_cb_annotation
        env.globals["get_default_for_cb_pattern"] = lambda x: \
            get_default_for_cb_pattern(JAVA, x)
        env.globals["get_rest_call"] = lambda x: get_rest_call(JAVA, x)
        env.globals["default_value_for_type"] = lambda x: \
            get_def_ret_val(JAVA, x)

        env.tests["collection"] = lambda x: is_collection(x)

        return env

    def generate_main(self, env, content_path, d):
        """Generate main class: {{ServiceName}}Application.java

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
            d (dict): dict with variables for templates
        """
        app_template = env.get_template("main.template")
        app_template.stream(d).dump(os.path.join(content_path, "App.java"))

    def generate_bootstrap_properties(self, env, output_dir, d):
        """Generate bootstrap.properties

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
            d (dict): dict with variables for templates
        """

        service = self.service
        root = os.path.join(output_dir, service.name)
        res_path = os.path.join(root, "src", "main", "resources")

        bootstrap_template = env.get_template("bootstrap_properties.template")

        if service.config_server:
            d["config_server_uri"] = "http://localhost:%s" % \
                                      service.config_server.port

        if service.service_registry:
            reg = service.service_registry
            url = "%s:%s/eureka" % (reg.url, reg.port)
            d["service_registry_url"] = url

        bootstrap_template.stream(d).dump(os.path.join(res_path,
                                                       "bootstrap.properties"))

    def generate_pom_xml(self, env, output_dir, d):
        """Generate pom.xml

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
            d (dict): dict with variables for templates
        """
        service = self.service
        root = os.path.join(output_dir, service.name)

        pom_template = env.get_template("pom_xml.template")
        pom_template.stream(d).dump(os.path.join(root, "pom.xml"))

    def generate_config(self, env, content_path):
        """Generate files in config folder

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """

    def generate_controllers(self, env, content_path):
        """Generate controller

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        controller_path = create_if_missing(
            os.path.join(content_path, "controller")
        )

        controller_data = {
            "service_name": self.service.name,
            "api": self.service.api,
            "timestamp": timestamp()
        }
        controller_template = env.get_template(
            "controller/controller.template")
        controller_template.stream(controller_data).dump(
            os.path.join(controller_path,
                         self.service.name + "Controller.java")
        )

    def generate_domain_model(self, env, content_path):
        """Generate domain model

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        domain_path = create_if_missing(os.path.join(content_path, "domain"))
        model_path = create_if_missing(os.path.join(domain_path, "model"))

        api = self.service.api

        for typedef in api.typedefs:
            data = {
                "dependency": False,
                "service_name": self.service.name,
                "name": typedef.name,
                "attributes": typedef.fields,
                "timestamp": timestamp()
            }
            class_template = env.get_template("domain/class.template")
            class_template.stream(data).dump(os.path.join(model_path,
                                             typedef.name + ".java"))

    def generate_services(self, env, content_path):
        """Generate services

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        service_path = create_if_missing(os.path.join(content_path, "service"))
        service = self.service
        service_name = service.name

        # base service
        base_path = create_if_missing(os.path.join(service_path, "base"))
        service_data = {
            "service_name": service_name,
            "package_name": service_name,
            "functions": service.api.functions,
            "dep_names": [s.name for s in service.dependencies],
            "timestamp": timestamp()
        }
        try:
            base_template = env.get_template("service/base_service.template")
            base_template.stream(service_data).dump(
                os.path.join(base_path,
                             "Base" + service_name + "Service.java"))
        except Exception:
            base_template = env.get_template("service/service_interface.template")
            base_template.stream(service_data).dump(
                os.path.join(base_path,
                             "I" + service_name + "Service.java"))

        # impl service
        impl_path = create_if_missing(os.path.join(service_path, "impl"))
        impl_file = os.path.join(impl_path, service_name + "Service.java")
        if not os.path.exists(impl_file):
            impl_template = env.get_template("service/service.template")
            impl_template.stream(service_data).dump(impl_file)

    def generate_messages(self, env, content_path):
        """Generate message objects

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        pass

    def generate_run_script(self, output_dir):
        """Generate run script for the generated application

        Args:
            env (Environment): jinja2 enviroment used during generation.
            output_dir (str): path to the output dir
        """
        generate_run_script(output_dir,
                            self.service.name,
                            self.service.version,
                            self.service.port)

        if self.service.host == HOST_CONTAINER:
            # Generate Dockerfile
            generate_dockerfile(output_dir,
                                self.service.name,
                                self.service.version,
                                self.service.port)

            # # Copy wait-for-it.sh
            # from shutil import copy2
            # src = os.path.join(get_root_path(), "silvera", "generator", "utils",
            #                    "wait-for-it.sh")
            # copy2(src, root)

    def generate(self, output_dir):
        """Generate service application.

        Args:
            output_dir (str): path to the output dir
        """
        env = self._get_env()

        service = self.service
        service_name = service.name

        java_struct(output_dir, service_name)
        root = os.path.join(output_dir, service_name)

        d = {
            "service_name": service.name,
            "service_port": "${PORT:%s}" % service.port,
            "service_version": service.version,
            "use_circuit_breaker": len(service.dependencies) > 0,
            "timestamp": timestamp(),
        }

        # Generate root files
        self.generate_bootstrap_properties(env, output_dir, d)
        self.generate_pom_xml(env, output_dir, d)

        content_path = os.path.join(root, "src", "main", "java", "com",
                                    "silvera", service_name)

        self.generate_main(env, content_path, d)
        self.generate_config(env, content_path)

        self.generate_domain_model(env, content_path)
        self.generate_controllers(env, content_path)
        self.generate_services(env, content_path)
        self.generate_messages(env, content_path)

        self.generate_run_script(output_dir)


class RPCServiceGenerator(ServiceGenerator):
    """Generates code for service that uses RPC style of communication"""

    def generate_main(self, env, content_path, d):
        super().generate_main(env, content_path, d)

        # Generate {{ServiceName}}AsyncConfiguration.java, if needed
        if self.service.has_async():
            cfg_template = env.get_template("config/config.template")
            cfg_name = self.service.name + "AsyncConfiguration.java"
            cfg_template.stream(d).dump(os.path.join(content_path, cfg_name))

    def generate_services(self, env, content_path):
        super().generate_services(env, content_path)

        # dependecy services
        service = self.service
        fns_by_service = defaultdict(list)
        for fn in service.dep_functions:
            fns_by_service[fn.service_name].append(fn)

        base_path = os.path.join(content_path, "service", "base")
        for s in service.dependencies:
            s_data = {
                "service_name": s.name,
                "package_name": service.name,
                "functions": fns_by_service[s.name],
                "use_circuit_breaker": True,
                "timestamp": timestamp()
            }
            service_template = env.get_template(
                "service/dependency_service.template")
            service_template.stream(s_data).dump(
                os.path.join(base_path,
                             s.name + "Service.java"))


class MsgServiceGenerator(ServiceGenerator):
    """Generates code for service that uses messaging as a style of
       communication."""
    def generate_config(self, env, content_path):
        cfg_path = create_if_missing(os.path.join(content_path, "config"))

        consumer_exists = len(self.service.consumes) > 0
        d = {
            "package_name": self.service.name,
            "service_name": self.service.name,
            "timestamp": timestamp(),
            "producer_exists": len(self.service.produces) > 0,
            "consumer_exists": consumer_exists
        }

        msg_template = env.get_template("config/kafka_config.template")
        msg_template.stream(d).dump(os.path.join(cfg_path, "KafkaConfig.java"))

        if consumer_exists:
            msg_pool = self.model.msg_pool

            d["messages"] = sorted(msg_pool.messages, key=lambda x: x.fqn)

            d_template = env.get_template("config/deserializer.template")
            d_template.stream(d).dump(os.path.join(cfg_path,
                                      "MessageDeserializer.java"))

    def generate_messages(self, env, content_path):
        msg_path = create_if_missing(os.path.join(content_path, "messages"))

        d = {
            "package_name": self.service.name,
            "timestamp": timestamp()
        }

        msg_template = env.get_template("message/message.template")
        msg_template.stream(d).dump(os.path.join(msg_path, "Message.java"))

        ann_template = env.get_template("message/message_annotation.template")
        ann_template.stream(d).dump(os.path.join(msg_path,
                                                 "MessageAnnotation.java"))

        field_template = env.get_template("message/message_field.template")
        field_template.stream(d).dump(os.path.join(msg_path,
                                                   "MessageField.java"))

        class_template = env.get_template("message/class.template")

        msg_pool = self.model.msg_pool

        def create_package(group, path, parent_pkg="messages"):
            """
            Creates a package for given message group, and generates
            its messages as Java classes
            """
            group_name = group.name.lower()
            curr_path = create_if_missing(os.path.join(path, group_name))

            curr_pkg = "%s.%s" % (parent_pkg, group_name)
            for msg in group.messages:
                d.update({
                    "service_name": self.service.name,
                    "pkg": curr_pkg,
                    "name": msg.name,
                    "fqn": msg.fqn,
                    "attributes": msg.fields
                })
                class_name = "%s.java" % msg.name
                class_template.stream(d).dump(os.path.join(curr_path,
                                                           class_name))

            for g in group.groups:
                create_package(g, curr_path, curr_pkg)

        # Groups will be packages
        for group in msg_pool.groups:
            create_package(group, msg_path)

    def generate_services(self, env, content_path):
        #
        # Generate services
        #
        service_path = create_if_missing(os.path.join(content_path, "service"))
        service = self.service
        service_name = service.name

        # consumers = []
        # for f service.api

        # base service
        base_path = create_if_missing(os.path.join(service_path, "base"))
        service_data = {
            "service_name": service_name,
            "package_name": service_name,
            "functions": service.api.functions,
            "dep_names": [s.name for s in service.dependencies],
            "timestamp": timestamp(),
            "consumers": service.f_consumers
        }

        base_template = env.get_template("service/service_interface.template")
        base_template.stream(service_data).dump(
            os.path.join(base_path,
                         "I" + service_name + "Service.java"))

        # impl service
        impl_path = create_if_missing(os.path.join(service_path, "impl"))
        impl_file = os.path.join(impl_path, service_name + "Service.java")
        if not os.path.exists(impl_file):
            impl_template = env.get_template("service/service.template")
            impl_template.stream(service_data).dump(impl_file)


_obj_to_fnc = {
    ConfigServerDecl: generate_config_server,
    ServiceRegistryDecl: generate_service_registry,
    ServiceDecl: generate_service,
    APIGateway: generate_api_gateway
}


def generate(decl, output_dir, debug):
    """Java 1.8 code generator.

    Args:
        decl(Decl): can be declaration of service, registry or config server.
        output_dir(str): output directory
    """
    fnc = _obj_to_fnc[decl.__class__]
    fnc(decl, output_dir)


def calculate_type(platform, _type):
    """Calculates platform type for a given Silvera type"""
    try:
        convert_complex_type(platform, _type)
    except KeyError:
        if isinstance(_type, CustomType):
            return str(_type)


def get_return_type(function):
    ret_type = convert_complex_type(JAVA, function.ret_type)

    if function.is_async():
        if ret_type == "void":
            ret_type = "Void"

        ret_type = "CompletableFuture<%s>" % ret_type

    return ret_type


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


def unfold_function_params(platform, func, with_anotations=True):
    """Creates a string from function parameters

    Args:
        platform (str): platform identifier
        func (Function): function whole params are unfolded
        with_anotations (bool): tells whether special anotations shall be
            included in string or not
    """
    if platform == JAVA:
        if with_anotations and func.http_verb == HTTP_POST:
            params = func.params
            if len(params) == 1:
                param = params[0]
                param_type = convert_complex_type(JAVA, param.type)
                return "@RequestBody %s %s" % (param_type, param.name)

        params = []
        for p in func.params:
            param = ""
            if with_anotations and p.url_placeholder:
                param = "@PathVariable "

            if with_anotations and p.query_param:
                required = "true" if p.default is None else "false"
                param = '@RequestParam(value="%s", required=%s) ' % (p.name,
                                                                     required)

            param += convert_complex_type(JAVA, p.type) + " "
            param += p.name
            params.append(param)

        return ", ".join(params)


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


def generate_run_script(output_path, app_name, app_version, app_port):
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


def generate_dockerfile(output_path, app_name, app_version, app_port):
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

    d = {"app_name": app_name,
         "app_version": app_version,
         "app_port": app_port}
    template.stream(d).dump(out)


# Create built-in Java generator.
java = GeneratorDesc(
    language_name="java",
    language_ver="1.8",
    description="Java 1.8 code generator",
    gen_func=generate
)