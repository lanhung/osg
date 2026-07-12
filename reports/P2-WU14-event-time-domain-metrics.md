# P2-WU14 event time-domain attribution metrics

Status: implementation and unit validation complete; real event results pending
the Paper 2 data gate.

One mask-aware function now reports bias, RMSE, Pearson correlation, explained
variance, signed peak amplitudes and peak-time error. The peak convention is the
earliest sample with maximum absolute magnitude, preserving its sign. Amplitude
error is model minus observation; time error is modeled peak time minus observed
peak time.

Correlation and explained variance are `None` when their variance denominator is
zero. Explained variance may be negative and is not clipped. At least two included
samples are required. The function does not mutate observations, modeled values
or the quality mask.

Frequency-domain coherence and event SNR remain separate metrics because their
windowing, detrending, gap and noise conventions require independent explicit
configuration.
