import "setup.tl"

service Employee {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        replicas=1
    }

    communication_style=rpc

    api {

        typedef Employee [
            i32 id
            str firstName
            str lastName
            str address
        ]

        @async
        @rest(method=POST)
        void add(Employee e)

        @async
        @rest(method=GET)
        Employee getEmployee(i32 id)

        @async
        @rest(method=GET)
        list<Employee> listEmployees()
    }

}

service Task {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8081
        lang="java"
        packaging="jar"
        replicas=1
    }

    communication_style=rpc

    api {

        typedef Task [
            i32 id
            str title
            str description
            str status
            i32 priority
        ]

        @async
        @rest(method=POST)
        Task createTask(str title, str description, i32 priority)

        @async
        @rest(method=POST)
        void addTask(Task task)

        @async
        @rest(method=GET)
        Task getTask(i32 id)

        @async
        @rest(method=GET)
        list<Task> listTasks()
    }
}


service TasksBoard {

    service_registry=ServiceRegistry

    deployment {
        port=8082
        lang="java"
        packaging="jar"
        replicas=1
    }

    communication_style=rpc

    api {

        typedef Board [
            i32 id
            str title
            list<TaskView> taskView
        ]

        typedef TaskView [
            i32 employeeId
            i32 taskId
            str employeeName
            str taskTitle
        ]

        @async
        @rest(method=POST)
        Board createBoard(str title)

        @async
        @rest(method=POST)
        TaskView assignTask(i32 boardId, i32 employeeId, i32 taskId)


        @async
        @rest(method=GET)
        Board getBoard(i32 id)
    }
}

connection TasksBoard -> Employee {
    getEmployee[fail_fast]
}

connection TasksBoard -> Task {
    getTask[fail_fast]
}