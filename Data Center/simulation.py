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
    
    # --- MODIFIED: FW + FAN COOLING SIMULATION ---
    # The previous LNG-OCR loop is commented out to focus on FW (Fresh Water) + Fan cooling.
    
    # 1. Define Target Load directly
    target_it_load_mw = 360.0
    heat_load_kw = target_it_load_mw * 1000.0

    print(f"[1] SYSTEM PARAMETERS (FW + FAN COOLING)")
    print(f"  Target IT Load         : {target_it_load_mw:.2f} MW")
    
    # 2. Fan System (Airflow across servers/CRAH)
    # Assumption: Delta T of Air = 15°C (Typical efficient containment)
    cp_air = 1.006 # kJ/kg.K
    rho_air = 1.2 # kg/m3
    dt_air = 15.0 # K
    
    # Mass flow of air required to remove heat: Q = m * Cp * dt
    m_dot_air = heat_load_kw / (cp_air * dt_air) # kg/s
    vol_flow_air = m_dot_air / rho_air # m3/s
    
    # Fan Power Calculation
    # Rule of thumb or specific fan laws. Modern EC fans ~ 0.2 kW/(m3/s) roughly
    # Or typically 5-10% of IT load for efficient systems. Let's calculate via pressure.
    # dP_air_total = 500 Pa (approx 2 inches WG, filters + coils + servers)
    # Fan Eff = 0.70
    dp_air = 600.0 # Pa
    fan_efficiency = 0.70
    fan_power_kw = (vol_flow_air * dp_air) / fan_efficiency / 1000.0 * 1000 # Correct to Watts then kW... wait formula is (m3/s * Pa) = Watts
    fan_power_kw = (vol_flow_air * dp_air) / fan_efficiency / 1000.0 # kW
    
    # 3. FW (Fresh Water) System
    # Heat is transferred from Air to Water via CRAH/CRAU coils
    # Assumption: Delta T of Water = 8°C (Typical Chilled Water) -> Higher dT like 12°C for modern
    cp_water = 4.18 # kJ/kg.K
    dt_water = 10.0 # K
    
    m_dot_fw = heat_load_kw / (cp_water * dt_water) # kg/s
    vol_flow_fw = m_dot_fw / 1000.0 # m3/s (approx density)
    
    # Pump Power (FW Loop)
    # dP_water = 300 kPa (Piping + HEX + Valves)
    # Pump Eff = 0.75
    dp_water = 350.0 # kPa
    pump_efficiency = 0.75
    pump_power_kw = (vol_flow_fw * dp_water) / pump_efficiency
    
    # 4. Heat Rejection (Chiller / Cooling Tower)
    # Assuming FW implies use of Fresh Water source (River/Lake) OR Cooling Tower.
    # If "FW" implies raw fresh water usage (River Cooling / Free Cooling):
    # Then just pump power (Source Pump) is needed aside from internal loop.
    # Let's assume a Source Pump is needed to bring FW in/out.
    # Source Pump: Low head if river, high flow.
    vol_flow_source = vol_flow_fw # Assume 1:1 via Heat Exchanger to keep internal loop clean
    dp_source = 200.0 # kPa
    source_pump_power_kw = (vol_flow_source * dp_source) / pump_efficiency
    
    # Total Cooling Power
    total_cooling_power_kw = fan_power_kw + pump_power_kw + source_pump_power_kw
    total_cooling_power_mw = total_cooling_power_kw / 1000.0
    
    # PUE Calculation
    pue = (target_it_load_mw + total_cooling_power_mw) / target_it_load_mw
    
    # --- OUTPUT ---
    print(f"\n[2] COMPONENT ANALYSIS")
    print(f"  A. Air Handling (Fans)")
    print(f"     Flow Rate           : {vol_flow_air:,.0f} m3/s")
    print(f"     Power Consumption   : {fan_power_kw/1000:.2f} MW")
    print(f"  B. Internal FW Loop (Pumps)")
    print(f"     Flow Rate           : {vol_flow_fw*1000:,.0f} L/s")
    print(f"     Power Consumption   : {pump_power_kw/1000:.2f} MW")
    print(f"  C. Heat Rejection (Source Pumps - River/Lake)")
    print(f"     Power Consumption   : {source_pump_power_kw/1000:.2f} MW")
    
    print(f"\n[3] PERFORMANCE RESULTS")
    print(f"  IT Load                : {target_it_load_mw:.2f} MW")
    print(f"  Total Cooling Power    : {total_cooling_power_mw:.2f} MW")
    print(f"  ✅ ESTIMATED PUE       : {pue:.4f}")
    
    print("-" * 60)
    print("NOTE: This simulation assumes a highly efficient water-cooled design (River/Lake Source).")
    print("      Does not include mechanical chiller compressor power (Free Cooling presumed).")
    print("      If chillers are required, PUE would typically increase to 1.3 - 1.4.")
    print("-" * 60)

    # --- COMMENTED OUT: OLD LNG-OCR LOGIC ---
    """
    # Mass Balance
    # Loop 1: LNG Flow
    m_dot_lng = (lng_flow_m3_day * lng_density) / (24 * 3600) # kg/s

    # Loop 2: OCR Flow
    q_condenser_kw = m_dot_lng * dh_lng_absorb * hx_efficiency
    
    q_evaporator_kw = q_condenser_kw / (1.0 - orc_cycle_thermal_eff)
    w_turbine_kw = q_evaporator_kw - q_condenser_kw 
    
    m_dot_ocr = q_evaporator_kw / dh_ocr_cycle
    
    # Loop 3: Server Fluid Flow
    m_dot_server = q_evaporator_kw / (cp_water * dt_server)

    # Power Generation
    w_gen_final_kw = w_turbine_kw * generator_efficiency
    w_gen_final_mw = w_gen_final_kw / 1000.0
    
    # ... (Rest of the old logic) ...
    """


if __name__ == "__main__":
    simulate_full_system_balance()
