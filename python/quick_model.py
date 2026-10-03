"""
Preliminary illustrative run — SPUR co-location model (simplified, single configuration)
Solar + BESS, 100 MW / 50 MW-200 MWh, CAISO

Early Python prototype of Model 2. The Excel workbook (models/SPUR_Combined_Model_v8.xlsx)
is the current model; this script is kept as a simplified, readable reference.
Differences from v8: solar only; baseline = built then idle until COD (Draft 1
specification, not v8's deferred construction); flat $60 BTM price; flip in year 8.

Implements the framework in SPUR_Financial_Modeling_Framework (May 2026), simplified:
 - Annual (not hourly) cash flows; BESS RTE losses approximated as 1% of delivered energy
 - Phase 2 revenue assumed equal in both scenarios (BTM PPA reprices to grid-equivalent
   at COD), so the measured delta isolates the queue-wait window
 - Reserves omitted; debt sized to DSCR = 1.35 on first grid-year EBITDA
Sources: CAPEX/OPEX midpoints from NREL ATB 2024 (https://atb.nrel.gov/electricity/2024/technologies);
grid price $72/MWh = LBNL contracted hybrid PPA level (https://emp.lbl.gov/utility-scale-solar);
BTM price $60/MWh = ~17% discount to the grid PPA (industry 10-20% convention).

Requires: numpy, numpy-financial, matplotlib
Run:      python quick_model.py   (prints the scenario sweep, saves breakeven_preliminary.png)
"""
import numpy as np
import numpy_financial as npf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- fixed parameters (framework midpoints) ----------------
CAP_MW        = 100
CF            = 0.275
CAPEX         = 197e6          # framework 2.2.3 illustrative build-up
QUAL_INV      = 180e6          # generation + BESS only (2.2.4)
MICROGRID     = 12e6           # $50-150/kW midpoint ~ $120/kW
GRID_PRICE    = 72.0           # $/MWh
BTM_PRICE     = 60.0           # $/MWh
DEBT_RATE     = 0.055
DEBT_TENOR    = 20
DSCR_TARGET   = 1.35
TAX_RATE      = 0.2984
MACRS         = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]
OPS_LIFE      = 25             # years from mechanical completion
CONSTR_YRS    = 2
FLIP_T        = 8              # calendar year of flip (framework table)
BUYOUT        = 1e6

LAND_INS      = 0.3e6 + 0.004 * CAPEX          # land lease + insurance
OM_FIXED      = 1.75e6 + 1.25e6                 # gen O&M + BESS O&M
MG_OM         = 0.75e6                          # microgrid O&M ($7.5/kW-yr)
AM_PCT        = 0.015                           # asset mgmt, % of revenue

def net_energy(op_year):
    gross = CAP_MW * CF * 8760.0               # MWh
    return gross * (1 - 0.005) ** op_year * 0.98 * 0.975

def tax_equity_contribution(itc_rate):
    if itc_rate <= 0:
        return 0.0                              # partnership collapses (Scenario D)
    itc = QUAL_INV * itc_rate
    basis = QUAL_INV - 0.5 * itc
    shield_pv = sum(basis * m * TAX_RATE / 1.07 ** (i + 1) for i, m in enumerate(MACRS))
    return 0.80 * (itc + shield_pv)             # TE pays ~80c per $ of benefit PV

def run(queue_years, itc_rate, coloc):
    total_capex = CAPEX + (MICROGRID if coloc else 0)
    # --- size debt to DSCR on first grid-phase year EBITDA ---
    e0 = net_energy(0)
    rev_grid = e0 * GRID_PRICE
    ebitda_grid = rev_grid - (OM_FIXED + LAND_INS + AM_PCT * rev_grid + (MG_OM if coloc else 0))
    ds_max = ebitda_grid / DSCR_TARGET
    ann_factor = (1 - (1 + DEBT_RATE) ** -DEBT_TENOR) / DEBT_RATE
    debt = ds_max * ann_factor
    te = tax_equity_contribution(itc_rate)
    dev_equity = total_capex - debt - te

    T_end = CONSTR_YRS + OPS_LIFE               # last operating calendar year
    dev_cf = [-dev_equity] + [0.0] * CONSTR_YRS
    for t in range(CONSTR_YRS + 1, T_end + 1):
        op = t - (CONSTR_YRS + 1)
        e = net_energy(op)
        in_queue = t <= CONSTR_YRS + queue_years
        if in_queue and not coloc:
            rev, opex = 0.0, LAND_INS           # idle: carrying costs only
        elif in_queue and coloc:
            rev = e * 0.99 * BTM_PRICE          # ~1% BESS RTE loss on delivered energy
            opex = OM_FIXED + LAND_INS + MG_OM + AM_PCT * rev
        else:
            rev = e * GRID_PRICE                # Phase 2 identical across scenarios
            opex = OM_FIXED + LAND_INS + (MG_OM if coloc else 0) + AM_PCT * rev
        ds = ds_max if t <= CONSTR_YRS + DEBT_TENOR else 0.0
        dc = rev - opex - ds
        share = 0.70 if (t <= FLIP_T and te > 0) else 0.975
        cash = dc * share
        if t == FLIP_T and te > 0:
            cash -= BUYOUT
        dev_cf.append(cash)
    return npf.irr(dev_cf), dev_equity, debt, te

# ---------------- scenario sweep ----------------
print(f"{'ITC':>4} {'Q(yr)':>5} {'Base IRR':>9} {'Coloc IRR':>10} {'Δ (pp)':>7}")
results = {}
for itc in (0.30, 0.0):
    for q in (2, 4, 6, 8):
        irr_b, eq_b, debt, te = run(q, itc, coloc=False)
        irr_c, eq_c, _, _ = run(q, itc, coloc=True)
        results[(itc, q)] = (irr_b, irr_c)
        print(f"{itc:>4.0%} {q:>5} {irr_b:>9.2%} {irr_c:>10.2%} {100*(irr_c-irr_b):>7.2f}")
    print(f"  capitalization @ ITC {itc:.0%}: debt ${debt/1e6:.0f}M | tax equity ${te/1e6:.0f}M | dev equity ${eq_b/1e6:.0f}M (base) / ${eq_c/1e6:.0f}M (coloc)")

# ---------------- breakeven chart ----------------
q_fine = np.arange(1, 9)
fig, ax = plt.subplots(figsize=(7, 4.2))
for itc, style in ((0.30, "-"), (0.0, "--")):
    base = [run(q, itc, False)[0] for q in q_fine]
    col  = [run(q, itc, True)[0] for q in q_fine]
    ax.plot(q_fine, [100*x for x in base], style, color="#888888",
            label=f"Baseline, ITC {itc:.0%}")
    ax.plot(q_fine, [100*x for x in col], style, color="#1a6b3c",
            label=f"Co-location, ITC {itc:.0%}")
ax.set_xlabel("Post-completion queue wait, mechanical completion → COD (years)")
ax.set_ylabel("Developer levered IRR (%)")
ax.set_title("Preliminary illustrative run — Solar+BESS 100 MW, CAISO\n(BTM $60/MWh, grid $72/MWh (hybrid PPA); NREL ATB 2024 cost midpoints)", fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("breakeven_preliminary.png", dpi=160)
print("chart saved")
