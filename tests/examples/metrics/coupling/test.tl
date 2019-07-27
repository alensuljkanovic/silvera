
service A {

    deployment {
        version="1.0.0"
    }

    communication_style=REST

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

    communication_style=REST

    api {
        typedef ObjDep1 [
            int id
            str content
        ]

        @rest(method=GET)
        ObjDep1 add(int id, str content)
    }
}

service DepA2 {

    deployment {
        version="1.0.0"
    }

    communication_style=REST

    api {
        typedef ObjDep2 [
            int id
            str content
        ]

        @rest(method=GET)
        ObjDep2 add(int id, str content)
    }
}

connection A -> DepA1 {
    get[fail_fast]
}


connection DepA1 -> DepA2 {
    get[fail_fast]
}