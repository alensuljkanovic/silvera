# Evaluation metrics

Silvera uses predefined metrics to evaluate the modeled application:

* *Weighted Service Interface Count (WSIC)* - This metric counts the number of exposed interface operations of a service. Lower values for WSIC are more favorable for the maintainability of a service.

* *Number of Versions per Service (NVS)* - The number of versions that are used concurrently in system Y for service S.

* *Services Interdependence in the System (SIY)* - Pairs ⟨S 1 , S 2 ⟩ where service S1 calls S2 while service S2 also calls S1 at some point.

* *Absolute Importance of the Service (AIS)* - AIS(S) for a service S is the number of consumers that depend on S, i.e. the number of clients that invoke at least one operation of S

* *Absolute Dependence of the Service (ADS)* - ADS(S) is the number of other services that S depends on, i.e. the number of services from which S invokes at least one operation.

* *Absolute Criticality of the Service (ACS)* - ACS(S) = AIS(S) × ADS(S)

To perform evaluation, run following command

```
$ silvera evaluate <project_dir>
```

For more info about these evaluation metrics, check these papers:
* Bogner, J.; Wagner, S.; Zimmermann, A. Automatically measuring the maintainability of service-and microservice-based systems:
  a literature review. Proceedings of the 27th International Workshop on Software Measurement and 12th International Conference
  on Software Process and Product Measurement, 2017, pp. 107–115.
* Hirzalla, M.; Cleland-Huang, J.; Arsanjani, A. A metrics suite for evaluating flexibility and complexity in service oriented
architectures. International Conference on Service-Oriented Computing. Springer, 2008, pp. 41–52.
* Rud, D.; Schmietendorf, A.; Dumke, R. Product metrics for service-oriented infrastructures.