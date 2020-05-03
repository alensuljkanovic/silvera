service Schematic {

    communication_style=rpc

    api {
        // Registry is not defined, so loading must fail.
        void add(list<Registry> r)
    }

}