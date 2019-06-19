
service UserService {

    communication_style=REST

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
    communication_style=thrift
}

service ChangedUserService extends UserService {

    communication_style=REST

    api {

        @rest(method=POST)
        bool logout(User user)
    }
}