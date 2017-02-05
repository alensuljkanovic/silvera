interface SimpleInterface {

    endpoint Server {
        ip: "192.168.0.14",
        port: 5559,
        lang: java,
        role: server
    }

    bool login(string username, string password)
    bool register(string username, string password)
}