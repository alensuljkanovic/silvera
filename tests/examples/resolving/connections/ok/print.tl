// This example tests RESTResolver

service PrintService {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

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

service FastPrintService extends PrintService {

    communication_style=rpc

    api {

       @rest(method=POST)
       void fastPrint(int id)
    }
}

service OfficeService {

     deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef Worker [
            str first_name
            str last_name
        ]

        @rest(method=POST)
        void addWorker(str first_name, str last_name)
    }
}

service NewOfficeService extends OfficeService {

    communication_style=rpc

    api {

        @rest(method=POST)
        void removeWorker(str first_name, str last_name)
    }
}

connection OfficeService -> PrintService {
    print[fail_fast]
}

connection NewOfficeService -> FastPrintService {
    print[fail_fast]
    fastPrint[fail_fast]
}
