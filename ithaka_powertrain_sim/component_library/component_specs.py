"""
Generic component specifications for hybrid motorcycle powertrain design.

This module defines standardized specifications for engines, motors, batteries,
and fuel systems based on realistic performance parameters rather than 
specific manufacturer parts.
"""

ENGINE_SPECS = {
    "250cc_20kW": {
        "displacement_cc": 250,
        "max_power_kW": 20,
        "dry_mass_kg": 35,
        "efficiency_peak": 0.28,
        "rpm_peak_efficiency": 6000,
        "rpm_max": 10000,
        "description": "Small single cylinder engine - lightweight, basic performance"
    },
    "400cc_30kW": {
        "displacement_cc": 400,
        "max_power_kW": 30,
        "dry_mass_kg": 45,
        "efficiency_peak": 0.32,
        "rpm_peak_efficiency": 5500,
        "rpm_max": 9000,
        "description": "Medium single cylinder engine - good balance of power and efficiency"
    },
    "500cc_40kW": {
        "displacement_cc": 500,
        "max_power_kW": 40,
        "dry_mass_kg": 55,
        "efficiency_peak": 0.35,
        "rpm_peak_efficiency": 5000,
        "rpm_max": 8500,
        "description": "Large single cylinder engine - high torque, good efficiency"
    },
    "650cc_50kW": {
        "displacement_cc": 650,
        "max_power_kW": 50,
        "dry_mass_kg": 65,
        "efficiency_peak": 0.36,
        "rpm_peak_efficiency": 6000,
        "rpm_max": 9000,
        "description": "Twin cylinder engine - smooth power delivery"
    },
    "750cc_60kW": {
        "displacement_cc": 750,
        "max_power_kW": 60,
        "dry_mass_kg": 70,
        "efficiency_peak": 0.38,
        "rpm_peak_efficiency": 6500,
        "rpm_max": 9500,
        "description": "Sport twin engine - higher performance"
    },
    "1000cc_80kW": {
        "displacement_cc": 1000,
        "max_power_kW": 80,
        "dry_mass_kg": 85,
        "efficiency_peak": 0.40,
        "rpm_peak_efficiency": 7000,
        "rpm_max": 10000,
        "description": "Sport four cylinder engine - high performance"
    }
}

MOTOR_SPECS = {
    "5kW_Hub": {
        "max_power_kW": 5,
        "continuous_power_kW": 3,
        "dry_mass_kg": 12,
        "efficiency_peak": 0.88,
        "rpm_max": 3000,
        "type": "hub",
        "description": "Small hub motor - city commuting"
    },
    "10kW_Hub": {
        "max_power_kW": 10,
        "continuous_power_kW": 7,
        "dry_mass_kg": 18,
        "efficiency_peak": 0.90,
        "rpm_max": 4000,
        "type": "hub",
        "description": "Medium hub motor - urban transport"
    },
    "15kW_MidDrive": {
        "max_power_kW": 15,
        "continuous_power_kW": 12,
        "dry_mass_kg": 20,
        "efficiency_peak": 0.92,
        "rpm_max": 6000,
        "type": "mid_drive",
        "description": "Small mid-drive motor - versatile performance"
    },
    "30kW_MidDrive": {
        "max_power_kW": 30,
        "continuous_power_kW": 25,
        "dry_mass_kg": 28,
        "efficiency_peak": 0.94,
        "rpm_max": 8000,
        "type": "mid_drive",
        "description": "Medium mid-drive motor - good highway capability"
    },
    "50kW_HighPerf": {
        "max_power_kW": 50,
        "continuous_power_kW": 40,
        "dry_mass_kg": 35,
        "efficiency_peak": 0.95,
        "rpm_max": 10000,
        "type": "high_performance",
        "description": "High performance motor - sport riding"
    },
    "80kW_HighPerf": {
        "max_power_kW": 80,
        "continuous_power_kW": 65,
        "dry_mass_kg": 42,
        "efficiency_peak": 0.96,
        "rpm_max": 12000,
        "type": "high_performance",
        "description": "Very high performance motor - track capable"
    },
    "120kW_HighPerf": {
        "max_power_kW": 120,
        "continuous_power_kW": 95,
        "dry_mass_kg": 50,
        "efficiency_peak": 0.96,
        "rpm_max": 15000,
        "type": "high_performance",
        "description": "Ultra high performance motor - superbike class"
    }
}

BATTERY_SPECS = {
    "5kWh_180WhKg": {
        "capacity_kWh": 5.0,
        "energy_density_WhKg": 180,
        "power_density_WKg": 800,
        "cell_mass_kg": 27.8,
        "pack_overhead_kg": 8.0,
        "max_discharge_rate_C": 3.0,
        "efficiency": 0.92,
        "description": "Small energy-dense pack - city commuting"
    },
    "10kWh_200WhKg": {
        "capacity_kWh": 10.0,
        "energy_density_WhKg": 200,
        "power_density_WKg": 1000,
        "cell_mass_kg": 50.0,
        "pack_overhead_kg": 12.0,
        "max_discharge_rate_C": 3.5,
        "efficiency": 0.93,
        "description": "Medium balanced pack - versatile use"
    },
    "15kWh_220WhKg": {
        "capacity_kWh": 15.0,
        "energy_density_WhKg": 220,
        "power_density_WKg": 1200,
        "cell_mass_kg": 68.2,
        "pack_overhead_kg": 15.0,
        "max_discharge_rate_C": 4.0,
        "efficiency": 0.94,
        "description": "Large high-density pack - long range touring"
    },
    "20kWh_180WhKg": {
        "capacity_kWh": 20.0,
        "energy_density_WhKg": 180,
        "power_density_WKg": 1500,
        "cell_mass_kg": 111.1,
        "pack_overhead_kg": 20.0,
        "max_discharge_rate_C": 5.0,
        "efficiency": 0.92,
        "description": "Large power-dense pack - high performance"
    },
    "25kWh_200WhKg": {
        "capacity_kWh": 25.0,
        "energy_density_WhKg": 200,
        "power_density_WKg": 1300,
        "cell_mass_kg": 125.0,
        "pack_overhead_kg": 25.0,
        "max_discharge_rate_C": 4.5,
        "efficiency": 0.93,
        "description": "Extra large pack - maximum range"
    }
}

FUEL_TANK_SPECS = {
    "8L": {
        "capacity_liters": 8.0,
        "dry_mass_kg": 3.5,
        "fuel_density_kg_per_L": 0.75,
        "energy_density_MJ_per_kg": 43.0,
        "description": "Small tank - lightweight, basic range"
    },
    "15L": {
        "capacity_liters": 15.0,
        "dry_mass_kg": 5.5,
        "fuel_density_kg_per_L": 0.75,
        "energy_density_MJ_per_kg": 43.0,
        "description": "Standard tank - good balance of weight and range"
    },
    "25L": {
        "capacity_liters": 25.0,
        "dry_mass_kg": 8.0,
        "fuel_density_kg_per_L": 0.75,
        "energy_density_MJ_per_kg": 43.0,
        "description": "Large tank - maximum range, heavier"
    }
}