"""
This module contains implementation of evaluation of Silvera models.
"""
import os
import warnings
from collections import defaultdict
from .registration import EvaluationDesc, FORMAT_STR, FORMAT_MD


class Evaluator:
    """Performs evaluation of model based on following metrics:

    Weighted Service Interface Count (WSIC)
    ---------------------------------------
    This metric counts the number of exposed interface operations of a service.
    Lower values for WSIC are more favorable for the maintainability of a
    service.

    Number of Versions per Service (NVS):
    -------------------------------------
    The number of versions that are used concurrently in system Y for service
    S.

    Services Interdependence in the System (SIY)
    --------------------------------------------
    Pairs ⟨S 1 , S 2 ⟩ where service S1 calls S2 while service S2 also calls
    S1 at some point.

    Absolute Importance of the Service (AIS)
    ----------------------------------------
    AIS(S) for a service S is the number of consumers that depend on S, i.e.
    the number of clients that invoke at least one operation of S

    Absolute Dependence of the Service (ADS)
    ----------------------------------------
    ADS(S) is the number of other services that S depends on, i.e. the
    number of services from which S invokes at least one operation.

    Absolute Criticality of the Service (ACS):
    ------------------------------------------
    ACS(S) = AIS(S) × ADS(S)
    """
    def _cals_wsic(self, service):
        """Calc WSIC(S) for given service

        Each function increases weight by 1, each param of simple type
        increases weight by 0.5, while param of complex type increases
        weight by 0.7.
        """
        from silvera.core import TypeDef
        wsic = 0
        for function in service.api.functions:
            wsic += 1
            for param in function.params:
                wsic += 0.5
                if isinstance(param.type, TypeDef):
                    wsic += 0.2

        return wsic

    def _calc_nvs(self, service):
        """Calc NVS for given service"""
        replicas = service.deployment.replicas
        return replicas

    def evaluate(self, model):
        """Evaluate model

        Args:
            model (Model): Model object

        Returns:
            EvaluationResult
        """
        result = EvaluationResult()

        for s in [s for m in model.modules for s in m.service_decls]:
            result.ads[s.name] = 0
            result.ais[s.name] = 0
            result.wsic[s.name] = self._cals_wsic(s)
            result.nvs[s.name] = self._calc_nvs(s)

        interdep = defaultdict(set)
        for c in [c for m in model.modules for c in m.dependencies]:
            start = c.start
            result.ads[start.name] += 1

            end = c.end
            result.ais[end.name] += 1

            # `start` service depends upon `end`
            interdep[start.name].add(end.name)

        siy = set()
        for s, deps in interdep.items():
            for s1, deps1 in interdep.items():
                if s in deps1 and s1 in deps:
                    siy.add((s, s1))

        result.siy = siy

        # result.to_report()

        return result


