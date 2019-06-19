import os
from talkie.generator.generator import TalkieGenerator
from talkie.resolvers import RESTResolver
from talkie.run import load
from talkie.utils import get_root_path


def test_web_shop():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "web-shop")

    model = load(example_path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    output_dir = os.path.join(get_root_path(), "talkie", "generator",
                              "src-gen")

    generator = TalkieGenerator(model)
    generator.generate(output_dir)

