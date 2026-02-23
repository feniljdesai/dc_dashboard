from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal, Dict, Any
import math

Redundancy = Literal["N", "N+1", "2N"]

@dataclass(frozen=True)
class Inputs:
    it_mw: float
    avg_kw_per_rack: float
    pue_target: float
    redundancy: Redundancy
    ups_runtime_min: float
    cooling_margin: float
    white_space_ft2_per_rack: float
    building_multiplier: float
    cost_per_mw_baseline_usd: float
    tier_uplift: float
    density_uplift: float
    market_uplift: float
    contingency: float

def redundancy_factor(redundancy: Redundancy, n_modules: int = 6) -> float:
    if redundancy == "N":
        return 1.0
    if redundancy == "2N":
        return 2.0
    n = max(2, n_modules)
    return (n + 1) / n

def kw_to_tons(it_kw: float) -> float:
    return it_kw * 0.2843

def compute(inputs: Inputs) -> Dict[str, Any]:
    it_kw = inputs.it_mw * 1000.0
    racks = math.ceil(it_kw / inputs.avg_kw_per_rack)

    facility_kw = it_kw * inputs.pue_target
    non_it_kw = facility_kw - it_kw

    cooling_tons = kw_to_tons(it_kw) * (1.0 + inputs.cooling_margin)

    red = redundancy_factor(inputs.redundancy, n_modules=max(2, min(12, math.ceil(racks / 100))))

    ups_kw = it_kw * red
    ups_mw = ups_kw / 1000.0
    runtime_hr = inputs.ups_runtime_min / 60.0
    battery_mwh = (ups_kw * runtime_hr) / 1000.0

    white_space_ft2 = racks * inputs.white_space_ft2_per_rack
    building_ft2 = white_space_ft2 * inputs.building_multiplier

    base_cost = inputs.cost_per_mw_baseline_usd * inputs.it_mw
    uplifted = base_cost * (1.0 + inputs.tier_uplift + inputs.density_uplift + inputs.market_uplift)
    cost_usd = uplifted * (1.0 + inputs.contingency)

    return {
        "inputs": asdict(inputs),
        "it_kw": it_kw,
        "racks": racks,
        "facility_kw": facility_kw,
        "non_it_kw": non_it_kw,
        "cooling_tons": cooling_tons,
        "redundancy_factor": red,
        "ups_mw": ups_mw,
        "battery_mwh": battery_mwh,
        "white_space_ft2": white_space_ft2,
        "building_ft2": building_ft2,
        "cost_usd": cost_usd,
    }