import "setup.tl"
import "messaging.tl"


service Employee {

    service_registry=ServiceRegistry
    communication_style=messaging

    api {

        typedef Employee [
            i32 id
            str firstName
            str lastName
            str address
        ]

        @rest(method=POST)
        @producer(EmployeeMsgGroup.EMPLOYEE_CREATED -> Broker.EV_EMPLOYEE_CREATED_CHANNEL)
        void create(str fistName, str lastName, str address)

        @rest(method=GET)
        Employee getEmployee(i32 id)

        @rest(method=GET)
        list<Employee> listEmployees()
    }

}