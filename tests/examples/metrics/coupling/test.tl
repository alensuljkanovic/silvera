
service A {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef ObjA [
            int id
            str content
        ]

        @rest(method=GET)
        ObjA get(int id)
    }
}

service DepA1 {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef ObjDep1 [
            int id
            str content
        ]

        @rest(method=GET)
        ObjDep1 add(int id, ObjDep1 content)
    }
}

service DepA2 {

    deployment {
        version="1.0.0"
    }

    communication_style=rpc

    api {
        typedef ObjDep2 [
            int id
            str content
        ]

        @rest(method=GET)
        ObjDep2 add(int id, str content)
    }
}

dependency A -> DepA1 {
    get[fail_fast]
}


dependency DepA1 -> DepA2 {
    add[fail_fast]
}

dependency DepA2 -> DepA1 {
    add[fail_fast]
}