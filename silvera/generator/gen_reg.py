import pkg_resources
from silvera.generator.platforms import JAVA


# Registry of all available code generators.
generators = None


class GeneratorDesc:
    """Generator description class, used for generator registration and
    discovery.
    """
    def __init__(self, language_name, language_ver, description, gen_func):
        """Initialize object

        Args:
            language_name (str): language name
            language_ver (str): language version
            description (str): a short description of the generator
            gen_func (callable): A callable that performs the generation

        """
        super().__init__()
        self.lang_name = language_name
        self.lang_ver = language_ver
        self.description = description
        self.gen_func = gen_func
        self.project_name = None

    def __call__(self, decl, output_dir, debug):
        self.gen_func(decl, output_dir, debug)


def generator(lang_name, lang_ver):
    """Decorator used for entry point registration

    Function decorated with this decorator will be registered as Silvera code
    codenerator for given language name and version.

    Args:
        lang_name (str): target language name
        lang_ver (str): target language version

    Returns:
        function
    """
    def wrapper(f):
        # take title line as description
        desc = f.__doc__.splitlines()[0] if f.__doc__ else ""
        return GeneratorDesc(lang_name, lang_ver, desc, f)
    return wrapper


def generator_for_language(language):
    """Returns the `GeneratorDesc` for a given language

    Args:
        language (str): target language name

    Returns:
        GeneratorDesc
    """
    generators = collect_generators()

    try:
       return generators[language]
    except KeyError:
        raise ValueError("Could not find generator for a language \
                         '%s'" % language)


def collect_generators():
    """Returns a dict of `GeneratorDesc` objects for each registered generator

    Args:
        None

    Returns:
        dict
    """
    global generators

    if generators is None:
        generators = {}
        group = "silvera_generators"
        for entry_point in pkg_resources.WorkingSet().iter_entry_points(group):
            gen_desc = entry_point.load()
            gen_desc.project_name = entry_point.dist.project_name
            generators[gen_desc.lang_name] = gen_desc

    return generators