# Co-location as an Alternative to Waiting for Grid Interconnection

Financial models for an undergraduate research project on whether renewable energy projects stuck in the CAISO interconnection queue could build early and sell power **behind the meter (BTM)** to an adjacent AI data center while they wait for a grid connection.

**Author:** Leyao Zhang, Rausser College of Natural Resources, UC Berkeley
**Program:** Sponsored Projects for Undergraduate Research (SPUR), Summer 2026
**Status:** Work in progress. The models support a working paper that is still in draft, so all results are preliminary.

---

## Research question

A developer with a project in the CAISO interconnection queue can either:

1. **Wait** to build until the interconnection agreement is in place, and earn nothing until commercial operation, or
2. **Build early and co-locate** by selling output through a dedicated microgrid to an adjacent data center until the grid connection is ready.

The project asks whether option 2 raises the developer's return **and** lowers the data center's delivered cost of electricity compared with waiting for the grid.

## Preliminary findings (Draft 3, October 2026)

- At the commonly cited BTM price of **$60/MWh**, co-location gives a *lower* developer levered IRR than waiting. This holds for all three configurations and at every delay tested. That price is below the $72/MWh grid PPA and below the LCOE of the solar and wind configurations.
- The data center's all-in grid alternative is estimated at about **$163/MWh**. Between this ceiling and each configuration's cost floor, the model finds a mutually acceptable price range **$63–75/MWh wide**. Within that range the developer earns more than its cost of capital and the data center cuts its delivered cost by **26–28%**.
- At the midpoint of that range, co-location beats waiting once the grid delay exceeds about **4 years for solar** and **2 years for wind**. For **geothermal** it wins at every delay tested.
- Most of the value comes from the **transmission, distribution, and capacity charges** that the data center avoids.

## Documentation

**[Model Guide](docs/model-guide.md)** walks through the full methodology: how the four models connect, the key formulas (capital stack, cash flow waterfall, LCOE, pricing range), every major assumption and its source, base-case results, how to run scenarios, and the version history.

## Repository contents

```
docs/
  model-guide.md                   Detailed methodology and assumptions
models/
  SPUR_Combined_Model_v8.xlsx      Current model (data source for Working Paper Draft 3)
  archive/                         Earlier versions, kept for reference
    SPUR_Combined_Model_v7.xlsx
    SPUR_Preliminary_Model_v3.xlsx / v5 / v7
    SPUR_Model3_DC_Cost_v1.xlsx
```

## Model structure (`SPUR_Combined_Model_v8.xlsx`)

Four linked models live in one workbook. Start at the `_Index` sheet.

| Model | Sheets | What it does |
|---|---|---|
| **1. Electricity price benchmark** | `M1_Inputs`, `M1_Benchmarks`, `M1_Scenarios`, `M1_Notes` | Derives low / average / high CAISO wholesale price benchmarks from CAISO Department of Market Monitoring (DMM) data. Builds a 3×3 load × carbon scenario matrix and a spot-to-PPA bridge. |
| **2. Project-level DCF** | `Inputs`, `Configurations`, `Capitalization`, `SolarBase` … `GeoColoc`, `Results` | Annual cash flow waterfalls with tax-equity partnership-flip capitalization for three configurations: **Solar+BESS 100 MW, Wind+BESS 150 MW, Geothermal+BESS 100 MW**. Each has a *Base* case (wait for the grid) and a *Coloc* case (BTM sales during the wait). Reports levered and unlevered IRR, NPV, and a value bridge. |
| **3. Data center delivered cost** | `M3_Inputs`, `M3_Coverage`, `M3_StructA_B`, `M3_StructC`, `M3_Results` | Compares the data center's all-in cost under (A) a utility tariff (PG&E B-20), (B) a sleeved grid PPA, and (C) BTM co-location. |
| **4. Bilateral BTM pricing** | `M4_LCOE`, `M4_Bounds`, `M4_Pricing`, `M4_Notes` | Bounds the BTM price between the developer's LCOE (floor) and the data center's grid alternative (ceiling). Tests two-sided viability across a bargaining-share parameter α. |
| **Figures** | `Fig2_Breakeven`, `Fig3_Zone`, `Fig4_Alpha` | Data behind the paper's figures. `Fig2` and `Fig4` hold static sweep values pasted from full model runs. `Fig3` is linked live to Model 4. |

### How to use

Open the workbook in Excel. The scenario levers are the yellow cells on the `Inputs` sheet:

- **Grid connection delay** (years; the paper tests 2 / 4 / 6 / 8)
- **ITC rate** (0% or 30%)
- **Credit type** (ITC or PTC)
- **BTM price source** (a single global price, or the per-configuration price from Model 4)
- **Baseline specification** (construction deferred until the grid is ready, or built and then idle)

Results update live on `Results`, `M3_Results`, and the `M4_*` sheets. Colour convention: blue = hard-coded input, green = linked from another sheet, yellow = scenario lever.

## Key data sources

- **NREL Annual Technology Baseline (ATB) 2024**: CAPEX, OPEX, capacity factors
- **LBNL *Queued Up* (2025)**: interconnection queue durations
- **LBNL *Utility-Scale Solar***: contracted hybrid PPA prices ($72/MWh grid PPA)
- **CAISO Department of Market Monitoring**: wholesale price statistics (Model 1)
- **PG&E Schedule B-20**: large C&I tariff for the data center's grid alternative
- Federal tax credit assumptions reflect the post-OBBBA landscape (ITC/PTC scenarios)

Sources for each parameter are cited next to the cell in the workbook.

## Known limitations / open items

- **Model 3 still has placeholder inputs**, for example data center utilization, the PCIA charge, standby / departing-load tariffs, and backup generation costs. They are labelled `Placeholder` in `M3_Inputs` and `M3_StructA_B` and will be replaced with sourced values.
- Cash flows are **annual, not hourly**. Battery round-trip losses are approximated as a flat percentage, and the mismatch between as-generated renewable output and a flat data center load is handled at the annual energy-balance level.
- The figure sheets `Fig2_Breakeven` and `Fig4_Alpha` contain static values from earlier model runs and do not recalculate when inputs change.

## Acknowledgements

Thanks to my SPUR mentor for guidance and comments on the model and paper drafts.
