"""This module contains classes that implement support for
OpenAPI specification.
"""
import os
import json

from silvera.const import BASIC_TYPES
from silvera.core import TypedList, TypedSet, TypedDict


class OpenAPISerializer:
    """OpenAPI serializer.

    Serializes service declarations into OpenAPI compatible Python dicts.
    Currently supports OpenAPI 3.0.0.
    """
    def __init__(self):
        self.version = "3.0.0"

    def type_map(self, silvera_type):
        return {
            # int
            "i64": ("integer", "i64"),
            "i32": ("integer", "i32"),
            "int": ("integer", "i64"),
            "bool": ("boolean", None),
            # string
            "str": ("string", None),
            "pwd": ("string", "password"),
            "date": ("string", "date"),
            # number
            "double": ("number", "double"),
            "float": ("number", "float"),
        }[silvera_type]

    def _create_paths(self, service_decl):
        """Creates content for `paths` section.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        def _read_update_delete(operation, obj_name):
            ret_val = {
                "description": "%s %s object." % (operation.title(),
                                                  obj_name),
                "operationId": "%s%s" % (operation, obj_name),
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "ID of %s to update" % obj_name.lower(),
                        "required": True,
                        "schema": {
                            "type": "string",
                        }
                    }
                ],
                "requestBody": {
                    "$ref": "#components/requestBodies/%sBody" % obj_name
                },
                "responses": {
                    "200": {
                        "$ref": "#components/responses/%sOK" % obj_name
                    }
                }
            }
            return ret_val

        paths = {}

        #
        # Domain objects (typedefs)
        #
        for obj_name, obj in service_decl.domain_objs.items():
            if obj.crud:
                post_path = "/%s" % obj_name.lower()
                # POST (path: /obj_name)
                if "@create" in obj.crud_dict:
                    d = {
                        "description": "Creates a new %s." % obj_name.lower(),
                        "operationId": "create%s" % obj_name,
                        "requestBody": {
                            "description": "%s to add." % obj_name,
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#components/schemas/%s" % obj_name
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "$ref": "#components/responses/%sOK" % obj_name
                            }
                        }
                    }
                    paths[post_path] = {"post": d}

                id_path = "/%s/id" % obj_name.lower()
                # PUT (path: /obj_name/ID)
                if "@update" in obj.crud_dict:
                    d = _read_update_delete("update", obj_name)
                    d["requestBody"] = {
                        "$ref": "#components/requestBodies/%sBody" % obj_name
                    }
                    if id_path not in paths:
                        paths[id_path] = {}

                    paths[id_path].update({"put": d})

                if "@read" in obj.crud_dict:
                    d = _read_update_delete("read", obj_name)
                    if id_path not in paths:
                        paths[id_path] = {}

                    paths[id_path].update({"get": d})

                if "@delete" in obj.crud_dict:
                    d = _read_update_delete("delete", obj_name)
                    if id_path not in paths:
                        paths[id_path] = {}

                    paths[id_path].update({"delete": d})

        #
        # User-added API fuctions
        #
        for function in service_decl.api.functions:
            if function.rest_path:
                path = "/%s" % function.rest_path
                if path not in paths:
                    paths[path] = {}

                if function.docstring:
                    descr = function.docstring.split()[0]
                else:
                    descr = ""

                d = {
                    "description": descr,
                    "operationId": function.name,
                }

                self._func_params(function, d)
                self._func_resp_bodies(function, d)

                paths[path].update({function.http_verb.lower(): d})

        return paths

    def _func_params(self, function, d):
        """Creates `parameters` section based on function params.

        Args:
            function (Function): function object
            d (dict): OpenAPI spec dict
        """
        # List with function parameters whose type is a Silvera
        # built-in type
        simple_params = []
        # List with function parameters whose type is complex type
        # These parameters will be sent in the request body.
        complex_params = []
        for p in function.params:
            if p.type in BASIC_TYPES:
                simple_params.append(p)
            else:
                complex_params.append(p)

        params_section = []
        for param in simple_params:
            params_section.append({
                "name": param.name,
                "in": "query" if param.query_param else "path",
                "required": True,
                "schema": {
                    "type": self.type_map(param.type)[0]
                }
            })

        d["parameters"] = params_section

        if complex_params:
            param = complex_params[0]
            rb = {
                "description": "JSON representation object",
                "required": True,
            }
            if isinstance(param.type, (TypedList, TypedSet)):
                list_type = param.type.type
                rb["content"] = {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#components/schemas/%s" % list_type.name
                            }
                        }
                    }
                }
            else:
                rb["content"] = {
                    "application/json": {
                        "schema": {
                            "$ref": "#components/schemas/%s" % param.type.name
                        }
                    }
                }
            d["requestBody"] = rb

    def _func_resp_bodies(self, function, d):
        """Creates `responses` section for user defined API functions.

        Args:
            function (Function): function object
            d (dict): OpenAPI spec dict
        """
        if function.ret_type == "void":
            # functions with void return type generate empty responses
            d.update({
                "responses": {
                    200: {
                        "description": "",
                        "content": {}
                    }
                }
            })
            return

        if isinstance(function.ret_type, (TypedList, TypedSet)):
            list_type = function.ret_type.type
            type_name = list_type
            try:
                # list of built-in types
                _type, _ = self.type_map(list_type)
                resp_items = {"type": _type}
            except KeyError:
                # list of complex objects (typedefs)
                resp_items = {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/%s" % type_name
                    }

                }
        else:
            try:
                # Silvera built-in types
                _type, _ = self.type_map(function.ret_type)
                resp_items = {"type": _type}
                type_name = _type
            except KeyError:
                # Typedefs
                type_name = function.ret_type.name
                resp_items = {
                    "$ref": "#/components/schemas/%s" % type_name
                }

        d.update({
            "responses": {
                200: {
                    "description": "JSON representation of %s "
                                   "object" % type_name,
                    "content": {
                        "application/json": {
                            "schema": resp_items
                        }
                    }
                }
            }
        })

    def _create_schemas(self, service_decl):
        """Creates content for`schemas` section.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        def _create_properties(domain_obj):
            required = []
            properties = {}
            for field in domain_obj.fields:
                if field.required:
                    required.append(field.name)

                if isinstance(field.type, (TypedList, TypedSet)):
                    properties[field.name] = {
                        "type": "array"
                    }
                    try:
                        _type, _format = self.type_map(field.type.type)
                        items = {"items": {"type": _type}}
                        properties[field.name].update(items)
                    except KeyError:
                        items = {
                            "items": {
                                "$ref": "#/components/schemas/%s" % field.type.type
                            }
                        }
                        properties[field.name].update(items)
                elif isinstance(field.type, TypedDict):
                    properties[field.name] = {
                        "type": "object"
                    }
                    try:
                        _type, _format = self.type_map(field.value_type)
                        items = {"additionalProperties": {"type": _type}}
                        properties[field.name].update(items)
                    except KeyError:
                        items = {
                            "additionalProperties": {
                                "$ref": "#/components/schemas/%s" % field.value_type
                            }
                        }
                        properties[field.name].update(items)
                else:
                    try:
                        # Silvera built-in type
                        _type, _format = self.type_map(field.type)
                        properties[field.name] = {
                            "type": _type
                        }
                        if _format:
                            properties[field.name].update({
                                "format": _format
                            })
                    except KeyError:
                        # Complex type
                        _format = None
                        properties[field.name] = {
                            "$ref": '#/components/schemas/%s' % field.type.name
                        }

            return required, properties

        schemas = {}
        for obj_name, obj in service_decl.domain_objs.items():
            req, props = _create_properties(obj)
            d = {
                "type": "object",
                "properties": props
            }
            if req:
                d["required"] = req
            schemas[obj_name] = d

        return schemas

    def _create_req_bodies(self, service_decl):
        """Creates content for `requestBodies` section.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        bodies = {}
        for obj_name, obj in service_decl.domain_objs.items():
            bodies["%sBody" % obj_name] = {
                "description": "JSON representation of %s object" % obj_name,
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#components/schemas/%s" % obj_name
                        }
                    }
                }
            }

        return bodies

    def _create_resp(self, service_decl):
        """Creates content for`responses` section.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        resp = {}
        for obj_name, obj in service_decl.domain_objs.items():
            resp["%sOK" % obj_name] = {
                "description": "JSON representation of %s object" % obj_name,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#components/schemas/%s" % obj_name
                        }
                    }
                }
            }

        return resp

    def _create_servers(self, service_decl):
        """Creates content for`servers` section.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        servers = [{"url": u} for u in service_decl.gateway_urls()]

        # If there are no API Gateways
        if not servers:
            service_url = service_decl.deployment.url
            service_url = service_url if service_url is not None else ""
            servers.append({"url": service_url})

        return servers

    def serialize(self, service_decl):
        """Serializes service declaration into dict that supports OpenAPI
        specification.

        Args:
            service_decl(ServiceDecl): service declaration object

        Returns:
            dict
        """
        deployment = service_decl.deployment
        if service_decl.docstring:
            description = service_decl.docstring.split("\n")[0].strip()
        else:
            description = ""

        data = {
            "openapi": self.version,
            "info": {
                "version": deployment.version,
                "title": service_decl.name,
                "description": description
            },
            "servers": self._create_servers(service_decl),
            "paths": self._create_paths(service_decl),
            "components": {
                "schemas": self._create_schemas(service_decl),
                "requestBodies": self._create_req_bodies(service_decl),
                "responses": self._create_resp(service_decl)
            }
        }

        return data


class OpenAPIDump:
    """Creates OpenAPI JSON file for given service declaration."""

    @staticmethod
    def dump(service_decl, output_dir):
        """Creates OpenAPI JSON file for given service declaration.

        Args:
            service_decl (ServiceDecl): service declaration object
            output_dir (str): output directory
        """
        serializer = OpenAPISerializer()
        data = serializer.serialize(service_decl)
        openapi_file = os.path.join(output_dir, "openapi.json")

        with open(openapi_file, "w") as f:
            f.write(json.dumps(data))
