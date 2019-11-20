
service UserService {

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

    communication_style=rpc

    api {

        @rest(method=POST)
        bool logout(User user)
    }
}