# Service

Service is a mechanism to enable access to one or more capabilities, where the access is provided using a prescribed interface and is exercised consistent with constraints and policies as specified by the service description [^1].

## How to define a service

In the following example, we will define a service named `User`, which will register itself
within a service registry called `ServiceRegistry`.


```
service User {

    service_registry=ServiceRegistry
    communication_style=rpc

    api{
        @crud
        typedef User [
            @id str username
            @required str password
            @required str email
        ]

        @rest(method=GET)
        list<User> listUsers()

        @rest(method=GET)
        bool userExists(str username)

        @rest(method=GET)
        str userEmail(str username)
    }
}
```

Attributes:

  * **name** (mandatory) - name of the service.
  * **service_registry** (optional) - reference to a [service registry](service_registry.md) where the service will be registered,
  * **communication_style** - tells which communication style will service use. This attribute can have either `rpc` or `messaging` as a value,
  * **deployment** (optional) - tells how service will be deployed (more info can be found [here](deployment.md)),
  * **api** (mandatory) - API of the service. Here you define all domain objects (via `typedef`) and functions accessible from the outside.

### Communication style

Communication style of a service is defined by  `communication_style` attribute. Service can use RPC (Remote procedure call) or Messaging communication style.

To see how services can communicate, click [here](communication.md).

Attribute communication style is set like this:

```
service User {
    ...
    communication_style=rpc
    ...
}

or

service User {
    ...
    communication_style=messaging
    ...
}
```

### API definition

#### Defining domain-objects

To define a domain object, use `typedef` construct. For example:

```
typedef Point [
    int x
    int y
]
```

Each `typedef` has a `name` and one-or-more `fields`. Field has following attributes:

* **data type** (mandatory) - field's data type (list of available data types is [here](types.md)),
* **name** (mandatory) - field's name,
* **classifiers** (optional):
  * *id* - marks field as `typedef`s ID. Use `@id` annotation to set field as ID.
  * *required* - marks field as required. Use `@required` annotation to set field as required.
  * *unique* - value of the field must be unique in the database. Use `@unique` annotation to set field as unique.
  * *ordered* - typedef will be sorted by this field when retrieving from the database. Use `@ordered` annotation to set field as ordered.


!!! note

    Classifiers unique and ordered are only partially supported for now!

Following example demonstrates how to define fields with aforementioned attributes:

```
    typedef User [
        @id str username
        @required str password
        @required @unique str email
    ]

    or in different formatting:

    typedef User [
        @id
        str username

        @required
        str password

        @required
        @unique
        str email
    ]
```

Domain objects are accessible only within the service itself. To manipulate with domain objects
you need methods. CRUD methods for a domain object can be generated automatically by applying
CRUD annotations:

* `@crud` - generates ALL CRUD methods for a typedef,
* `@create` - generates only CREATE method,
* `@read` - generates only READ method for a typedef,
* `@update` - generates only UPDATE method for a typedef, and
* `@delete` - generates only DELETE method for a typedef.

Here's how CRUD annotations can be used:

```
// generate all CRUD methods
@crud
typedef Point [
    int x
    int y
]

// or

// generate only create method
@create
typedef Point [
    int x
    int y
]

// or

// generate only read method
@read
typedef Point [
    int x
    int y
]

// combining multiple annotations is also possible...
// like this:
// generate create and read methods
@create
@read
typedef Point [
    int x
    int y
]
```

#### Defining API methods

Methods are defined similarly to Java or C#:

```python
bool userExists(str username)
```

Each method has:

* **return type** (mandatory),
* **name** (mandatory),
* **parameters** (optional)

Each method can be annotated with `@rest` annotation. For example

```python
// generates following REST mapping: "/userexists/{username}"
@rest(method=GET)
bool userExists(str username)

// you can also provide a custom mapping
@rest(method=GET, mapping="/exists/{username}")
bool userExists(str username)
```

All HTTP methods are supported by `@rest` annotation. If `@rest` annotation is omitted,
Silvera will try to figure out the which HTTP method to use, or it will throw exception.


!!! note
    In the current version of Silvera, calculating proper `@rest` annotation is little buggy, 
    so please set annotations manually.

Besides `@rest`, method can also be annotated with messaging annotations:

* `@producer` - annotates method as a message producer, or
* `@consumer` - annotates methods as a message consumer.

Methods can be either **public** or **internal**. Consumer methods are usually only used as internal. Following example shows how to define both set of methods:

```
service EmailNotifier {

    ...

    api{

       ...

        //
        // this will be public method:
        //
        @rest(method=GET)
        list<Notification> listNotifications()

        // Internal methods are defined in within `internal` scope:
        internal {
            // Consumes 'OrderMsgGroup.OrderCreated' message from
            // 'EV_ORDER_CREATED_CHANNEL' channel defined in 'Broker'
            @consumer(OrderMsgGroup.OrderCreated <- Broker.EV_ORDER_CREATED_CHANNEL)
            void orderCreated()
        }
    }
}
```

Consumer methods will be generated with corresponding message object as a parameter. For example,
in Java, method `orderCreated` will look like this:

```java
private orderCreated(com.silvera.EmailNotifier.messages.ordermsggroup.OrderCreated message){
    ...
}
```


[^1]:  [OASIS Reference Model for Service Oriented Architecture 1.0](http://www.oasis-open.org/committees/tc_home.php?wg_abbrev=soa-rm)