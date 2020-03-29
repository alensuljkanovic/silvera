import "messaging.tl"


service Task {

    //service_registry=ServiceRegistry
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
        // method createTask publishes TASK_CREATED event to Broker's EV_TASK_CREATED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_CREATED -> Broker.EV_TASK_CREATED_CHANNEL)
        Task createTask(str title, str description, i32 priority)

        @rest(method=GET)
        Task getTask(i32 id)

        @rest(method=GET)
        list<Task> listTasks()

        @rest(method=PUT)
        // method assignTask publishes to TASK_ASSIGNED event to Broker's EV_TASK_ASSIGNED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_ASSIGNED -> Broker.EV_TASK_ASSIGNED_CHANNEL)
        void assignTask(i32 taskId, i32 ownerId)

        @rest(method=PUT)
        // method closeTask publishes TASK_CLOSED event to Broker's EV_TASK_CLOSED_CHANNEL channel
        @producer(TaskMsgGroup.TASK_CLOSED -> Broker.EV_TASK_CLOSED_CHANNEL)
        void closeTask(i32 taskId)

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