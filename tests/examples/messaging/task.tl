import "setup.tl"
import "messaging.tl"


service Task {

    service_registry=ServiceRegistry
    communication_style=messaging

    api {

        typedef Task [
            i32 id
            i32 ownerId
            str title
            str description
            str status // OPENED, ASSIGNED, CLOSED
            i32 priority
        ]

        @rest(method=POST)
        @producer(TASK_CREATED -> Broker.EV_TASK_CREATED_CHANNEL)
        Task createTask(str title, str description, i32 priority)

        @rest(method=GET)
        Task getTask(i32 id)

        @rest(method=GET)
        list<Task> listTasks()

        @rest(method=PUT)
        @consumer(AssignTask <- Broker.CMD_ASSING_TASK_CHANNEL)
        @producer(TASK_ASSIGNED -> Broker.EV_TASK_ASSIGNED_CHANNEL)
        void assignTask(i32 taskId, i32 ownerId)

        @rest(method=PUT)
        @consumer(CloseTask <- Broker.CMD_CLOSE_TASK_CHANNEL)
        @producer(TASK_CLOSED -> Broker.EV_TASK_CLOSED_CHANNEL)
        void closeTask(i32 taskId)
    }
}