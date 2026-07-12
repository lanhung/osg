# WU43 control/compute machine inventory

Status: Vultr and AutoDL inspected; AutoDL registered suite passed; revised
canonical outputs still require a Vultr rerun for the cross-machine gate

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

The inspected host is `autodl-container-7fb444a9ae-9b4ed319`, with 64 logical
Intel Xeon Silver 4314 CPUs, 134,787,624,960 bytes RAM, and four NVIDIA RTX 5000
Ada Generation GPUs. Each GPU reports 32,760 MiB, compute capability 8.9, driver
570.124.06, and driver-advertised CUDA 12.8. The locked project environment uses
Python 3.12.12 and uv 0.8.24. PyTorch is deliberately absent because the current
registered physics baselines do not require GPU execution.

The canonical local source is synchronized to
`/root/autodl-tmp/ocean-gravity-run/repo`; bulk data and execution outputs use
sibling `data/` and `outputs/` directories on the AutoDL data volume. Local tool
caches, `.git`, virtual environments, and raw/derived data are excluded.

## Cross-machine gate

All five registered experiments now reproduce their registered SHA on AutoDL,
and the complete suite passes 430 tests plus 12 subtests. The first run exposed
platform-dependent final bits in the dependency-free DFT reports for P1-E002 and
P1-E003. A predeclared `1e-24` signal-energy coverage floor removes numerical
leakage, and report values are canonicalized to 10 significant digits without
changing scientific classifications. The revised canonical outputs still need
to be rerun on Vultr before the cross-machine gate is marked complete.
