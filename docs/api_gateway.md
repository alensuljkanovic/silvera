# API gateway

API gateway is the single entry point for all clients. Using API gateway comes with
several benefits. Most notable are following:

* Client is unaware of the structure of the application,
* It's easier for client to determine location of service instances,
* Reduces the number of requests or roundtrips,...

!!! note

    More information about the API gateway design pattern can be found here: 
    [https://microservices.io/patterns/apigateway.html](https://microservices.io/patterns/apigateway.html)

## How to define an API gateway

In the following example, we will define a service registry named `EntryPoint`:

```
api-gateway EntryPoint {
    // gateway will be registered within ServiceRegistry instance
    service_registry = ServiceRegistry

    deployment {
        version="0.0.1"
        port=9095
        url="http://localhost"
        host=container
    }

    communication_style=rpc

    gateway-for {
        User as /api/u
        Order as /api/o
        ...
    }
}
```

API gateway has following attributes:

* **name** (mandatory) - name of the API gateway.
* **service_registry** (optional) - reference to a [service registry](service_registry.md) where the service will be registered,
* **deployment** (optional) - tells how gateway will be deployed (more info can be found [here](deployment.md)),
* **gateway-for** (mandatory) - Maps service instance to URL. By using this URL, clients can reach
corresponding the service.