service-registry ServiceRegistry{
    tool=eureka
    client_mode=False
    deployment {
        version="0.0.1"
        port=9091
        url="http://loc_reg"
    }
}