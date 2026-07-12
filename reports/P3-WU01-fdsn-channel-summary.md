# P3-WU01 FDSN channel-inventory summarizer

Status: offline parser and conservative station gate implemented; live inventory pending DNS

## Contract

The parser groups exact network/station/location/band/start/end channel epochs
and accepts only BH or LH groups containing `Z+N+E` or `Z+1+2`. Incomplete
epochs remain in a separate output rather than disappearing.

It records coordinates, sample-rate set and whether every text row contains a
scalar sensitivity. It always leaves `full_response_verified=false`: channel
text metadata, even with a scalar scale, is not a StationXML response audit.

## Safety boundary

A three-component candidate still does not prove waveform availability,
continuous event/noise coverage, licence, real-time latency, correct response,
timing quality, or acceptable PEGS-band noise. These remain separate gates.

## Commands after network restoration

```bash
python3 scripts/fetch_fdsn_station_inventory.py \
  --output data/raw/paper3/fdsn_station_channels.txt

python3 scripts/summarize_fdsn_inventory.py \
  --input data/raw/paper3/fdsn_station_channels.txt \
  --output data/interim/paper3/fdsn_station_candidates.json
```

The current control plane cannot resolve the EarthScope host, so no station is
yet marked available.
