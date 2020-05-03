import "service_a.tl"

service B {

    deployment {
        version="0.0.1"
    }

    communication_style=rpc

    api {
        bool check_b(str some_param)
    }
}
