// This example tests RESTResolver

service PrintService {

    deployment {
        version="1.0.0"
    }

    communication_style=REST

    api {
        typedef Document [
            int id
            str name
            str content
        ]

        @rest(method=GET)
        void print(int id)
    }
}

service OfficeService {

     deployment {
        version="1.0.0"
    }

    communication_style=REST

    api {
        typedef Worker [
            str first_name
            str last_name
        ]

        @rest(method=POST)
        void addWorker(str first_name, str last_name)
    }
}

connection OfficeService -> PrintService {
    print[fail_fast]
}
