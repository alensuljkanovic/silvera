# Silvera changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Evaluation called during compilation process. Evaluation report generated as Markdown file in the output folder.
* OpenAPI specification (openapi.json) generated for each service with REST API during compilation.

### Removed

* Attribute `tool` from service registry declaration is removed. Which service registry will actually be used is determined by code generators.
* Attribute `communication_style` is removed. Communication style is now determined based on used annotations.

## [0.2.3] - 2020-11-07

* Fix textx compatibility

## [0.2.2] - 2020-10-19

* Generate code for publishing messages in methods that are annotated as producers
* Report an error if module not properly loaded

## [0.2.1] - 2020-10-18

* Fixed bug regarding CRUD annotations in service and controller templates

## [0.2.0] - 2020-10-17

* File extension changed from .tl to .si
* Fixed bug in generation of dependency calls where return value is list
* Support for @required in built-in Java generator
* Exact line in file is shown for undefined types
* Added initial support for Circuit Breaker pattern in built-in Java generator

## [0.1.0] - 2020-10-04

* First release. 
* Generates Java 1.8 code
* Support for RPC and messaging
* Supports services, registry, API gateway, circuit breaker,...
* Evaluation based on metrics