import streamlit as st
import pandas as pd
import json
from engine import Inputs, compute

st.set_page_config(page_title="DC Concept Sizer", layout="wide")

st.title("Data Center Concept Sizer")

with st.sidebar:
    st.header("Inputs")

    it_mw = st.number_input("IT load (MW)", min_value=0.1, value=5.0, step=0.1)
    avg_kw_per_rack = st.number_input("Average rack density (kW/rack)", min_value=1.0, value=30.0, step=1.0)
    pue_target = st.number_input("PUE target", min_value=1.05, value=1.30, step=0.01)

    redundancy = st.selectbox("Redundancy", ["N", "N+1", "2N"], index=1)
    ups_runtime_min = st.number_input("UPS runtime (minutes)", min_value=1.0, value=5.0, step=1.0)

    cooling_margin = st.slider("Cooling margin", 0.0, 0.5, 0.10, 0.01)

    st.subheader("Space assumptions")
    white_space_ft2_per_rack = st.number_input("White space per rack (ft²/rack)", min_value=10.0, value=30.0, step=1.0)
    building_multiplier = st.number_input("Building multiplier (total/white space)", min_value=1.0, value=2.5, step=0.1)

    st.subheader("Cost assumptions")
    cost_per_mw_baseline_usd = st.number_input("Baseline cost ($/MW of IT)", min_value=1_000_000.0, value=11_300_000.0, step=100_000.0)
    tier_uplift = st.slider("Tier/redundancy uplift", 0.0, 0.6, 0.15, 0.01)
    density_uplift = st.slider("High density uplift", 0.0, 0.6, 0.10, 0.01)
    market_uplift = st.slider("Market uplift", 0.0, 0.6, 0.00, 0.01)
    contingency = st.slider("Contingency", 0.0, 0.5, 0.10, 0.01)

inputs = Inputs(
    it_mw=it_mw,
    avg_kw_per_rack=avg_kw_per_rack,
    pue_target=pue_target,
    redundancy=redundancy,
    ups_runtime_min=ups_runtime_min,
    cooling_margin=cooling_margin,
    white_space_ft2_per_rack=white_space_ft2_per_rack,
    building_multiplier=building_multiplier,
    cost_per_mw_baseline_usd=cost_per_mw_baseline_usd,
    tier_uplift=tier_uplift,
    density_uplift=density_uplift,
    market_uplift=market_uplift,
    contingency=contingency,
)

result = compute(inputs)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Racks", f"{result['racks']:,}")
c2.metric("Facility Power", f"{result['facility_kw']/1000:.2f} MW")
c3.metric("Cooling", f"{result['cooling_tons']:.0f} tons")
c4.metric("CAPEX (rough)", f"${result['cost_usd']/1e6:.1f}M")

st.divider()

left, right = st.columns([1.2, 1.0])

with left:
    st.subheader("Key outputs")
    st.write({
        "IT load (kW)": round(result["it_kw"], 1),
        "Non-IT power (kW)": round(result["non_it_kw"], 1),
        "Redundancy factor": round(result["redundancy_factor"], 3),
        "UPS (MW)": round(result["ups_mw"], 2),
        "Battery (MWh)": round(result["battery_mwh"], 2),
        "White space (ft²)": round(result["white_space_ft2"], 0),
        "Building (ft²)": round(result["building_ft2"], 0),
    })

with right:
    st.subheader("Export")
    flat = {
        **{f"input_{k}": v for k, v in result["inputs"].items()},
        "it_kw": result["it_kw"],
        "racks": result["racks"],
        "facility_kw": result["facility_kw"],
        "non_it_kw": result["non_it_kw"],
        "cooling_tons": result["cooling_tons"],
        "ups_mw": result["ups_mw"],
        "battery_mwh": result["battery_mwh"],
        "white_space_ft2": result["white_space_ft2"],
        "building_ft2": result["building_ft2"],
        "cost_usd": result["cost_usd"],
    }
    df = pd.DataFrame([flat])
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="dc_concept_snapshot.csv", mime="text/csv")
    st.download_button("Download JSON", data=json.dumps(result, indent=2), file_name="dc_concept_snapshot.json", mime="application/json")

st.caption("Next upgrades: ASHRAE inlet compliance panel, HVAC plant selection, and Tier III/IV topology outputs.")