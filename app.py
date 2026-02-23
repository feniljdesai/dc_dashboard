cd "C:\Users\Fenil Desai\dc_dashboard"

$app = @'
import streamlit as st
import pandas as pd
import json
from engine import Inputs, compute

st.set_page_config(page_title="Data Center Concept Sizer", layout="wide")
st.title("Data Center Concept Sizer")

with st.sidebar:
    st.header("Inputs")

    it_mw = st.number_input("IT load (MW)", min_value=0.1, value=5.0, step=0.1)
    avg_kw_per_rack = st.number_input("Average rack density (kW/rack)", min_value=1.0, value=30.0, step=1.0)
    pue_target = st.number_input("PUE target", min_value=1.05, value=1.30, step=0.01)

    st.subheader("Reliability")
    redundancy = st.selectbox("Redundancy", ["N", "N+1", "2N"], index=1)
    ups_runtime_min = st.number_input("UPS runtime (minutes)", min_value=1.0, value=5.0, step=1.0)
    generator_margin = st.slider("Generator margin", 0.0, 0.5, 0.10, 0.01)

    st.subheader("Electrical assumptions")
    lv_voltage = st.selectbox("LV voltage (V)", [480, 415, 400], index=0)
    power_factor = st.number_input("Power factor", min_value=0.80, max_value=1.0, value=0.95, step=0.01)

    ups_module_mw = st.number_input("UPS module size (MW)", min_value=0.25, value=1.0, step=0.25)
    gen_unit_mw = st.number_input("Generator unit size (MW)", min_value=0.5, value=2.5, step=0.5)
    xfmr_mva = st.number_input("Transformer size (MVA)", min_value=1.0, value=5.0, step=1.0)

    pdu_kw = st.number_input("PDU capacity (kW)", min_value=50.0, value=500.0, step=50.0)
    rpp_circuits = st.number_input("RPP circuits per unit", min_value=12, value=84, step=6)
    circuits_per_rack = st.number_input("Branch circuits per rack", min_value=1, value=2, step=1)
    rack_pdu_per_rack = st.number_input("Rack PDUs per rack", min_value=1, value=2, step=1)

    st.subheader("Cooling")
    cooling_plant = st.selectbox(
        "Cooling plant",
        [
            "DX (air-cooled CRAC/RTU)",
            "CHW air-cooled chillers",
            "CHW water-cooled chillers",
            "Liquid cooling ready (D2C + CDU + CHW)",
        ],
        index=1,
    )
    cooling_margin = st.slider("Cooling margin", 0.0, 0.5, 0.10, 0.01)
    chw_deltaT_F = st.number_input("CHW delta-T (°F)", min_value=8.0, value=20.0, step=1.0)
    economizer = st.checkbox("Economizer enabled", value=True)
    chiller_unit_tons = st.number_input("Chiller unit size (tons)", min_value=100.0, value=500.0, step=50.0)
    crah_unit_kw = st.number_input("CRAH/CRAC unit sensible (kW)", min_value=25.0, value=150.0, step=25.0)
    cdu_unit_kw = st.number_input("CDU unit capacity (kW)", min_value=50.0, value=200.0, step=25.0)
    percent_liquid_cooled = st.slider("Liquid-cooled fraction", 0.0, 1.0, 0.0, 0.05)

    st.subheader("Space assumptions")
    white_space_ft2_per_rack = st.number_input("White space per rack (ft²/rack)", min_value=10.0, value=30.0, step=1.0)
    building_multiplier = st.number_input("Building multiplier", min_value=1.0, value=2.5, step=0.1)

    st.subheader("Cost assumptions")
    cost_per_mw_baseline_usd = st.number_input("Baseline cost ($/MW IT)", min_value=1_000_000.0, value=11_300_000.0, step=100_000.0)
    redundancy_uplift = st.slider("Redundancy uplift", 0.0, 0.6, 0.15, 0.01)
    cooling_uplift = st.slider("Cooling uplift", 0.0, 0.6, 0.10, 0.01)
    market_uplift = st.slider("Market uplift", 0.0, 0.6, 0.00, 0.01)
    contingency = st.slider("Contingency", 0.0, 0.5, 0.10, 0.01)

