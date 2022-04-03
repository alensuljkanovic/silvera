"""This module contains functions used to quickly create project"""
import os


def create_setup(file_dir, registry_name, registry_port, config_name,
                 config_path, config_port):
    # reg_name, reg_port = registry

    if not config_name:
        config_name = "ConfigServer"

    if not config_path:
        config_path = ""

    if not config_port:
        config_port = 9090

    content = "config-server %s {\n" % config_name
    content += '\tsearch_path="%s"\n' % config_path
    content += "\tdeployment {\n"
    content += '\t\tversion="0.0.1"\n'
    content += '\t\tport=%s\n' % config_port
    content += "\t}\n"
    content += "}\n\n"

    print("\tGenerated config-server: %s at port %s" % (config_name,
                                                        config_port))

    if not registry_name:
        registry_name = "ServiceRegistry"

    if not registry_port:
        registry_port = 9091

    content += "service-registry %s {\n" % registry_name
    content += "\tclient_mode=False\n"
    content += "\tdeployment {\n"
    content += '\t\tversion="0.0.1"\n'
    content += '\t\tport=%s\n' % registry_port
    content += '\t\turl="http://localhost"\n'
    content += "\t}\n"
    content += "}\n"

    print("\tGenerated service registry: %s at port %s" % (registry_name,
                                                           registry_port))

    with open(os.path.join(file_dir, "setup.si"), "w") as f:
        f.write(content)


def create_messaging(file_dir):

    content = "msg-pool {\n"
    content += "\t// define example msg group\n"
    content += "\tgroup ExampleMsgGroup [\n"
    content += "\t\tmsg EXAMPLE_EVENT []\n"
    content += "\t]\n"
    content += "}\n"

    content += "msg-broker Broker {\n"
    content += "\t channel EV_EXAMPLE_EVENT_CHANEL(ExampleMsgGroup.EXAMPLE_EVENT)\n"
    content += "}\n"

    with open(os.path.join(file_dir, "messaging.si"), "w") as f:
        f.write(content)


def create_service(name, registry, comm, port):
    """Generates service file for given service

    Args:
        name (str): service name
        registry (str): name of the service registry
        comm (str): service's communication style
        port (int): service's port
    """
    pass
