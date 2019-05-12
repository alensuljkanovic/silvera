import "share.setup.tl"
import "user.tl"
import "product.tl"

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

connection PaymentService -> UserService {
    checkPaymentInfo[fail_fast]
}


connection PaymentService -> ProductService {
    getProductQTY[fallback_method getProductQTYFallback]
}
