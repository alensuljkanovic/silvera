service-registry ServiceRegistry{
    tool=eureka
    client_mode=False
    deployment {
        version="0.0.1"
        port=9091
        url="http://localhost"
    }
}

service Library {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8080
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {
        typedef Registry [
            list<Component> components
        ]

        typedef Component [
            str name
            list<Terminal> terminals
            list<Property> properties
        ]

        typedef Terminal [
            str name
            str direction
        ]

        typedef Property [
            str name
            str label
            bool editable
            bool visible
            i32 default_value
        ]


        @rest(method=POST)
        void add(Component component)

        @rest(method=DELETE)
        void remove(str componentName)

        @rest(method=GET)
        Component get(str componentName)

        @rest(method=GET)
        list<Component> listLibrary()

    }
}


service Schematic {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8081
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {
        typedef Shematic [
            list<ComponentInstance> components
            list<Connection> connections
        ]

        typedef ComponentInstance[
            str libraryName
            str name
            list<TerminalInstance> terminals
            list<PropertyInstance> properties
        ]

        typedef TerminalInstance [
            ComponentInstance parent
            str name
            str direction
        ]

        typedef PropertyInstance [
            ComponentInstance parent
            str name
            i32 value
        ]

        typedef Connection [
            str name
            TerminalInstance start
            TerminalInstance end
        ]

        @rest(method=POST)
        void addComponent(ComponentInstance component)

        @rest(method=DELETE)
        void removeComponent(str componentName)

        @rest(method=POST)
        void addConnection(Connection connection)

        @rest(method=DELETE)
        void removeConnection(str connectionName)

        @rest(method=GET)
        void setPropertyValue(str componentName, str propertyName, i32 value)

        @rest(method=GET)
        Shematic getSchematic()

    }
}


service ConnectionsValidator {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8082
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {
        typedef Status[
            i32 code
            str message
        ]

        typedef Connection [
            str start_name
            str start_direction
            str end_direction
            str end_name
        ]

        @rest(method=GET)
        bool validate(list<Connection> connections)
    }
}



service AnsiCCompiler {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8083
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {

        typedef ComponentData [
            str id
            str name
            list<ComponentData> parents
            list<ComponentData> children

        ]

        @rest(method=GET)
        str compileToAnsiC(list<ComponentData> input)
    }
}

service ARMCCompiler {

    service_registry=ServiceRegistry

    deployment {
        version="0.0.1"
        port=8084
        lang="java"
        packaging="jar"
        host=PC
        replicas=1
    }

    communication_style=rpc

    api {
        typedef ComponentData [
            str id
            str name
            list<ComponentData> parents
            list<ComponentData> children

        ]

        str compileToArmC(list<ComponentData> input)
    }
}

dependency Schematic -> Library {
    get[fail_fast]
}

dependency ConnectionsValidator -> Schematic {
    getSchematic[fail_fast]
}

dependency AnsiCCompiler -> ConnectionsValidator {
    validate[fail_fast]
}

dependency AnsiCCompiler -> Schematic {
    getSchematic[fail_fast]
}

dependency ARMCCompiler -> ConnectionsValidator {
    validate[fail_fast]
}

dependency ARMCCompiler -> Schematic {
    getSchematic[fail_fast]
}