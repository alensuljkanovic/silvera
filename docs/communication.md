# Inter-service communication

Service can use RPC (Remote procedure call) or Messaging communication style.

RPC communication style is based on request-reply protocol. It is simple to use, but it creates
coupling between client service and provider service.

Messaging provides loose runtime coupling, but adds additional complexity to the system because
you need to define [message broker](./communication#message-broker) and [message pool](./communication#message-pool).

## Remote procedure call (RPC)

!!! note

    Silvera's RPC communication is generalization of Remote Method Invocation described here:
    [https://microservices.io/patterns/communication-style/rpi.html](https://microservices.io/patterns/communication-style/rpi.html)

When using RPC, in order for two services to be able  to communicate, you must define
a dependency between them.

In the example that follows, we will define two dependencies for `Order` service.
These are `User` service and `Storage` service. More precisely, `Order` service
depends on `User` service methods `userExist` and `userEmail`, and `Storage`
service method `takeIngredient`.


```
dependency Order -> User {
    userExists[fail_fast]
    userEmail[fail_fast]
}

dependency Order -> Storage {
    takeIngredient[fail_fast]
}
```

Based on the dependency declaration, Silvera will generate a code that can be used
to interact with the target service.

What happens if `User` service or `Storage` service is unavailable when request takes
place? Luckily, Silvera implements Circuit Breaker pattern, and how the situation is
handled is defined by one of the following options:

* **fail_fast** - exception will be raised in the client if API call fails (default behavior),
* **fail_silent** - returns an empty response,
* **fallback_method** - defines a method that will be called in case the original method fails,
* **fallback_static** - returns default values, and
* **fallback_cache** - returns a cached version of response if present, otherwise returns empty response like fail_silent.

!!! note

    More information about the Circuit Breaker design pattern can be found here:
    [https://microservices.io/patterns/reliability/circuit-breaker.html](https://microservices.io/patterns/reliability/circuit-breaker.html)

## Messaging

Messaging communication style depends on two things: message broker, and message
pool.

!!! note

    In the current version, Silvera supports only Kafka as a message broker.

!!! note

    More information about the Messaging design pattern can be found here:
    [https://microservices.io/patterns/communication-style/messaging.html](https://microservices.io/patterns/communication-style/messaging.html)

### Message pool

Message pool is globally available object that contains all messages that are used
withing the system. Message can contain parameters (command message) or not (event).

Here's how to define a message pool with two messages:

```
msg-pool {

    // define message group Commands
    group Commands [

        msg CreateCommand[
           str param1
           str param2
           ...
        ]
    ]

    // define message group Events
    group Events [
        msg StorageItemTaken[]
    ]
}

```

### Message broker

Message broker is an entity whose responsibility is to deliver messages to a destination.

Message broker contains `channels` where messages are stored. Services that add messages
to channels are called `publishers`, while services that read messages from channels
are called `consumers`. A service can be both publisher and consumer at the same time.

Here's how to define a message broker:

```
// message broker is named Broker
msg-broker Broker {

    channel CMD_CREATE_COMMAND_CHANNEL(Commands.CreateCommand)
    channel EV_STORAE_ITEM_TAKEN_CHANNEL(Events.StorageItemTaken)
```

As shown in the example above, **channels in Silvera are typed**. Which means, only
messages of certain type can be added to the channel.

### How do I send messages?

In order to send a message, you need to annotate an API method with `@producer` annotation.

In following example, method `takeFromStorage` will send `Events.StorageItemTaken` message to the `EV_STORAGE_ITEM_TAKEN_CHANNEL` channel defined in broker named `Broker`.

```
service Order [

    ...

    api {
        ...
        @producer(Events.StorageItemTaken -> Broker.EV_STORAGE_ITEM_TAKEN_CHANNEL)
        bool takeFromStorage(i32 itemId)
    }
]

```

!!! note

    Silvera will generate code that will publish the command to 
    the messaging broker, but setting values to command's attributes need to be 
    handled manually, otherwise empty message will be sent!

### How do I receive messages?

In order to consume a message, you need to annotate an API method with `@consumer` annotation.

In following example, internal method `itemTakenListener` will receive `Events.StorageItemTaken` message from the `EV_STORAGE_ITEM_TAKEN_CHANNEL` channel defined in broker named `Broker`.

```
service StorageListener [

    ...

    api {
        ...

        internal {
            @consumer(Events.StorageItemTaken <- Broker.EV_STORAGE_ITEM_TAKEN_CHANNEL)
            void itemTakenListener()
        }

    }
]

```

In the generated code, `itemTakenListener` will have `Events.StorageItemTaken` object
as a parameter.