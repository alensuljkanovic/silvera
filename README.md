# Silvera

Silvera is an tool for acceleration of development of microservice architectures.

Silvera consists of two parts: a domain-specific language - SilveraDSL, and
a Silvera compiler. SilveraDSL is a declarative language for modeling microservice
architectures based on [textX](https://github.com/textX/textX), and it is designed
in a way that directly implements domain-related design patterns. SilveraDSL
specifications are used by the compiler to produce executable program code.

Silvera is fully implemented in Python.

## Installation

You can use `pip` to install Silvera:

```
$ pip install silvera
```

To verify that you have installed Silvera correctly run the following command:

```
$ silvera
```

You should get output like this:

```
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
  visualize        Visualize the architecture for given project.
```


## Feature highlights

* **Designed patterns directly implemented in language**

* **Project modularization - imports**

* **Project evaluation based on metrics**

* **Automatic code generation**

* **Support for custom code generators via plugins**


## User guide

For documentation and tutorials, please check Silvera's wiki page: [here](https://gitlab.com/alensuljkanovic/silvera/-/wikis/home).


## Python versions

Tested with Python 3.7.4