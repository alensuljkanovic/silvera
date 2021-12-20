import pkg_resources

evaluators = None
built_in_evaluators = {}
FORMAT_STR = "str"
FORMAT_MD = "md"


class EvaluationDesc:

    def __init__(self, name, description, eval_func):
        self.name = name
        self.description = description
        self.eval_func = eval_func
        self.project_name = None

    def __call__(self, model, output_dir, output_format=None):
        self.eval_func(model, output_dir, output_format)


def clean_evaluator_registrations():
    """Clean all evaluator registrations()"""
    global evaluators
    evaluators = {}


def collect_evaluators():
    """Returns a dict of `EvaluatorDesc` objects for each registered evaluator

    Args:
        None

    Returns:
        dict
    """
    global evaluators

    if evaluators is None:
        evaluators = {}
        group = "silvera_evaluators"
        for entry_point in pkg_resources.WorkingSet().iter_entry_points(group):
            ev_desc = entry_point.load()
            ev_desc.project_name = entry_point.dist.project_name
            evaluators[ev_desc.name] = ev_desc

    global built_in_evaluators
    from .builtin import default_evaluator
    built_in_evaluators[default_evaluator.name] = default_evaluator

    return evaluators


def get_evaluator(name):

    all_evaluators = collect_evaluators()

    try:
        return all_evaluators[name]
    except KeyError:

        global built_in_evaluators
        try:
            return built_in_evaluators[name]
        except KeyError:
            raise ValueError("Could not find evaluator with name: '%s'" % name)
