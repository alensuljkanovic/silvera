service SchemeService {

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=REST

    api {
        typedef Scheme [
            list<ComponentLink> connections
            list<Connection> connections
        ]

        typedef TerminalLink [
            str name
            str direction
        ]

        typedef PropertyLink [
            str property_name
            i32 value
        ]

        typedef ComponentLink [
            str component_name
            str name
            list<PropertyLink> properties
            list<TerminalLink> terminals
        ]

        typedef Connection [
            str start_component
            str start_terminal
            str end_component
            str end_terminal
        ]

        @rest(method=GET)
        void add(str component_name)

        @rest(method=GET)
        Connection connect(str start_component, str start_terminal,  str end_component, str end_terminal)

        @rest(method=GET)
        void set_property_value(str component_name, str property_name, i32 value)

        @rest(method=GET)
        list<ComponentLink> list_components()
    }
}

service LibraryService {

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=REST

    api {
        typedef Component [
            str name
            str icon
            list<Terminal> terminals
            list<Property> properties
        ]

        typedef Terminal [
            Component parent
            str name
            str direction
        ]

        typedef Property [
            Component parent
            str name
            str label
            i32 default_value
        ]

        typedef TerminalLink [
            str name
            str direction
        ]

        typedef PropertyLink [
            str property_name
            i32 value
        ]

        typedef ComponentLink [
            str component_name
            str name
            list<PropertyLink> properties
            list<TerminalLink> terminals
        ]

        @rest(method=GET)
        void add_to_lib(Component component)

        @rest(method=GET)
        ComponentLink get_component(str component_name)

    }
}


service CompileService {

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=REST

    api {
        typedef Netlist [
            list<Node> nodes
        ]

        typedef Node [
            str component_type
            str component_name
        ]

        void compile(Netlist netlist)

    }
}

connection SchemeService -> LibraryService {
    get_component[fail_fast]
}

connection SchemeService -> CompileService {
    compile[fail_fast]
}