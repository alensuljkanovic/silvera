import "print.tl"

service OfficeService {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef Worker [
            i32 id
            str first_name
            str last_name
            list<Task> tasks
        ]

        typedef Task [
            i32 id
            str description
        ]

        @rest(method=POST)
        void addWorker(str first_name, str last_name, list<Task> tasks)

        @rest(method=POST)
        Worker removeWorker(Worker w)

        @rest(method=POST)
        list<Worker> listWorkers()
    }
}

service NewOfficeService extends OfficeService{

    deployment {
        version="2.0.0"
    }

    communication_style=messaging

    api {
        void updateWorker(Worker w)
    }
}

dependency OfficeService -> PrintService {
    print[fail_fast]
}
