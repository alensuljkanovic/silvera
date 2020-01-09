// Pool of all messages that are used throught the application.
// Types of messages:
// 1. CommandMessage - Use to invoke a procedure in another application
// 2. EventMessage - Use to notify another application of a change in this application

msg-pool {
    // Defining commands
    command AssignTask [
        i32 taskId
        i32 employeeId
    ]

    command CloseTask [
        i32 taskId
    ]

    // Defining events
    events [
        BOARD_CREATED
        EMPLOYEE_CREATED
        TASK_CREATED
        TASK_ASSIGNED
        TASK_CLOSED
    ]

}

// Defining a message broker. Its sole responsibility is to deliver messages
// to a destination.
msg-broker Broker {

    channel CMD_ASSING_TASK_CHANNEL(AssignTask)
    channel CMD_CLOSE_TASK_CHANNEL(CloseTask)

    channel EV_BOARD_CREATED_CHANNEL(BOARD_CREATED)
    channel EV_EMPLOYEE_CREATED_CHANNEL(EMPLOYEE_CREATED)
    channel EV_TASK_CREATED_CHANNEL(TASK_CREATED)
    channel EV_TASK_ASSIGNED_CHANNEL(TASK_ASSIGNED)
    channel EV_TASK_CLOSED_CHANNEL(TASK_CLOSED)
}
