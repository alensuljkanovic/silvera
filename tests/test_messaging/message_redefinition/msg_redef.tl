// Pool of all messages that are used throught the application.
msg-pool {

    group Group1 [
        msg EVENT1[]
    ]

    group Group2 [
        msg EVENT1[] // OK

        // not OK.
        msg EVENT2[]
        msg EVENT2[]
    ]
}

