"""Fetch and summarize StationXML responses for frozen station pairs."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def summarize_stationxml(payload: bytes, network: str, station: str) -> dict:
    root = ET.fromstring(payload)
    channels = []
    for network_element in root.iter():
        if _local_name(network_element.tag) != "Network":
            continue
        if network_element.attrib.get("code") != network:
            continue
        for station_element in network_element:
            if _local_name(station_element.tag) != "Station":
                continue
            if station_element.attrib.get("code") != station:
                continue
            for channel in station_element:
                if _local_name(channel.tag) != "Channel":
                    continue
                code = channel.attrib.get("code", "")
                if len(code) != 3 or code[:2] not in {"BH", "LH"}:
                    continue
                response = next(
                    (
                        child
                        for child in channel
                        if _local_name(child.tag) == "Response"
                    ),
                    None,
                )
                sensitivity = None
                if response is not None:
                    sensitivity = next(
                        (
                            child
                            for child in response
                            if _local_name(child.tag) == "InstrumentSensitivity"
                        ),
                        None,
                    )
                response_stage_count = 0
                transfer_function_stage_count = 0
                if response is not None:
                    for stage in response:
                        if _local_name(stage.tag) != "Stage":
                            continue
                        response_stage_count += 1
                        if any(
                            _local_name(element.tag)
                            in {"PolesZeros", "Coefficients", "FIR", "Polynomial"}
                            for element in stage.iter()
                        ):
                            transfer_function_stage_count += 1
                channels.append(
                    {
                        "location": channel.attrib.get("locationCode", ""),
                        "channel": code,
                        "start_time": channel.attrib.get("startDate", ""),
                        "end_time": channel.attrib.get("endDate", ""),
                        "response_present": response is not None,
                        "instrument_sensitivity_present": sensitivity is not None,
                        "response_stage_count": response_stage_count,
                        "transfer_function_stage_count": transfer_function_stage_count,
                    }
                )
    groups: dict[tuple[str, str, str, str], set[str]] = {}
    complete_response: dict[tuple[str, str, str, str], bool] = {}
    full_response_structure: dict[tuple[str, str, str, str], bool] = {}
    for channel in channels:
        key = (
            channel["location"],
            channel["channel"][:2],
            channel["start_time"],
            channel["end_time"],
        )
        groups.setdefault(key, set()).add(channel["channel"][2])
        complete_response[key] = complete_response.get(key, True) and (
            channel["response_present"]
            and channel["instrument_sensitivity_present"]
        )
        full_response_structure[key] = full_response_structure.get(key, True) and (
            channel["response_present"]
            and channel["instrument_sensitivity_present"]
            and channel["response_stage_count"] > 0
            and channel["transfer_function_stage_count"] > 0
        )
    triplets = []
    for key, components in sorted(groups.items()):
        has_triplet = "Z" in components and (
            {"N", "E"}.issubset(components) or {"1", "2"}.issubset(components)
        )
        if has_triplet:
            triplets.append(
                {
                    "location": key[0],
                    "band": key[1],
                    "start_time": key[2],
                    "end_time": key[3],
                    "components": sorted(components),
                    "response_and_sensitivity_present_for_group": complete_response[key],
                    "full_response_structure_present_for_group": full_response_structure[key],
                }
            )
    return {
        "network": network,
        "station": station,
        "response_channel_count": len(channels),
        "three_component_response_epoch_count": len(triplets),
        "three_component_response_epochs": triplets,
    }


def build_url(config: dict, network: str, station: str) -> str:
    query = {
        "format": "xml",
        "level": "response",
        "network": network,
        "station": station,
        "channel": config["channel"],
        "starttime": config["starttime"],
        "endtime": config["endtime"],
        "includerestricted": "false",
        "nodata": 404,
    }
    return f"{config['endpoint']}?{urllib.parse.urlencode(query)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported response-audit schema version")
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    results = []
    retrieval_time = datetime.now(UTC).isoformat()
    for row in config["stations"]:
        network = row["network"]
        station = row["station"]
        url = build_url(config, network, station)
        request = urllib.request.Request(url, headers={"User-Agent": "oceangravity/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:  # noqa: S310
                payload = response.read()
                status = response.status
                final_url = response.url
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
            results.append(
                {
                    **row,
                    "status": "no_data_404",
                    "requested_url": url,
                    "http_status": 404,
                }
            )
            continue
        raw_path = args.raw_dir / f"{network}.{station}.xml"
        raw_path.write_bytes(payload)
        summary = summarize_stationxml(payload, network, station)
        results.append(
            {
                **row,
                "status": "retrieved",
                "requested_url": url,
                "final_url": final_url,
                "http_status": status,
                "raw_path": str(raw_path),
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                **summary,
            }
        )
    output = {
        "schema_version": 1,
        "retrieved_at_utc": retrieval_time,
        "selection_status": config["selection_status"],
        "station_pair_count": len(results),
        "retrieved_pair_count": sum(row["status"] == "retrieved" for row in results),
        "pairs_with_response_triplet": sum(
            row.get("three_component_response_epoch_count", 0) > 0 for row in results
        ),
        "pairs_with_full_response_structure_triplet": sum(
            any(
                epoch.get("full_response_structure_present_for_group", False)
                for epoch in row.get("three_component_response_epochs", ())
            )
            for row in results
        ),
        "stations": results,
        "warning": "StationXML response presence does not establish waveform availability, current operation, real-time latency, licence, or usable PEGS noise.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
