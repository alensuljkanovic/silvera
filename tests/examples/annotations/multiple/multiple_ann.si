service TestService {

    communication_style=rpc

    api {
        typedef TestObj [
            i32 id
            str desc
        ]

        @rest(method=POST)
        @async
        @thrift
        void add(TestObj t)

        @async
        @rest(method=GET)
        @thrift
        void get(i32 id)
    }
}