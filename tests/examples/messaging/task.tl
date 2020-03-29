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

        @rest(method=POST, mapping="/task")
        // method addTask publishes TASK_CREATED event to Broker's EV_TASK_CREATED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_CREATED -> Broker.EV_TASK_CREATED_CHANNEL)
        Task addTask(Task task)

        @rest(method=GET, mapping="/task/{id}")
        Task getTask(i32 id)

        @rest(method=GET, mapping="/task")
        list<Task> getTasks()

        @rest(method=PUT, mapping="/task/assign/{taskId}/{ownerId}")
        // method assignTask publishes to TASK_ASSIGNED event to Broker's EV_TASK_ASSIGNED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_ASSIGNED -> Broker.EV_TASK_ASSIGNED_CHANNEL)
        void assignTask(i32 taskId, i32 ownerId)

        @rest(method=PUT, mapping="/task/close/{id}")
        // method closeTask publishes TASK_CLOSED event to Broker's EV_TASK_CLOSED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_CLOSED -> Broker.EV_TASK_CLOSED_CHANNEL)
        void closeTask(i32 id)

        internal {

            // method assignTask consumes AssignTask command from Broker's CMD_ASSIGN_TASK_CHANNEL channel
            @consumer(TaskMsgGroup.AssignTask <- Broker.CMD_ASSIGN_TASK_CHANNEL)
            void assignTask()

            @consumer(TaskMsgGroup.CloseTask <- Broker.CMD_CLOSE_TASK_CHANNEL)
            // method closeTask publishes TASK_CLOSED event to Broker's EV_TASK_CLOSED_CHANNEL channel
            @producer(TaskMsgGroup.TASK_CLOSED -> Broker.EV_TASK_CLOSED_CHANNEL)
            void closeTask()
        }
    }
}