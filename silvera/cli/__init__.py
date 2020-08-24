import click
import os
import silvera.run as runners
import silvera.generator.generator as gn
from silvera.generator.gen_reg import collect_generators
from silvera import quickstart
from silvera.evaluation import Evaluator


@click.group()
@click.option('--debug', default=False, is_flag=True,
              help="Debug/trace output.")
@click.pass_context
def silvera(ctx, debug):
    ctx.obj = {'debug': debug}


@silvera.command()
@click.argument('project_dir', type=click.Path(), required=True)
@click.pass_context
def check(ctx, project_dir):
    """Checks if created model is valid."""
    try:
        runners.load(project_dir)
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Everything is OK!")


@silvera.command()
@click.argument('project_name')
@click.option('--registry', '-r',
              help="Service registry name")
@click.option('--registry-port', '-rp', type=int,
              help="Service registry port")
@click.option('--cfg', '-c',
              help="Config  server name")
@click.option('--cfg-path', '-cpath',
              help="Config  properties path")
@click.option('--cfg-port', '-cp', type=int,
              help="Config server port")
@click.option('--messaging', default=False, is_flag=True,
              help="Create message broker and message pool.")
@click.pass_context
def init(ctx, project_name, registry, registry_port, cfg, cfg_path, cfg_port,
         messaging):
    """Creates initial Silvera project"""
    cwd = os.getcwd()

    click.echo("Creating project '%s' in '%s'" % (project_name,
                                                  cwd))
    project_path = os.path.join(cwd, project_name)
    if os.path.exists(project_path):
        raise click.ClickException("Project with given name already exists!")

    os.mkdir(project_path)
    open(os.path.join(project_path, ".silvera-project"), "a").close()

    # registry_name, registry_port = registry
    click.echo("Generating setup.tl")
    quickstart.create_setup(project_path, registry, registry_port, cfg,
                            cfg_path, cfg_port)

    if messaging:
        click.echo("Generating messaging.tl")
        quickstart.create_messaging(project_path)


@silvera.command()
@click.argument('project_dir', type=click.Path(), required=True)
@click.option('--output-dir', '-o', type=click.Path(), default=None,
              help='The output dir to generate to. Default = same as input.')
@click.option('--rest-strategy', '-r', default=0,
              help='Strategy to be applied during REST resolving. \
              Default = no strategy')
@click.pass_context
def compile(ctx, project_dir, output_dir, rest_strategy):
    """Compiles application code into to provided output directory."""
    project_dir = os.path.abspath(project_dir)

    click.echo("Compiling...")
    try:
        click.echo("Loading model...")
        model = runners.load(project_dir, rest_strategy)
    except Exception as ex:
        raise click.ClickException(str(ex))

    if not output_dir:
        output_dir = os.path.join(project_dir, "output")
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    else:
        output_dir = os.path.abspath(output_dir)

    try:
        click.echo("Generating code...")
        gn.generate(model, output_dir)
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise click.ClickException(str(ex))

    click.echo("Compilation finished successfully!")
    click.echo("Project generated in: %s" % output_dir)


@silvera.command()
@click.argument('project_dir', type=click.Path(), required=True)
@click.pass_context
def evaluate(ctx, project_dir):
    """Evaluates the architecture for given project."""
    project_dir = os.path.abspath(project_dir)

    try:
        click.echo("Loading model...")
        model = runners.load(project_dir)
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Evaluating...")
    evaluator = Evaluator()
    result = evaluator.evaluate(model)
    result.to_report()


@silvera.command()
@click.pass_context
def list_generators(ctx):
    """Lists all currently available code generators"""
    for gen_desc in collect_generators().values():
        click.echo("{}-{} -> {}".format(gen_desc.lang_name,
                                        gen_desc.lang_ver,
                                        gen_desc.description))


@silvera.command()
@click.argument('project_dir', type=click.Path(), required=True)
@click.option('--output-dir', '-o', type=click.Path(), default=None,
              help='The output dir to generate to. Default = same as input.')
@click.pass_context
def visualize(ctx, project_dir, output_dir):
    """Visualize the architecture for given project."""
    project_dir = os.path.abspath(project_dir)

    try:
        click.echo("Loading model...")
        model = runners.load(project_dir)
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Creating dot file...")
    from silvera.export import export_to_dot

    if output_dir is None:
        output_dir = project_dir

    export_to_dot(model, output_dir)