import "share.setup.tl"
import "user.tl"
import "product.tl"

service ShoppingCartService {

    config_server=share.setup.ConfigServer
    service_registry=share.setup.ServiceRegistry

    deployment {
        version="0.0.1"
        port=8082
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=REST

    api {
        typedef ShoppingCart [
            str id
            str userId
            date date
            double sumPrice
            CartItem items
        ]

        typedef CartItem [
            str productId
            str productName
            int qty
            double productPrice
        ]

        @rest(method=POST)
        ShoppingCart createShoppingCart(ShoppingCart cart)
    }
}


connection ShoppingCartService -> user.UserService {
    checkUser[fail_silent]
}


connection ShoppingCartService -> product.ProductService {
    checkProduct[fail_silent]
}