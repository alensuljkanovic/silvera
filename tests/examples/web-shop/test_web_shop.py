import os
from talkie.generator.generator import TalkieGenerator
from talkie.lang.meta import get_metamodel
from talkie.resolvers import RESTResolver
from talkie.utils import get_root_path


def test_web_shop():
    examples_path = os.path.join(get_root_path(), "tests", "examples",
                                 "web-shop")

    metamodel = get_metamodel()
    path = os.path.join(examples_path, "web-shop.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    output_dir = os.path.join(get_root_path(), "talkie", "generator",
                              "src-gen")

    generator = TalkieGenerator(model)
    generator.generate(output_dir)

