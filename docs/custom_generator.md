# Custom generator

Silvera allows users to register new code generators as plugins.

Silvera uses the `pkg_resources` module from [setuptools](https://setuptools.readthedocs.io/en/latest/)
and its concept of extension point to declaratively specify the registration of the new code generator.
Extensions are defined within the project's `setup.py` module. All Python projects installed in
the environment that declare the extension point will be discoverable dynamically.

Registration of a new code generator is performed in two steps (as shown below). You can also follow
the video tutorial:

[![Custom code generator](https://img.youtube.com/vi/p63EnxR40ic/3.jpg)](https://youtu.be/p63EnxR40ic)

There is also a demo application where this functionality is demonstrated: [PyGen](https://github.com/alensuljkanovic/silvera-demo/tree/master/pygen)

## Step 1

Create an instance of `GeneratorDesc` class. An instance of GeneratorDesc class contains
information about the code generator's target language, description, and the reference
towards the function that should be called to perform code generation.
This function has three parameters: `Decl` object, a path to the directory where code will be generated,
and a flag that shows whether the code generator is run in debug mode.

```python
from silvera.generator.gen_reg import GeneratorDesc

def generate(decl, output_dir, debug):
    """Entry point function for code generator.

    Args:
        decl(Decl): can be declaration of service registry or config
                    server.
        output_dir(str): output directory.
        debug(bool): True if debug mode activated. False otherwise.
    """
    ...

python = GeneratorDesc(
    language_name="python",
    language_ver="3.7.4",
    description="Python 3.7.4 code generator",
    gen_func=generate
)
```

## Step 2

Now, we need to make the code generator discoverable by Silvera. To do this,
we must register the `GeneratorDesc` object in the `setup.py` entry point named
`silvera_generators`:

```python
# setup.py

from setuptools import setup

setup(
    ...
    entry_points={
        'silvera_generators': [
            'python = pygen.generator:python'
        ]
    }
)
```
