# Pre-registered evaluation criteria

The three papers now have machine-readable success, negative-result, and failure
rules under `configs/paper*/evaluation_criteria.json`. These files were written
before production data analysis or PEGS simulator selection.

Key consequences:

- Paper 1 cannot call a curve intersection a detection result; duration,
  bandwidth, uncertainty, analytic validation, and published-case validation are
  required.
- Paper 2 cannot claim event attribution from a visually correlated case. It
  requires raw-enough gravimeter data, independent controls, component closure,
  an event holdout, and improvement under the frozen analysis.
- Paper 3 cannot claim warning value from PEGS arriving early. Continuous-stream
  false alarms, detection probability, reliable magnitude, conventional
  comparators, domain holdouts, realistic noise, and station outages are gates.

Numerical criteria that are scientific conventions rather than instrument facts
are explicit here so they can be revised only by a documented, pre-analysis
amendment—not after inspecting final results.
