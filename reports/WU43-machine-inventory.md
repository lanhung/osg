# WU43 control/compute machine inventory

Status: Vultr inspected; AutoDL inspection and cross-machine regression pending

## Vultr control plane

- 1 logical Skylake-class x86_64 CPU under a Microsoft hypervisor
- 1,716,604,928 bytes RAM and 5,662,306,304 bytes swap
- Python 3.14.4
- no visible NVIDIA GPU
- neither `uv` nor Docker installed
- DNS unavailable for tested GitHub and EarthScope hosts

This explains why the current dependency-free reference suite is appropriate,
but production ocean-grid or ML workloads are not.

## AutoDL compute plane

Only the user-supplied description “multi-card NVIDIA A5000” is recorded. GPU
count, CPU, RAM, disk, driver, CUDA, Python and framework versions remain null
until the machine is inspected. The repository does not claim compatibility or
equivalent results yet.

## Cross-machine gate

All four registered experiments must be run on AutoDL. Exact SHA identity is the
default target. If platform floating behavior prevents byte identity, tolerances
must be declared before comparison and a discrepancy report must replace a
silent checksum change.
