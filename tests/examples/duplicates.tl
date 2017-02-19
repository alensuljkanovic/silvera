interface Duplicates {

    endpoint Client {
        ip: "192.168.0.14",
        port: 5559,
        lang: java,
        role: client
    }

    endpoint Client {
        ip: "192.168.0.17",
        port: 5559,
        lang: python,
        role: server
    }

    bool login(string username, string password)
    bool register(string username, string password)
}