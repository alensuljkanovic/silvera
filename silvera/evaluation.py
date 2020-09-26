"""
This module contains implementation of evaluation of Silvera models.
"""
from collections import defaultdict


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

    def to_report(self):
        """Prints report"""

        wsic_avg = self.wsic_avg
        print("Weighted Service Interface Count (WSIC):")
        print("\tSystem average: %.2f" % wsic_avg)

        for s in sorted(self.wsic, key=lambda x: self.wsic[x] - wsic_avg):
            diff = self.wsic[s] - wsic_avg
            print("\tService:'%s':" % s)
            print("\t\tWsic[s]: %.2f" % self.wsic[s])
            print("\t\tDiff from avg: %.2f" % diff)

        print("\n\nAbsolute Importance of the Service (AIS):")
        print("System average[AIS_avg]:  %.2f" % self.ais_avg)
        for s, total_calls in self.ais.items():
            diff = self.ais[s] - self.ais_avg
            print("\tService '%s':" % s)
            print("\t\tAIS[s]: %s" % total_calls)
            print("\t\tAIS[s] - AIS_avg: %.2f" % diff)

        print("\n\nAbsolute Dependence of the Service (ADS)")
        print("System average: %.2f" % self.ads_avg)
        for s, total_calls in self.ads.items():
            diff = self.ads[s] - self.ads_avg
            print("\tService '%s':" % s)
            print("\tADS[s]: %s" % total_calls)
            print("\tADS[s] - ADS_avg: %.2f" % diff)

        print("\n\nAbsolute Criticality of the Service (ACS)")
        print("System average: %.2f" % self.ads_avg)
        for s, value in self.acs.items():
            diff = self.acs[s] - self.acs_avg
            print("\tService '%s':" % s)
            print("\t\tACS[s]: %s" % value)
            print("\t\tACS[s] - ACS_avg: %.2f" % diff)

        print("\n\nServices Interdependence in the System (SIY)")
        if not self.siy:
            print("\tNo interdependent pairs found!")

        for s in self.siy:
            print("\t{}".format(s))
