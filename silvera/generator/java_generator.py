import os
import warnings
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from silvera.const import HOST_CONTAINER, HTTP_POST
from silvera.core import (CustomType, ConfigServerDecl, ServiceRegistryDecl,
                          ServiceDecl, APIGateway, TypeDef)
from silvera.generator.platforms import (
    JAVA, convert_complex_type, get_def_ret_val, is_collection, convert_list_to_array
)
from silvera.utils import get_templates_path
from silvera.generator.registration import GeneratorDesc
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
    # Generate application.properties
    #
    application_template = env.get_template("application_properties.template")
    application_template.stream(d).dump(os.path.join(res_path,
                                                     "application.properties"))
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
    # Generate application.properties
    #
    application_template = env.get_template("eureka_application.template")
    application_template.stream(d).dump(os.path.join(res_path,
                                                     "application.properties"))

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
        "gateway_for": [(g.service.name, g.path, g.service.port,
                         g.service.service_registry is not None)
                        for g in api_gateway.gateway_for],
        "timestamp": timestamp(),
        "user_service_registry": user_service_registry
    }

    gt_path = os.path.join(output_dir, gname)
    res_path = os.path.join(gt_path, "src", "main", "resources")
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    #
    # Generate application.properties
    #
    application_template = env.get_template("application_properties.template")
    application_template.stream(d).dump(os.path.join(res_path,
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
        - application.properties
        - pom.xml
    """
    if service.uses_messaging:
        generator = MsgServiceGenerator(service)
    else:
        generator = RPCServiceGenerator(service)

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
            "messaging" if self.service.uses_messaging else "rpc"
        )

        self.model = service.parent.model

    def _get_env(self):
        env = Environment(loader=FileSystemLoader(self._templates_path))
        env.filters["firstupper"] = lambda x: x[0].upper() + x[1:]
        env.filters["firstlower"] = lambda x: x[0].lower() + x[1:]
        env.filters["converttype"] = lambda x: convert_complex_type(JAVA, x)
        env.filters["convertlisttoarray"] = lambda x: convert_list_to_array(
            JAVA, x
        )
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
        env.globals["get_produced_messages"] = get_produced_messages

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

    def generate_application_properties(self, env, output_dir, d):
        """Generate application.properties

        Args:
            env (Environment): jinja2 environment used during generation.
            output_dir (str): path to the parent folder in generated project
            d (dict): dict with variables for templates
        """

        service = self.service
        root = os.path.join(output_dir, service.name)
        res_path = os.path.join(root, "src", "main", "resources")

        application_template = env.get_template("application_properties.template")

        if service.config_server:
            d["config_server_uri"] = "http://localhost:%s" % \
                                      service.config_server.port

        if service.service_registry:
            reg = service.service_registry
            url = "%s:%s/eureka" % (reg.url, reg.port)
            d["service_registry_url"] = url

        application_template.stream(d).dump(os.path.join(res_path,
                                                         "application.properties"))

    def generate_pom_xml(self, env, output_dir, d):
        """Generate pom.xml

        Args:
            env (Environment): jinja2 enviroment used during generation.
            output_dir (str): path to the parent folder in generated project
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
            "timestamp": timestamp(),
            "typedefs": self.get_typedefs(self.service),
            "consumers_per_message": self.get_consumers_per_message()
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

            attrs = typedef.fields
            id_attr = None
            for attr in attrs:
                if attr.isid:
                    id_attr = {"name": attr.name,
                               "type": attr.type}

            data = {
                "dependency": False,
                "service_name": self.service.name,
                "name": typedef.name,
                "attributes": attrs,
                "id_attr": id_attr,
                "timestamp": timestamp()
            }
            class_template = env.get_template("domain/class.template")
            class_template.stream(data).dump(os.path.join(model_path,
                                             typedef.name + ".java"))

        if self.service.dep_typedefs:
            # domain dependency classes
            dependencies_path = create_if_missing(
                os.path.join(domain_path, "dependencies")
            )
            for typedef in self.service.dep_typedefs:
                data = {
                    "dependency": True,
                    "service_name": self.service.name,
                    "name": typedef.name,
                    "attributes": typedef.fields,
                    "timestamp": timestamp()
                }
                class_template = env.get_template("domain/class.template")
                class_template.stream(data).dump(
                    os.path.join(dependencies_path, typedef.name + ".java")
                )

    def generate_repositories(self, env, content_path):
        """Generate repository folder

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        repo_path = create_if_missing(os.path.join(content_path, "repository"))

        api = self.service.api

        for typedef in api.typedefs:

            id_datatype = "str"
            for field in typedef.fields:
                if field.isid:
                    id_datatype = field.type

            data = {
                "service_name": self.service.name,
                "timestamp": timestamp(),
                "typedef": typedef.name,
                "id_datatype": id_datatype
            }
            class_template = env.get_template("repository/repository.template")
            class_template.stream(data).dump(os.path.join(repo_path,
                                             typedef.name + "Repository.java"))

    def generate_services(self, env, content_path):
        """Generate services

        Args:
            env (Environment): jinja2 enviroment used during generation.
            content_path (str): path to the parent folder in generated project
        """
        service_path = create_if_missing(os.path.join(content_path, "service"))
        service = self.service
        service_name = service.name

        typedefs = self.get_typedefs(service)

        # base service
        base_path = create_if_missing(os.path.join(service_path, "base"))
        service_data = {
            "service_name": service_name,
            "package_name": service_name,
            "functions": service.api.functions,
            "typedefs": typedefs,
            "dep_names": [s.name for s in service.dependencies],
            "timestamp": timestamp(),
            "consumers": service.f_consumers,
            "produced_msgs": self.get_produced_msgs(),
            "consumed_msgs": self.get_consumed_msgs(),
            "consumers_per_message": self.get_consumers_per_message()
        }

        base_template = env.get_template("service/service_interface.template")
        base_template.stream(service_data).dump(
            os.path.join(base_path, "I" + service_name + "Service.java")
        )

        # impl service
        impl_path = create_if_missing(os.path.join(service_path, "impl"))
        impl_file = os.path.join(impl_path, service_name + "Service.java")
        if not os.path.exists(impl_file):
            impl_template = env.get_template("service/service.template")
            impl_template.stream(service_data).dump(impl_file)

        if service.dependencies:
            self.generate_serv_dependencies(env, service, content_path)

    def generate_serv_dependencies(self, env, service, content_path):
        dp_path = os.path.join(content_path, "service", "dependencies")
        create_if_missing(dp_path)

        fns_by_service = defaultdict(list)
        use_circuit_breaker = False
        for fn in service.dep_functions:
            if fn.cb_pattern not in {None, "fail_fast"}:
                use_circuit_breaker = True
            fns_by_service[fn.service_name].append(fn)

        for s in service.dependencies:
            s_data = {
                "service_name": s.name,
                "package_name": service.name,
                "functions": fns_by_service[s.name],
                "has_domain_dependencies": len(service.dep_typedefs) > 0,
                "use_circuit_breaker": use_circuit_breaker,
                "timestamp": timestamp(),
                "uses_registry": True if s.service_registry else False,
                "service_url": "%s:%s" % (s.url, s.port)
            }
            service_template = env.get_template(
                "service/dependency_service.template")
            service_template.stream(s_data).dump(
                os.path.join(dp_path,
                             s.name + "Client.java"))

    def get_typedefs(self, service):
        """For given service returns type with typedef names and type of the
        ID attribute

        Args:
            service (ServiceDecl): service declaration

        Returns:
            tuple
        """
        typedefs = []
        for t in service.api.typedefs:
            if not t.crud:
                continue
            # if ID is not specified, the type of generated key will be str
            id_datatype = "str"
            for field in t.fields:
                if field.isid:
                    id_datatype = field.type

            typedefs.append((t.name, id_datatype, t.crud_dict))
        return typedefs

    def get_consumed_msgs(self):
        """Returns collection of FQNs of consumed messages"""
        return self._get_msgs(self.service.consumes)

    def get_produced_msgs(self):
        """Returns collection of FQNs of produced messages"""
        return self._get_msgs(self.service.produces)

    def _get_msgs(self, collection):
        """Returns collection of FQNs messages from given collection."""
        result = []
        for msg_obj in collection:
            result.append(_build_msg_fqn(msg_obj))
        return result

    def get_consumed_channels(self):
        """Returns collection of consumed channels"""
        result = set()
        for v in self.service.consumes.values():
            for ch in v:
                result.add(ch.name)
        return result

    def get_consumers_per_message(self):
        """Returns message FQN to function mappings."""
        result = {}
        for msg_obj, values in self.service.consumers_per_message.items():
            result[_build_msg_fqn(msg_obj)] = values
        return result

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
            "uses_registry": service.service_registry is not None
        }

        # Generate root files
        self.generate_application_properties(env, output_dir, d)
        self.generate_pom_xml(env, output_dir, d)

        content_path = os.path.join(root, "src", "main", "java", "com",
                                    "silvera", service_name)

        self.generate_main(env, content_path, d)
        self.generate_config(env, content_path)

        self.generate_domain_model(env, content_path)
        self.generate_repositories(env, content_path)
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


class MsgServiceGenerator(ServiceGenerator):
    """Generates code for service that uses messaging as a style of
       communication."""
    def generate_config(self, env, content_path):
        cfg_path = create_if_missing(os.path.join(content_path, "config"))

        def get_produced_msgs(service):
            """Returns the list of message FQN produced by the service."""
            msgs = set({_build_msg_fqn(m)
                        for m in service.produces.keys()})
            for t in service.api.typedefs:
                msgs.update({_build_msg_fqn(m) for m in t.produces})

            return sorted(msgs)

        consumed_msgs = self.get_consumed_msgs()
        consumed_channels = self.get_consumed_channels()

        d = {
            "package_name": self.service.name,
            "service_name": self.service.name,
            "timestamp": timestamp(),
            "produced_msgs": get_produced_msgs(self.service),
            "consumed_msgs": consumed_msgs,
            "consumed_channels": consumed_channels
        }

        msg_template = env.get_template("config/kafka_config.template")
        msg_template.stream(d).dump(os.path.join(cfg_path, "KafkaConfig.java"))

        # NOTE: This probably is not needed, for now.
        # if consumed_msgs:
        #     msg_pool = self.model.msg_pool
        #
        #     d["messages"] = sorted(msg_pool.messages, key=lambda x: x.fqn)
        #
        #     d_template = env.get_template("config/deserializer.template")
        #     d_template.stream(d).dump(os.path.join(cfg_path,
        #                               "MessageDeserializer.java"))

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
    return ", ".join(params) if params else ""


def get_produced_messages(func):
    """Returns a list of message fqn and channel pairs.

    Args:
        func (Function): function object
    Returns:
        list
    """
    result = []
    for msg, channel in func.produces:
        result.append((_build_msg_fqn(msg), channel))
    return result


def _build_msg_fqn(msg_obj):
    """Build FQN in form of package name."""
    if "." in msg_obj.fqn:
        values = msg_obj.fqn.split(".")
        pkg = ".".join(values[:-1]).lower()
        fqn = pkg + "." + msg_obj.name
        return fqn
    else:
        return msg_obj.name


def generate_cb_annotation(func):
    if not func.cb_pattern or func.cb_pattern == "fail_fast":
        return ""

    return '@HystrixCommand(fallbackMethod = "%s")' % func.cb_fallback


def get_default_for_cb_pattern(platform, func):

    if platform == JAVA:
        if func.cb_pattern in ("fallback_method", "fallback_static"):
            return get_def_ret_val(platform, func.ret_type)
        elif func.cb_pattern == "fallback_stubbed":
            if isinstance(func.ret_type, TypeDef):
                return "new {}()".format(func.ret_type.name)
            else:
                return get_def_ret_val(platform, func.ret_type)
        elif func.cb_pattern == "fail_silent":
            warnings.warn("Circuit Breaker pattern 'fail_silent' returns "
                          "default value instead of empty response. Sorry :(. ")
            return get_def_ret_val(platform, func.ret_type)
        elif func.cb_pattern == "fallback_cache":
            warnings.warn("Circuit Breaker pattern 'fallback_cache' returns "
                          "default value instead of cached value. Sorry :(. ")
            return get_def_ret_val(platform, func.ret_type)


def get_rest_call(platform, func):
    """Returns the REST URL towards the function of the service that current
    service depends upon"""
    if platform == JAVA:
        port = func.dep.parent.parent.port
        url = 'http://localhost:%s' % port

        rest_mapping = func.dep.rest_path
        return "/" + rest_mapping
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
            if with_anotations:
                if p.url_placeholder:
                    param = "@PathVariable "
                elif p.query_param:
                    required = "true" if p.default is None else "false"
                    param = '@RequestParam(value="%s", required=%s) ' % (p.name,
                                                                         required)
                else:
                    param = "@RequestBody "
            # if with_anotations and p.query_param:
            #     required = "true" if p.default is None else "false"
            #     param = '@RequestParam(value="%s", required=%s) ' % (p.name,
            #                                                          required)

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

    d = {"name": app_name, "version": app_version, "port": app_port}
    for template_name, ext in [("run_sh", "sh"), ("run_cmd", "cmd")]:
        run_template = env.get_template("%s.template" % template_name)

        out = os.path.join(output_path, app_name, "run.%s" % ext)

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
    language_ver="17",
    description="Java 17 code generator",
    gen_func=generate
)