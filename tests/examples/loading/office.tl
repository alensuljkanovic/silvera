import "print.tl"

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

        @rest(method=POST)
        Worker removeWorker(Worker w)
    }
}

service NewOfficeService extends OfficeService{

     deployment {
        version="2.0.0"
    }

    communication_style=thrift

    api {
        void updateWorker(Worker w)
    }
}

connection OfficeService -> PrintService {
    print[fail_fast]
}
