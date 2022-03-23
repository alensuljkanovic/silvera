# Silvera

Silvera is a tool for acceleration of development of microservice architectures.

Silvera consists of two parts: a domain-specific language - SilveraDSL, and
a Silvera compiler. SilveraDSL is a declarative language for modeling microservice
architectures based on [textX](https://github.com/textX/textX), and it is designed
in a way that directly implements domain-related design patterns. SilveraDSL
specifications are used by the compiler to produce executable program code.

Silvera is fully implemented in Python.

## Feature highlights

* **Designed patterns directly implemented in language**

* **Project modularization - imports**

* **Project evaluation based on metrics**

* **Automatic code generation**

* **Support for custom code generators via plugins**


## Installation

You can use `pip` to install Silvera:

```sh
$ pip install silvera
```

To verify that you have installed Silvera correctly run the following command:

```sh
$ silvera
```

You should get output like this:

```sh
Usage: silvera [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check            Checks if created model is valid.
  compile          Compiles application code into to provided output...
  evaluate         Evaluates the architecture for given project.
  init             Creates initial Silvera project
  list-generators  Lists all currently available code generators
  list-evaluators  Lists all currently available architecture evaluators
  visualize        Visualize the architecture for given project.
```

## Video tutorials


### Basics

[![Silvera Tutorial 1: Basics](https://img.youtube.com/vi/auYNqP4FgW0/0.jpg)](https://youtu.be/auYNqP4FgW0)

### Messaging

[![Silvera Tutorial 2: Messaging](https://img.youtube.com/vi/MQyfZOXX99M/0.jpg)](https://youtu.be/MQyfZOXX99M)

### Microservice deployment options & custom code generator

[![Silvera Tutorial 3: Microservice deployment options & custom code generator](https://img.youtube.com/vi/p63EnxR40ic/0.jpg)](https://youtu.be/p63EnxR40ic)