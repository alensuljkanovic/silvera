interface SimpleInterface {

    endpoint Server2 {
        ip: "192.168.0.14",
        port: 5559,
        lang: java,
        role: server
    }

    endpoint Client2 {
        ip: "192.168.0.17",
        port: 5559,
        lang: python,
        role: client
    }

    bool login(string username, string password)
    bool register(string username, string password)
}