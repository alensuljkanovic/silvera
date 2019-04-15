// This example tests RESTResolver

service TestService {

    deployment {
        version="1.0.0"
    }

    communication_style=REST

    api {
        typedef CustomObject [
            str id
            int qty
            str description
        ]

        @rest(method=POST)
        void addCustomObject(CustomObject o)
    }
}
