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

service UserService {

    config_server=ConfigServer
    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
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

        @rest(method=POST)
        bool checkUser(str userId)

        @rest(method=POST)
        bool register(User user)

        @rest(method=GET)
        PaymentDetail getPaymentInfo(str userId)

        @rest(method=POST)
        bool checkPaymentInfo(str userId)

    }
}

service PaymentService {

    config_server=ConfigServer
    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8081
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
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

        @rest(method=POST)
        Payment createPayment(Payment payment)


    }
}

service ShoppingCartService {

    config_server=ConfigServer
    service_registry=ServiceRegistry

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

service ProductService {

    config_server=ConfigServer
    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8083
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
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

        @rest(method=GET)
        int getProductQTY(str productId)

        @rest(method=GET)
        Product getProduct(int productId)

        @rest(method=GET)
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


