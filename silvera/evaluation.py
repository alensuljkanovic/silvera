"""
This module contains implementation of evaluation of Silvera models.
"""
from collections import defaultdict


class Evaluator:
    """Performs evaluation of model based on following metrics:

    Coupling
    --------
    This metric, for each service, counts the number of services it depends
    upon.

    Fan in
    ------
    This metric, for each service, counts the number of functions used by
    other services. Component with high `fan in` can prove to be a possible
    bottleneck.

    Fan out
    -------
    This metric, for each service, counts the number of functions from other
    services that are called. Lower `fan out` means that the service shows
    lower dependency towards other services.


    """
    def __init__(self):
        # self.coupling_results = defaultdict(list)
        self.fan_in_results = defaultdict(lambda: defaultdict(list))
        self.fan_out_results = defaultdict(lambda: defaultdict(list))

    def _add_fan_in(self, connection):
        fan_in = self.fan_in_results
        start = connection.start
        end = connection.end

        for fnc in (cb.method_name for cb in connection.circuit_break_defs):
            per_service = fan_in[end]
            per_service[fnc].append(start)

    def _add_fan_out(self, connection):
        fan_out = self.fan_out_results
        start = connection.start
        end = connection.end

        for fnc in (cb.method_name for cb in connection.circuit_break_defs):
            per_service = fan_out[start]
            per_service[end].append(fnc)

    def evaluate(self, model):
        # coupling = self.coupling_results
        #model_to_graph(model)
        fan_in = self.fan_in_results
        fan_out = self.fan_out_results

        for module in model.modules:
            for connection in module.connections:
                self._add_fan_in(connection)
                self._add_fan_out(connection)

        print("\n\n`FAN IN` results:")
        for serv, results in fan_in.items():
            print("Service '%s':" % serv.name)
            total_calls = 0
            for method, callers in results.items():
                print("\tFunction: `%s`" % method)

                print("\t\tNumber of functions calls: %s" % len(callers))
                print("\t\tCallers: {}".format([s.name for s in callers]))

                total_calls += len(callers)

            print("\t**Total calls**: %s" % total_calls)

        print("\n\n`FAN OUT` results:")
        for serv, results in fan_out.items():
            print("Service '%s':" % serv.name)
            total_calls = 0
            for dep_serv, methods in results.items():
                print("\tService: `%s`" % dep_serv.name)

                print("\t\tNumber of functions called: %s" % len(methods))
                print("\t\tFunctions called: {}".format(methods))

                total_calls += len(methods)

                print("\t**Total calls**: %s" % total_calls)

            print("\n")

    # def coupling_for(self, serv):
    #     """Returns coupling metric for a given service"""
    #     if not self.coupling_results:
    #         raise ValueError("Evaluation must be performed before calling"
    #                          "this method.")
    #
    #     return self.coupling_results[serv]

#
# def model_to_graph(model):
#     from networkx import DiGraph
#
#     graph = DiGraph()
#
#     for module in model.modules:
#         for serv in module.service_decls:
#             graph.add_node(serv)
#     # for module in model.modules:
#     #     graph.add_nodes_from(list(module.service_decls))
#
#     for module in model.modules:
#         for connection in module.connections:
#             start = connection.start
#             end = connection.end
#
#             for fnc in (cb.method_name for cb in
#                         connection.circuit_break_defs):
#                 graph.add_edge(start, end, method=fnc)
#             # graph.add_edge(connection.start, connection.end)
#
#     print("Nodes:")
#     print(graph.nodes)
#     print("Edges:")
#     print(graph.edges)
#
#     print("Succ")
#     for n in graph.predecessors(model.find_by_fqn("test.DepA2")):
#         print(n, )
