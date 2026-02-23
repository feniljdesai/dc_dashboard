from dataclasses import dataclass, asdict
import math

@dataclass(frozen=True)
class Inputs:
    it_mw: float
    avg_kw_per_rack: float
    pue_target: float

def compute(inputs: Inputs):
    it_kw = inputs.it_mw * 1000.0
    racks = int(math.ceil(it_kw / inputs.avg_kw_per_rack))
    facility_kw = it_kw * inputs.pue_target
    return {
        'inputs': asdict(inputs),
        'it_kw': it_kw,
        'racks': racks,
        'facility_kw': facility_kw,
        'equipment': [
            {'Category':'Electrical','Equipment':'UPS (placeholder)','Qty':1,'Unit capacity':inputs.it_mw,'Unit':'MW','Sizing basis':'IT MW','Notes':''},
            {'Category':'Mechanical','Equipment':'Cooling (placeholder)','Qty':1,'Unit capacity':facility_kw,'Unit':'kW','Sizing basis':'IT*PUE','Notes':''},
        ]
    }
