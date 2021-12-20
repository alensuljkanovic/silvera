"""
This module contains code generator for Silvera.
"""
import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from silvera.generator.registration import generator_for_language
from silvera.const import HOST_CONTAINER
from silvera.openapi.serialization import OpenAPIDump
from silvera.utils import get_templates_path
from silvera.generator.platforms import JAVA


def compose_entry(decl):
    res = {
        "name": decl.name,
        "ports": ",".join(["{0}:{0}".format(decl.port)])
    }
    return res


def generate(model, output_dir, debug=False):
    """Entry function for code generation.

    Iterates over every declaration in the model and calls appropriate code
    generation function for it.

    Args:
        model(Model): Silvera model object
        output_dir(str): output directory
        debug (bool): debug flag
    """

    compose = {
        "version": "3.6",
        "services": []
    }
    for_compose = lambda x: compose["services"].append(x)

    for module in model.modules:
        for config_serv in module.config_servers:
            # Currently, config servers can only work in Java.
            generator = generator_for_language(JAVA)
            generator(config_serv, output_dir, debug)
            if config_serv.host == HOST_CONTAINER:
                for_compose(config_serv)

        for serv_registry in module.service_registries:
            # Currently, service registry can only work in Java.
            generator = generator_for_language(JAVA)
            generator(serv_registry, output_dir, debug)
            if serv_registry.host == HOST_CONTAINER:
                for_compose(serv_registry)

        for gt in module.api_gateways:
            # Currently, API Gateways can only work in Java.
            generator = generator_for_language(JAVA)
            generator(gt, output_dir, debug)
            if gt.host == HOST_CONTAINER:
                for_compose(gt)

        for service in module.services:
            lang = service.lang
            # port = service.port
            generator = generator_for_language(lang)

            generator(service, output_dir, debug)
            if service.host == HOST_CONTAINER:
                for_compose(service)

            OpenAPIDump.dump(service, os.path.join(output_dir, service.name))

    if compose["services"]:
        _generate_docker_compose(output_dir, compose)


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
