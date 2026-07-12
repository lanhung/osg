# WU33 experiment registry validation and dispatcher

Status: implemented and tested against all current registered experiments

## Contract

Every metadata document is checked for required fields, directory identity,
paper identity, full code commit, repository-contained paths, existing runner
and config, config checksum, optional data manifest, unique outputs, and output
checksums. Validation fails closed before batch reproduction begins.

`make reproduce-all` validates the registry, invokes the existing isolated
experiment reproducer for every registered experiment, verifies each frozen
output SHA, and validates the registry again after execution.

## Current result

Three Paper 1 experiments are registered and valid. The registry test is part
of the default dependency-free suite, preventing unnoticed config/output drift.

## Commands

```bash
make validate-experiments
make reproduce-all
```
