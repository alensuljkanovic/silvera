# Configuration server

Enables centralized configuration. Here's how to define one:

```
config-server ConfigServer {

    // path to the properties folder
    search_path="file://${user.home}/Projects/MicroServiceProps/centralProperties/"

    deployment {
        version="0.0.1"
        port=9090
    }
}
```