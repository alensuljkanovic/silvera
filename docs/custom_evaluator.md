# Custom evaluator

Silvera allows users to register new evaluators as plugins.

Silvera uses the `pkg_resources` module from [setuptools](https://setuptools.readthedocs.io/en/latest/)
and its concept of extension point to declaratively specify the registration of the new evaluator.
Extensions are defined within the project's `setup.py` module. All Python projects installed in
the environment that declare the extension point will be discoverable dynamically.

Registration of new evaluator is performed in the same way as registration of new code generator,
which is described [here](custom_generator.md).

There is also a demo application where this functionality is demonstrated: 
[PyGen](https://github.com/alensuljkanovic/silvera-demo/tree/master/pygen)

