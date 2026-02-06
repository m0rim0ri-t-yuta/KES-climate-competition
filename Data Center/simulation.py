import pandas as pd

def simulate_full_system_balance():
    print("=== FINAL DESIGN SIMULATION: LNG-OCR-SERVER SYSTEM ===\n")
    
    # --- 1. INPUTS ---
    lng_flow_m3_day = 3310.0   # From previous 500MW Co-location scenario
    
    # Efficiencies
    hx_efficiency = 0.95
    turbine_efficiency_isentropic = 0.85
    generator_efficiency = 0.95
    orc_cycle_thermal_eff = 0.15 # Realistic thermal efficiency for this temp range
    
    # Fluid Properties for reference
    cp_lng = 3.5 # kJ/kg.K (Liquid Methane approx)
    cp_ocr = 2.4 # kJ/kg.K (Liquid Propane approx)
    lng_density = 450.0 # kg/m3
    
    # Specific Enthalpy Changes (Delta H)
    # LNG: -162C to -140C (Liquid+Gas phase change absorption)
    # Allows approx 600 kJ/kg absorption in the condenser (Latent 510 + Sensible)
    dh_lng_absorb = 600.0 # kJ/kg
    
    # OCR (Propane): Cycle Latent Heat
    # Propane latent heat is ~425 kJ/kg. 
    dh_ocr_cycle = 350.0 # kJ/kg (Effective working range in cycle)

    # Server Fluid (Water/Glycol)
    cp_water = 3.00 # kJ/kg.K
    t_server_in = 45.0
    t_server_out = 25.0
    dt_server = t_server_in - t_server_out # 20K delta T
    
    # --- 2. MASS BALANCE ---
    # Loop 1: LNG Flow
    m_dot_lng = (lng_flow_m3_day * lng_density) / (24 * 3600) # kg/s

    # Loop 2: OCR Flow
    # Heat Balance at Condenser: Q_cond = m_dot_lng * dh_lng * eff
    # For a Rankine cycle: Q_in (Evap) = W_out + Q_out (Cond)
    # W_out = Q_in * thermal_eff
    # Q_out = Q_in * (1 - thermal_eff)
    # -> Q_in = Q_out / (1 - thermal_eff)
    
    q_condenser_kw = m_dot_lng * dh_lng_absorb * hx_efficiency
    
    q_evaporator_kw = q_condenser_kw / (1.0 - orc_cycle_thermal_eff)
    w_turbine_kw = q_evaporator_kw - q_condenser_kw # Conservation of energy
    
    # OCR Mass Flow needed to carry this heat
    # Q_in = m_dot_ocr * dh_ocr
    m_dot_ocr = q_evaporator_kw / dh_ocr_cycle
    
    # Loop 3: Server Fluid Flow
    # Q_evaporator is the heat removed from servers
    # Q_evap = m_dot_server * Cp * dt
    m_dot_server = q_evaporator_kw / (cp_water * dt_server)

    # --- 3. POWER GENERATION ---
    # Turbine Output (mechanical -> electrical)
    w_gen_final_kw = w_turbine_kw * generator_efficiency
    w_gen_final_mw = w_gen_final_kw / 1000.0
    
    # --- 4. PUE CALCULATION ---
    # Cooling Capacity Provided (The 'Work' done by the cooling system)
    cooling_capacity_mw = q_evaporator_kw / 1000.0
    
    # Aux Power (Pumps for 3 loops)
    # REVISED: Calculated based on Flow Rates to reflect fluid properties (Cp) impact
    
    # 1. Server Pump (Water/Glycol)
    # Power = (Flow * Pressure_Drop) / Efficiency
    # Assume dP = 200 kPa (approx 20m head, typical for DCs), Pump Eff = 0.70
    vol_flow_server = m_dot_server / 1000.0 # m3/s (assuming ~1000 kg/m3)
    pump_power_server_kw = (vol_flow_server * 200.0) / 0.70
    
    # 2. LNG Pump (Cryogenic)
    # Assume dP = 100 kPa, Eff = 0.65 (Cryogenic pumps often lower eff)
    vol_flow_lng = m_dot_lng / lng_density # m3/s
    pump_power_lng_kw = (vol_flow_lng * 100.0) / 0.65
    
    # 3. OCR Pump (Working Fluid)
    # Feed pump delta P is driven by cycle pressure ratio.
    # Simplified: 5% of Turbine output (Rankine cycle rule of thumb)
    pump_power_ocr_kw = w_turbine_kw * 0.05
    
    aux_power_kw = pump_power_server_kw + pump_power_lng_kw + pump_power_ocr_kw
    aux_power_mw = aux_power_kw / 1000.0
    
    # Net Power of Cooling System
    # Net = Consumed - Generated
    net_cooling_power_mw = aux_power_mw - w_gen_final_mw
    
    # PUE (Local Zone)
    # PUE = (IT Load + Net Cooling Power) / IT Load
    # IT Load is equal to the heat we are removing (assuming 100% capture)
    it_load_mw = cooling_capacity_mw
    local_pue = (it_load_mw + net_cooling_power_mw) / it_load_mw

    # --- 5. OUTPUT ---
    print(f"[1] HEAT & MASS BALANCE TABLE")
    print(f"{'LOOP':<15} | {'FLUID':<15} | {'Cp (kJ/kg.K)':<15} | {'FLOW RATE (kg/s)':<18} | {'HEAT TRANSFER (MW)':<18}")
    print("-" * 90)
    print(f"{'1. Heat Sink':<15} | {'LNG (-162C)':<15} | {cp_lng:<15.2f} | {m_dot_lng:<18.2f} | {q_condenser_kw/1000:<18.2f} (Rejected)")
    print(f"{'2. OCR Cycle':<15} | {'R290 Propane':<15} | {cp_ocr:<15.2f} | {m_dot_ocr:<18.2f} | {w_gen_final_mw:<18.2f} (Gen. Out)")
    print(f"{'3. Heat Source':<15} | {'Water/Glycol':<15} | {cp_water:<15.2f} | {m_dot_server:<18.2f} | {cooling_capacity_mw:<18.2f} (Absorbed)")
    print("-" * 90)
    
    print(f"\n[2] TURBINE PERFORMANCE")
    print(f"  Input Heat (Q_in)      : {q_evaporator_kw/1000:.2f} MW (Waste heat from Servers)")
    print(f"  Rejected Heat (Q_out)  : {q_condenser_kw/1000:.2f} MW (Absorbed by LNG)")
    print(f"  Gross Turbine Power    : {w_turbine_kw/1000:.2f} MW")
    print(f"  Net Generator Output   : {w_gen_final_mw:.2f} MW")
    
    print(f"\n[3] EFFICIENCY METRICS")
    print(f"  IT Load Supported      : {cooling_capacity_mw:.2f} MW")
    print(f"  Auxiliary Consumption  : {aux_power_mw:.2f} MW (Pumps/Fans)")
    print(f"  Net Power Balance      : {net_cooling_power_mw:.2f} MW (Aux - Gen)")
    if net_cooling_power_mw < 0:
        print(f"    -> System GENERATES {abs(net_cooling_power_mw):.2f} MW more than it consumes!")
    
    print(f"\n  ✅ LOCAL PUE           : {local_pue:.4f}")
    if local_pue < 1.0:
        print("     (Performance exceeds 1.0 because the cooling system is a net power generator)")

    # --- 6. SCENARIO: 360 MW DATA CENTER ---
    print(f"\n[4] SCENARIO ANALYSIS: 360 MW FULL SCALE DATA CENTER")
    target_it_load_mw = 360.0
    scaling_factor = target_it_load_mw / it_load_mw
    
    print(f"  Scaling Factor         : {scaling_factor:.2f}x (Based on current LNG flow simulation)")
    
    # Baseline Scenario (Traditional Chiller System)
    # Assumption: Standard Efficient DC with PUE 1.35 (0.35 power overhead)
    baseline_pue = 1.35
    baseline_cooling_power_mw = target_it_load_mw * (baseline_pue - 1.0)
    
    # Proposed Scenario (LNG-OCR System)
    # Scaled Net Power (Negative means Generation)
    proposed_net_power_mw = net_cooling_power_mw * scaling_factor
    
    # Total Savings (Power)
    # Savings = (Power you WOULD have used) - (Power you ARE using)
    # If proposed is negative (generating), you save the consumption AND gain the generation.
    total_power_saving_mw = baseline_cooling_power_mw - proposed_net_power_mw
    
    # Annual Energy Savings
    hours_per_year = 8760
    total_energy_saving_gwh = (total_power_saving_mw * hours_per_year) / 1000.0
    
    # Required LNG Flow
    required_lng_flow_m3_day = lng_flow_m3_day * scaling_factor
    
    print(f"  Required LNG Flow      : {required_lng_flow_m3_day:,.0f} m3/day")
    print("-" * 60)
    print(f"  Baseline Cooling Cost  : {baseline_cooling_power_mw:.2f} MW (Consumed @ PUE {baseline_pue})")
    print(f"  LNG-OCR System Cost    : {proposed_net_power_mw:.2f} MW (Net Generation)")
    print("-" * 60)
    print(f"  TOTAL POWER SAVED      : {total_power_saving_mw:.2f} MW")
    print(f"  ANNUAL ENERGY SAVED    : {total_energy_saving_gwh:.2f} GWh/year")
    print("-" * 60)
    
    # CO2 Savings Estimate (US Grid Average ~0.37 kg/kWh or 370 tonnes/GWh)
    co2_factor_tonnes_gwh = 370.0
    co2_saved_tonnes = total_energy_saving_gwh * co2_factor_tonnes_gwh
    print(f"  EST. CO2 REDUCTION     : {co2_saved_tonnes:,.0f} tonnes/year")

if __name__ == "__main__":
    simulate_full_system_balance()
