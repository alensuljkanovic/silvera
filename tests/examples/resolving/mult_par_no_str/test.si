// This example tests RESTResolver

service TestService {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef CustomObject [
            str id
            str name
            int qty
            str description
        ]

        void getObject(str name, str description)
    }
}
