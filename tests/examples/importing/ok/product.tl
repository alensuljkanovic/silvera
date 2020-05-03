import "share.setup.tl"

service ProductService {

    config_server=share.setup.ConfigServer
    service_registry=share.setup.ServiceRegistry

    deployment {
        version="0.0.1"
        port=8083
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {
        typedef Product [
            str id
            int qty
            bool active
            str name
            str description
            double price
        ]

        @rest(method=GET)
        int getProductQTY(str productId)

        @rest(method=GET)
        Product getProduct(int productId)

        @rest(method=GET)
        bool checkProduct(int productId)
    }
}