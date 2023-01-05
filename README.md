# Silvera

Silvera is a declarative language for modeling microservice
architectures based on [textX](https://github.com/textX/textX), and it is designed
in a way that directly implements domain-related design patterns.

Silvera is:

* lightweight and editor-agnostic language - you can use text editor of your choice to write Silvera programs.
* built with heterogeneity in mind - Silvera's compiler can produce code for any programming language or framework since
  [code generators are registered as plugins](https://alensuljkanovic.github.io/silvera/custom_generator/).

In addition, Silvera uses microservice-tailored metrics to evaluate the architecture
of the designed system and automatically generates the documentation. 
Architecture Evaluation Processor comes with a set of 
[predefined metrics](https://alensuljkanovic.github.io/silvera/evaluation-metrics/), 
but you can also [add your own!](https://alensuljkanovic.github.io/silvera/custom_evaluator/).

Silvera is fully implemented in Python.

# Quick intro

Here is a small example where we define a service registry and one microservice.

```
# setup.si

service-registry ServiceRegistry {
	client_mode=False
	deployment {
		version="0.0.1"
		port=9091
		url="http://localhost"
	}
}
```

```
import "setup.si"

service Bookstore {

    service_registry=ServiceRegistry

    api {

        @crud
        typedef Book [
            @id str isbn
            @required str title
            @required str author
            str category
            @required double price
        ]

        @rest(method=GET)
        list<Book> listBooks()

        @rest(method=GET)
        bool bookExists(str isbn)

        @rest(method=GET)
        double bookPrice(str isbn)
    }

}
```


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

For documentation and tutorials, visit docs: https://alensuljkanovic.github.io/silvera/

## Additional code generators

Additional code generators that you can use are:

* [pyvera](https://github.com/dovvla/pyvera) - Python code generator for Silvera
* [silvera-csharp-gen](https://github.com/albertmakan/silvera-csharp-gen) - C# code generator for Silvera
* [gogen](https://github.com/stasadj/gogen) - Go code generator for Silvera

## Citing Silvera

If you are using textX in your research project we would be very grateful if you cite our paper:

Suljkanović, A.; Milosavljević, B.; Inđić, V.; Dejanović, I. Developing Microservice-Based Applications Using the Silvera Domain-Specific Language. Appl. Sci. 2022, 12, 6679. https://doi.org/10.3390/app12136679 
## Python versions

Tested with Python 3.7.4+
