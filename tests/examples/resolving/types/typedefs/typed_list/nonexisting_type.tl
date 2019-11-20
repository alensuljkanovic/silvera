service Schematic {

    communication_style=REST

    api {
        // Component is not defined, so loading must fail.
        typedef Registry [
            list<Component> components
        ]
    }

}