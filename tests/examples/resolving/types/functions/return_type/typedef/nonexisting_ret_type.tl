service Schematic {

    communication_style=REST

    api {

        // Registry is not defined, so loading must fail.
        Registry getRegistry()
    }

}