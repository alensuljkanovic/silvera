service Schematic {

    communication_style=REST

    api {
        // Name is not defined, so loading must fail.
        typedef Registry [
            Name name
            i32 id
        ]
    }

}