inputs = Inputs(
    it_mw=it_mw,
    avg_kw_per_rack=avg_kw_per_rack,
    pue_target=pue_target,
    redundancy=redundancy,
    ups_runtime_min=ups_runtime_min,
    generator_margin=generator_margin,
    lv_voltage=lv_voltage,
    power_factor=power_factor,
    ups_module_mw=ups_module_mw,
    gen_unit_mw=gen_unit_mw,
    xfmr_mva=xfmr_mva,
    pdu_kw=pdu_kw,
    rpp_circuits=int(rpp_circuits),
    circuits_per_rack=int(circuits_per_rack),
    rack_pdu_per_rack=int(rack_pdu_per_rack),
    cooling_plant=cooling_plant,
    cooling_margin=cooling_margin,
    chw_deltaT_F=chw_deltaT_F,
    economizer=economizer,
    chiller_unit_tons=chiller_unit_tons,
    crah_unit_kw=crah_unit_kw,
    cdu_unit_kw=cdu_unit_kw,
    percent_liquid_cooled=percent_liquid_cooled,
    white_space_ft2_per_rack=white_space_ft2_per_rack,
    building_multiplier=building_multiplier,
    cost_per_mw_baseline_usd=cost_per_mw_baseline_usd,
    redundancy_uplift=redundancy_uplift,
    cooling_uplift=cooling_uplift,
    market_uplift=market_uplift,
    contingency=contingency,
)

res = compute(inputs)

tab1, tab2, tab3 = st.tabs(["Summary", "BOM + Sizing", "Export"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Racks", f"{res['racks']:,}")
    c2.metric("Facility Power", f"{res['facility_kw']/1000:.2f} MW")
    c3.metric("Cooling", f"{res['cooling_tons']:.0f} tons")
    c4.metric("CAPEX (rough)", f"${res['cost_usd']/1e6:.1f}M")

    st.divider()
    df_key = pd.DataFrame([
        ["IT load", res["it_kw"], "kW"],
        ["Facility power", res["facility_kw"], "kW"],
        ["Non-IT power", res["non_it_kw"], "kW"],
        ["Cooling capacity", res["cooling_tons"], "tons"],
        ["UPS installed", res["ups_installed_mw"], "MW"],
        ["Battery energy", res["battery_mwh"], "MWh"],
        ["Generator installed", res["gen_installed_mw"], "MW"],
        ["LV current (facility)", res["facility_amps_lv"], "A (approx)"],
        ["LV current (IT)", res["it_amps_lv"], "A (approx)"],
        ["CHW flow", res["chw_gpm"], "gpm (approx)"],
        ["White space", res["white_space_ft2"], "ft²"],
        ["Building total", res["building_ft2"], "ft²"],
    ], columns=["Metric", "Value", "Unit"])
    st.dataframe(df_key, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Equipment BOM + sizing (concept)")
    equip_df = pd.DataFrame(res["equipment"])

    categories = ["All"] + sorted(equip_df["Category"].unique().tolist())
    colA, colB = st.columns([0.35, 0.65])
    with colA:
        cat = st.selectbox("Category filter", categories, index=0)
    with colB:
        q = st.text_input("Search (name/notes/basis)", value="")

    filtered = equip_df.copy()
    if cat != "All":
        filtered = filtered[filtered["Category"] == cat]
    if q.strip():
        needle = q.strip().lower()
        mask = (
            filtered["Equipment"].str.lower().str.contains(needle, na=False)
            | filtered["Sizing basis"].str.lower().str.contains(needle, na=False)
            | filtered["Notes"].str.lower().str.contains(needle, na=False)
        )
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Export")
    st.download_button(
        "Download BOM CSV",
        data=pd.DataFrame(res["equipment"]).to_csv(index=False),
        file_name="dc_bom_concept.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Full JSON",
        data=json.dumps(res, indent=2),
        file_name="dc_concept_full.json",
        mime="application/json",
    )
'@

[System.IO.File]::WriteAllText("app.py", $app, (New-Object System.Text.UTF8Encoding($false)))