
service UserService {

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1

        restart-policy {
            delay=3
            max_attempts=5
            condition=any
        }
    }

    communication_style=rpc

    api {
        typedef User [
            str id
            str password
            bool active
            str createdBy
            str deletedBy
        ]


        User login(str userId, str password)

        @rest(method=POST)
        bool register(User user)
    }
}

service ProxyService extends UserService {
    communication_style=messaging
}

service ChangedUserService extends UserService {

    deployment {
        version="0.2.1"
        port=8081
        lang="python"
        packaging="wheel"
        restart-policy {
            condition=on-failure
            max_attempts=3
        }
    }

    communication_style=rpc
}