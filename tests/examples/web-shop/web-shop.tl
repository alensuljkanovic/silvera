config-server ConfigServer {
    version="0.0.1"
    port=9090
    search_path="file://${user.home}/Projects/MicroServiceProps/centralProperties/"
}

service-registry ServiceRegistry{
    version="0.0.1"
    tool=eureka
    port=9091
    uri="http://localhost"
    client_mode=False
}

service UserService {
    version="0.0.1"
    port=8080
    config_server=ConfigServer
    service_registry=ServiceRegistry
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
    }

    communication_style=REST

    api {
        typedef User [
            str id
            str password
            PaymentDetail paymentDetail
            UserDetail userDetail
            bool active
            str createdBy
            str deletedBy
        ]

        typedef UserDetail [
            str firstName
            str lastName
            str address
            int age
            int gender
        ]

        typedef PaymentDetail [
            str cardType
            str cardNumber
            date validFrom
            date validTo
        ]

        User login(str userId, str password)
        bool checkUser(str userId)
        bool register(User user)
        PaymentDetail getPaymentInfo(str userId)
        bool checkPaymentInfo(str userId)

    }
}

service PaymentService {
    version="0.0.1"
    port=8081
    config_server=ConfigServer
    service_registry=ServiceRegistry
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
    }

    communication_style=REST

    api {
        typedef Payment [
            str id
            str userId
            str shoppingCartId
            str currency
            str cardId
            date paymentDate
        ]

        Payment createPayment(Payment payment)


    }
}

service ShoppingCartService {
    version="0.0.1"
    port=8082
    config_server=ConfigServer
    service_registry=ServiceRegistry
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
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

        ShoppingCart createShoppingCart(ShoppingCart cart)
    }
}

service ProductService {
    version="0.0.1"
    port=8083
    config_server=ConfigServer
    service_registry=ServiceRegistry
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
    }

    communication_style=REST

    api {
        typedef Product [
            str id
            int qty
            bool active
            str name
            str description
            double price
        ]

        int getProductQTY(str productId)
        Product getProduct(int productId)
        bool checkProduct(int productId)
    }
}


connection PaymentService -> UserService {
    checkPaymentInfo[fail_fast]
}


connection PaymentService -> ProductService {
    getProductQTY[fallback_method getProductQTYFallback]
}


connection ShoppingCartService -> UserService {
    checkUser[fail_silent]
}


connection ShoppingCartService -> ProductService {
    checkProduct[fail_silent]
}