class EvaluationResult:
    """Result of evaluation"""

    def __init__(self):
        self.ais = defaultdict(int)
        self.ads = defaultdict(int)
        self.wsic = defaultdict(int)
        self.nvs = defaultdict(int)
        self.siy = []

    @property
    def ais_avg(self):
        return sum(self.ais.values())/len(self.ais)

    @property
    def ads_avg(self):
        return sum(self.ads.values())/len(self.ads)

    @property
    def wsic_avg(self):
        return sum(self.wsic.values())/len(self.wsic)

    @property
    def nvs_avg(self):
        return sum(self.nvs.values())/len(self.nvs)

    @property
    def acs(self):
        return {s: self.ais[s] * self.ads[s] for s in self.ads}

    @property
    def acs_avg(self):
        return sum(self.acs.values())/len(self.acs)

    def _to_markdown(self):
        """Creates evaluation report as a string with Markdown syntax.

        Returns:
            str, list
        """
        def title(s):
            return "# %s\n\n" % s

        def section(s):
            return "## %s\n\n" % s

        def descr(s):
            return "*%s*\n\n" % s

        def sys_avg(s):
            return "**System average: %.2f**\n\n" % s

        def service(s):
            return "Service *%s*:\n\n" % s

        wsic_avg = self.wsic_avg

        report = title("Evaluation report")
        warn_lst = []

        # WSIC
        report += section("Weighted Service Interface Count (WSIC)")
        report += descr("This metric counts the number of exposed interface "
                        "operations of a service. Lower values for WSIC are "
                        "more favorable for the maintainability of a service.")
        report += sys_avg(wsic_avg)

        for s in sorted(self.wsic, key=lambda x: self.wsic[x] - wsic_avg):
            diff = self.wsic[s] - wsic_avg
            report += service(s)
            report += "*  Wsic[s]: %.2f\n" % self.wsic[s]
            report += "*  Diff from avg: %.2f\n\n" % diff
            if diff > 0:
                warn_lst.append("WSIC for '%s' service (%s) is larger than the "
                                "systems average (%s). Lower values for WSIC "
                                "are more favorable for the maintainability "
                                "of a service." % (s, self.wsic[s], wsic_avg))

        # NVS
        report += section("Number of Versions per Service (NVS)")
        report += descr("The number of versions that are used concurrently "
                        "in system Y for service S.")
        report += sys_avg(self.nvs_avg)

        for s in sorted(self.nvs, key=lambda x: self.nvs[x] - self.nvs_avg):
            diff = self.nvs[s] - self.nvs_avg
            report += service(s)
            report += "*  NVS[s]: %.2f\n" % self.nvs[s]
            report += "*  Diff from avg: %.2f\n\n" % diff
            if diff > 0:
                warn_lst.append("NVS for '%s' service (%s) is larger than the "
                                "systems average (%s). Large NVS impacts "
                                "maintainability of the services." %
                                (s, self.wsic[s], wsic_avg))

        # AIS
        report += section("Absolute Importance of the Service (AIS)")
        report += descr("AIS(S) for a service S is the number of consumers "
                        "that depend on S, i.e. the number of clients that "
                        "invoke at least one operation of S.")
        report += sys_avg(self.ais_avg)

        for s, total_calls in self.ais.items():
            diff = self.ais[s] - self.ais_avg
            report += service(s)
            report += "*  AIS[s]: %s\n" % total_calls
            report += "*  AIS[s] - AIS_avg: %.2f\n\n" % diff
            if diff > 0:
                warn_lst.append("AIS for '%s' service (%s) is larger than the "
                                "systems average (%s). This service may be a "
                                "potential bottleneck." % (s, self.ais[s],
                                                           self.ais_avg))

        # ADS
        report += section("Absolute Dependence of the Service (ADS)")
        report += descr("ADS(S) is the number of other services that S "
                        "depends on, i.e. the number of services from which "
                        "S invokes at least one operation.")
        report += sys_avg(self.ads_avg)
        for s, total_calls in self.ads.items():
            diff = self.ads[s] - self.ads_avg
            report += service(s)
            report += "*  ADS[s]: %s\n" % total_calls
            report += "*  ADS[s] - ADS_avg: %.2f\n\n" % diff
            if diff > 0:
                warn_lst.append("ADS for '%s' service (%s) is larger than the "
                                "systems average (%s). This service may be a "
                                "potential bottleneck." % (s, self.ads[s],
                                                           self.ads_avg))

        # ACS
        report += section("Absolute Criticality of the Service (ACS)")
        report += descr("ACS(S) = AIS(S) × ADS(S)")
        report += sys_avg(self.acs_avg)
        for s, value in self.acs.items():
            diff = self.acs[s] - self.acs_avg
            report += service(s)
            report += "*  ACS[s]: %s\n" % value
            report += "*  ACS[s] - ACS_avg: %.2f\n\n" % diff
            if diff > 0:
                warn_lst.append("ACS for '%s' service (%s) is larger than the "
                                "systems average (%s)." % (s, self.acs[s],
                                                           self.acs_avg))

        # SIY
        report += section("Services Interdependence in the System (SIY)")
        report += descr("Pairs ⟨S 1 , S 2 ⟩ where service S1 calls S2 while "
                        "service S2 also calls S1 at some point.")
        if not self.siy:
            report += "*  No interdependent pairs found!\n\n"

        for s in self.siy:
            report += "{}\n".format(s)
            warn_lst.append("Interdependent services: %s. Could these services"
                            "be merged?\n" %s)

        # Add warnings to the report
        if warn_lst:
            report += section("Warnings")
            for w in warn_lst:
                report += "* %s\n" % w

        return report, warn_lst

    def to_report(self, output_dir=None, f=FORMAT_STR):
        """Prints report"""
        report, warn_lst = self._to_markdown()

        if f == FORMAT_MD:
            with open(os.path.join(output_dir, "evaluation_report.md"), "w") as f:
                f.write(report)

            # Print warnings at the end of function so they do not mix with
            # report
            for w in warn_lst:
                warnings.warn(w)
        else:
            print(report)


def evaluate(model, output_dir, output_format=FORMAT_STR):
    ev = Evaluator()
    result = ev.evaluate(model)
    result.to_report(output_dir, output_format)


# built-in architecture evaluator
default_evaluator = EvaluationDesc(
    name="default",
    description="Silvera's default architecture evaluator.",
    eval_func=evaluate
)
