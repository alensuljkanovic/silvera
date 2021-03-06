# Service Registry

Service registry is database of services. It contains information about all service instances and their locations.

If used, client service can use service registry to determine the location of a service instance to which it wants to send requests.

!!! note

    More information about the Service Registry design pattern can be found here: 
    [https://microservices.io/patterns/apigateway.html](https://microservices.io/patterns/apigateway.html)


## How to define a service registry


In the following example, we will define a service registry named `ServiceRegistry`:

```java
service_registry ServiceRegistry {
    client_mode=False
    deployment {
        version="0.0.1"
        port=9091
        url="http://localhost"
        host=container
    }
}

```

As seen above, service registry has following attributes:

* **name** (mandatory) - name of the service registry.
* ~~**tool** (mandatory) - defines which tool will be used as a service registry. Currently, *Silvera* supports only Eureka~~ *This attribute is removed in version 0.3.0*.
* **client_mode** (mandatory) - defines whether service registry can be registered within another service registry or not.
* **deployment** (mandatory) - defines how registry will be deployed. Attributes of deployment
are defined [here](deployment.md).

!!! warning
    
    The attribute `tool` is removed in version 0.3.0. Which service registry implementation
    will be used in now decided in the code generators.
