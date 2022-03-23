# Silvera CLI commands

Silvera has several CLI commands:

- `check` - used to check models for syntax and semantic validity,
- `compile` - used to compile model into to executable output,
- `evaluate`- used to evaluate the architecture for given project,
- `init` - used to create initial Silvera project,
- `list-generators` - used to lists all currently available code generators,
- `list-evaluators` - used to lists all currently available architecture evaluators,
- `visualize` - used to visualize the architecture for given project.

To list all available commands just call the `silvera`:

```sh
$ silvera
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