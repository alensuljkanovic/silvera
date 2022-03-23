# Deployment

Deployment is used to describe how Deployable ([service](service.md), [service registry](service_registry.md), [API gateway](api_gateway.md) or [configuration server](configuration_server.md)) object will be deployed.

Deployment contains following attributes:

* **version** (optional) - defines a version of Deployable object,
* **url** (optional) - defines an URL where can be reached,
* **port** (optional) - defines a port where can be reached,
* **lang** (optional) - defines a programming language to be used as a target language,
* **host** (optional) - defines a host of the generated code (PC or container),
* **replicas** (optional) - defines a number of service replicas which will be started,
* **restart_policy** (optional) - defines a restart policy for a service.

!!! note

    Current version of Silvera has no support for replicas and restart_policy. Model will be compiled, but these attributes will be ignored.

Following example shows how deployable can be defined:

```
deployment {
    version="0.0.1"
    port=9091
    url="http://localhost"
    host=container
}
```

If `lang` is omitted, Silvera will generate Java source code.