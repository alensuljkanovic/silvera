service Schematic {

    communication_style=rpc

    api {
        // Component is not defined, so loading must fail.
        typedef Registry [
            list<Component> components
        ]
    }

}