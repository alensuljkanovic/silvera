service-registry ServiceRegistry{
    tool=eureka
    client_mode=False
    deployment {
        version="0.0.1"
        port=9092
        url="http://loc_reg2"
    }
}