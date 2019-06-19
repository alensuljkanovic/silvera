service PrintService {

    deployment {
        version="1.0.0"
    }

    communication_style=REST

    api {
        typedef Document [
            int id
            str name
            str content
        ]

        @rest(method=GET)
        void print(int id)

        @rest(method=GET)
        void printDoc(Document d)
    }
}
