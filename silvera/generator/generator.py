"""
This module contains code generator for Silvera.
"""
import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from silvera.const import HOST_CONTAINER
from silvera.generator.platforms import JAVA
from silvera.utils import get_templates_path


def compose_entry(decl):
    res = {
        "name": decl.name,
        "ports": ",".join(["{0}:{0}".format(decl.port)])
    }
    return res


# Registry of all available code generators.
generators = None


def generator_for_language(language):
    """Returns the generator for a given language."""
    global generators
    try:
       return generators[language]
    except KeyError:
        raise ValueError("Could not find generator for a language \
                         '%s'" % language)


def init():
    """Initialize the generators registry."""
    global generators
    if not generators:
        from silvera.generator import java_generator

        generators = {
            JAVA: java_generator.generate
        }


def generate(model, output_dir):
    """Entry function for code generation. 
    
    Iterates over every declaration in the model and calls appropriate code
    generation function for it.

    Args:
        model(Model): Silvera model object
        output_dir(str): output directory
    """
    init()

    compose = {
        "version": "3.6",
        "services": []
    }
    for_compose = lambda x: compose["services"].append(x)

    for module in model.modules:
        for config_serv in module.config_servers:
            # Currently, config servers can only work in Java.
            generator = generator_for_language(JAVA)
            generator(config_serv, output_dir)
            if config_serv.host == HOST_CONTAINER:
                for_compose(config_serv)

        for serv_registry in module.service_registries:
            # Currently, service registry can only work in Java.
            generator = generator_for_language(JAVA)
            generator(serv_registry, output_dir)
            if serv_registry.host == HOST_CONTAINER:
                for_compose(serv_registry)

        for service in module.service_instances:
            lang = service.type.lang
            generator = generator_for_language(lang)
            generator(service, output_dir)
            if service.type.host == HOST_CONTAINER:
                for_compose(service)

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
