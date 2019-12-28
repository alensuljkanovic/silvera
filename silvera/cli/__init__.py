import click
import os
import silvera.run as runners
import silvera.generator.generator as gn
from silvera.generator.gen_reg import collect_generators


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
        click.echo(str(ex))
        return

    click.echo("Everything is OK!")


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
    click.echo(project_dir)
    try:
        click.echo("Loading model...")
        model = runners.load(project_dir, rest_strategy)
    except Exception as ex:
        click.echo(str(ex))
        return

    if not output_dir:
        output_dir = project_dir
    else:
        output_dir = os.path.abspath(output_dir)

    click.echo(output_dir)
    try:
        click.echo("Generating code...")
        gn.generate(model, output_dir)
    except Exception as ex:
        click.echo(str(ex))
        return

    click.echo("Compilation finished successfully!")


@silvera.command()
@click.pass_context
def list_generators(ctx):
    """Lists all currently available code generators"""
    for gen_desc in collect_generators().values():
        click.echo("{}-{} -> {}".format(gen_desc.lang_name,
                                        gen_desc.lang_ver,
                                        gen_desc.description))