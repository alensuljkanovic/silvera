import "setup.tl"
import "messaging.tl"


service TasksBoard {

    service_registry=ServiceRegistry
    communication_style=messaging

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
            str taskStatus
        ]

        @rest(method=POST)
        @producer(BoardMsgGroup.BOARD_CREATED -> Broker.EV_BOARD_CREATED_CHANNEL)
        Board createBoard(str title)

        @rest(method=POST)
        @producer(TaskMsgGroup.AssignTask -> Broker.CMD_ASSIGN_TASK_CHANNEL)
        TaskView assignTask(i32 boardId, i32 taskId, i32 employeeId)

        @rest(method=GET)
        Board getBoard(i32 id)
    }
}