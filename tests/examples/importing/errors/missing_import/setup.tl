config-server ConfigServer {

    search_path="file://${user.home}/Projects/MicroServiceProps/centralProperties/"
    deployment {
        version="0.0.1"
        port=9090
    }
}

service-registry ServiceRegistry{
    tool=eureka
    client_mode=False
    deployment {
        version="0.0.1"
        port=9091
        url="http://localhost"
    }
}