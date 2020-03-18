
import "setup.tl"
import "messaging.tl"


service Dashboard {

    service_registry=ServiceRegistry
    communication_style=messaging

    api {
        typedef Status [
            i32 boardsNum
            i32 employeesNum
            i32 openedTasksNum
            i32 assignedTasksNum
            i32 closedTasksNum
        ]

        @rest(method=GET)
        Status status()

        @consumer(
            BoardMsgGroup.BOARD_CREATED <- Broker.EV_BOARD_CREATED_CHANNEL,
            EmployeeMsgGroup.EMPLOYEE_CREATED <- Broker.EV_EMPLOYEE_CREATED_CHANNEL,
            TaskMsgGroup.TASK_CREATED <- Broker.EV_TASK_CREATED_CHANNEL,
            TaskMsgGroup.TASK_ASSIGNED <- Broker.EV_TASK_ASSIGNED_CHANNEL,
            TaskMsgGroup.TASK_CLOSED <- Broker.EV_TASK_CLOSED_CHANNEL
        )
        void refresh()
    }

}