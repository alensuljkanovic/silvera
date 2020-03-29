// Pool of all messages that are used throught the application.
msg-pool {

    // define message group
    group TaskMsgGroup [

        // Defining commands
        @expires_after(2000)  // defines expiration timeout
        msg AssignTask [
            i32 taskId
            i32 employeeId
        ]

        @expires_after(2000)  // defines expiration timeout
        msg CloseTask [
            i32 taskId
        ]

        // Defining events
        msg TASK_CREATED[]
        msg TASK_ASSIGNED[]
        msg TASK_CLOSED[]
    ]

    group BoardMsgGroup [
        msg BOARD_CREATED[]
    ]

    group EmployeeMsgGroup [
        msg EMPLOYEE_CREATED[]
    ]
}

// Defining a message broker. Its sole responsibility is to deliver messages
// to a destination.
// 'Publishers' send messages strictly to the broker, and 'consumers' receive
// messages also strictly from the broker.
msg-broker Broker {

    channel CMD_ASSIGN_TASK_CHANNEL(TaskMsgGroup.AssignTask)
    channel CMD_CLOSE_TASK_CHANNEL(TaskMsgGroup.CloseTask)

    channel EV_BOARD_CREATED_CHANNEL(BoardMsgGroup.BOARD_CREATED)
    channel EV_EMPLOYEE_CREATED_CHANNEL(EmployeeMsgGroup.EMPLOYEE_CREATED)
    channel EV_TASK_CREATED_CHANNEL(TaskMsgGroup.TASK_CREATED)
    channel EV_TASK_ASSIGNED_CHANNEL(TaskMsgGroup.TASK_ASSIGNED)
    channel EV_TASK_CLOSED_CHANNEL(TaskMsgGroup.TASK_CLOSED)
}
