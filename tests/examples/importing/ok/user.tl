import "share.setup.tl"

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