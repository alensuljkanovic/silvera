// This example tests RESTResolver

service TestService {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef CustomObject [
            str id
            int qty
            str description
        ]

        void getAll()
    }
}
