import "service_b.tl"

service A {

    deployment {
        version="0.0.1"
    }

    communication_style=rpc

    api {
        bool check_a(str some_param)
    }
}