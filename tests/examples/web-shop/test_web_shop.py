import os
from silvera.generator.generator import SilveraGenerator
from silvera.resolvers import RESTResolver
from silvera.run import load
from silvera.utils import get_root_path


def test_web_shop():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "web-shop")

    model = load(example_path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    output_dir = os.path.join(get_root_path(), "silvera", "generator",
                              "src-gen")

    generator = SilveraGenerator(model)
    generator.generate(output_dir)

