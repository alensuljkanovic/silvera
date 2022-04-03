# From model to runnable

!!! note
    
    Java 17 is needed to run generated code!

## Compile and run the project

First, you need to compile the model. For compilation, use the following command:

```sh
$ silvera compile <project_dir> -o <output_dir>
```

If model is compiled successfully, before you run the applications, first you need to run MongoDB instance:

```sh
$ sudo systemctl start mongo.service
```

If your application is using `messaging` communication style, you need to run `Zookeper` and `Kafka` before starting an applications. To run `Zookeper` run the following command:

```sh
$ cd <kafka_project>
$ bin/zookeeper-server-start.sh config/zookeeper.properties
```

To run `Kafka` run following command:

```sh
$ cd <kafka_project>
$ bin/kafka-server-start.sh config/server.properties
```

After that, go to the output directory and run `run.sh` script:

```sh
$ cd <output_dir>
$ sh run.sh
```

## Introduce manual changes to the generated code

The functionality of custom functions needs to be added manually.

During the compilation, Silvera produces a Java project with the following
structure:

```
<MicroserviceName>
| src
| main
└───java
    └─── com.silvera.<MicroserviceName>
             └───controller
             └─── domain.model
             └─── service
                 └─── base
                 └─── impl
             └───App.java
    └─── resources
    |test
| pom.xml
| run.cmd
| run.sh
```

Package `service.impl` contains the implementation of service functions. Here,
you can provide the custom functions the necessary functionality. For example,
for the `User` microservice (check section [Service declaration](service.md)), the
generated `UserService.java` looks like this:

```java
// UserService.java

...

@Service
public class UserService implements IUserService {


    @Autowired
    UserRepository userRepository;


    public UserService(){
        super();
    }

    // Auto-generated CRUD methods
    @Override
    public User createUser(User user){
        userRepository.save(user);
        Optional<User> opt = userRepository.findById(user.getId());
        return opt.orElse(null);
    }

    @Override
    public User updateUser(java.lang.String id, User userUpdate){
        User entity = this.readUser(id);
        userRepository.save(userUpdate);
        return userUpdate;
    }

    @Override
    public User readUser(java.lang.String id){
        Optional<User> opt = userRepository.findById(id);
        return opt.orElseThrow(IllegalArgumentException::new);
    }

    @Override
    public void deleteUser(java.lang.String id){
        User entity = readUser(id);
        userRepository.delete(entity);
    }



    @Override
    public java.util.List<User> listUsers() {
        /*
            TODO: Implement this function!!!
        */
        throw new java.lang.UnsupportedOperationException("Not implemented yet.");
    }



    @Override
    public java.lang.Boolean userExist(java.lang.String username) {
        /*
            TODO: Implement this function!!!
        */
        throw new java.lang.UnsupportedOperationException("Not implemented yet.");
    }



    @Override
    public java.lang.String userEmail(java.lang.String username) {
        /*
            TODO: Implement this function!!!
        */
        throw new java.lang.UnsupportedOperationException("Not implemented yet.");
    }


}
```

As seen above, the CRUD methods are provided with the default functionality,
but custom functions `listUsers`, `userExists`, and`userEmail` must be implemented
manualy. The functionality is added by simply changing the implementation of these
functions.

!!! note 

    This file will preserve its changes between successive compilations. Meaning, if the base service is changed in the meantime, this file needs to be updated
    manually.

