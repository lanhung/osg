# WU44 CI experiment-registry validation

Status: workflow updated; remote GitHub Actions run pending successful push

The Python 3.11 and 3.13 CI matrix now performs three independent checks:

1. the full dependency-free unit/physics/regression suite;
2. source/test/script bytecode compilation;
3. experiment metadata, path, config SHA and output SHA validation.

The CI step validates frozen artifacts but does not regenerate them on both
Python versions. Cross-version byte identity for transcendental-heavy outputs is
not assumed without evidence; `make reproduce-all` remains the explicit local or
machine qualification command.

No remote run exists yet because the current control plane cannot resolve
GitHub. The workflow result must not be marked passing until a network-capable
push triggers GitHub Actions.
