config-server ConfigServer {
    version="0.0.1"
    port=9090
    search_path="file://${user.home}/Projects/MicroServiceProps/centralProperties/"
}

service-registry EmployeeEurekaServer{
    version="0.0.1"
    tool=eureka
    port=9091
    uri="http://localhost"
    client_mode=False
}


api-gateway APIGateway {
    version="1.0.0"
    port=8080
    config_server=ConfigServer
    service_registry=EmployeeEurekaServer
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
    }

    communication_style=REST

    gateway-for {
        EmployeeSearch as "emp"
    }
}


service EmployeeSearch {
    version="1.0.0"
    port=8080
    config_server=ConfigServer
    service_registry=EmployeeEurekaServer
    lang="java"

    deployment {
        packaging="jar"
        host=PC
        n=1
    }

    communication_style=REST

    api {
        typedef Employee [
            i32 employeeId
            str name
            str practiceArea
            str designation
            str companyInfo
        ]

        Employee findById(i32 id)
        list<Employee> findAll()
    }

}
