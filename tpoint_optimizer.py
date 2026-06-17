import pandas as pd
import numpy as np
from scipy.optimize import least_squares
import os

# ==========================================
# BLOCK 1: DIGITAL TWIN (Woody's Kinematic Model)
# ==========================================
def woody_model(p, az, el):
    """
    Calculates the theoretical dAZ and dEL corrections based on the 7 kinematic parameters.
    Inputs 'az' and 'el' must be in radians.
    """
    # UNPACKING: Assign the 7 array values to direct variables.
    # This avoids using brackets and prevents dimension errors.
    A1, M1, M3, M4, M5, A2, A3 = p

    # Theoretical kinematic equations (First-order)
    # (Note: These reflect the standard 7-parameter TPOINT mathematical model)
    daz_calc = A1 + M1 * np.cos(el) + M3 * np.sin(el) - M4 * np.sin(az) * np.sin(el) - M5 * np.cos(az) * np.sin(el)
    del_calc = A2 + A3 * np.cos(el) - M4 * np.cos(az) + M5 * np.sin(az)

    return daz_calc, del_calc

# ==========================================
# BLOCK 2: COST FUNCTION (Error Evaluation)
# ==========================================
def error_function(p, az, el, dAZ_measured, dEL_measured):
    """
    Calculates the residual difference between the empirical error measured by the ZWO camera
    and the theoretical error predicted by the Woody model.
    The SciPy least_squares engine will iteratively minimize this difference to zero.
    """
    dAZ_calc, dEL_calc = woody_model(p, az, el)

    # The residuals are the difference between measured and calculated errors
    residual_az = dAZ_measured - dAZ_calc
    residual_el = dEL_measured - dEL_calc

    # least_squares requires a 1D array of residuals
    return np.append(residual_az, residual_el)

# ==========================================
# BLOCK 3: DATA INGESTION & LEAST SQUARES ENGINE
# ==========================================
def calculate_tpoint_parameters(csv_filename):
    print(f"Loading photometric data from '{csv_filename}'...")
    
    try:
        # Ingest data using Pandas
        data = pd.read_csv(csv_filename)
    except FileNotFoundError:
        print("[ERROR] CSV file not found. Ensure you run the Pointing Run (Acquisition Module) first.")
        return

    print("[SUCCESS] Data loaded. Starting mathematical optimization...")

    # Extract coordinates (Convert degrees to radians for trigonometric functions)
    az_theoretical = np.radians(data['Theoretical_AZ'].values)
    el_theoretical = np.radians(data['Theoretical_EL'].values)

    # Extract measured errors and convert them from degrees to arcseconds ('')
    # This ensures 100% compatibility with the legacy pointing.c code
    dAZ_measured = data['dAZ'].values * 3600.0
    dEL_measured = data['dEL'].values * 3600.0

    # Initial guess for the 7 parameters: [A1, M1, M3, M4, M5, A2, A3]
    p0 = np.zeros(7)

    # Run the Least Squares optimization engine
    result = least_squares(error_function, p0, args=(az_theoretical, el_theoretical, dAZ_measured, dEL_measured))

    # Unpack the optimized physical defects discovered by the algorithm
    A1_opt, M1_opt, M3_opt, M4_opt, M5_opt, A2_opt, A3_opt = result.x

    # Output generation
    print("\n" + "="*60)
    print(" OPTIMIZATION SUCCESSFUL: 7 TPOINT PARAMETERS EXTRACTED")
    print("="*60)
    print(f"A1 (Azimuth Collimation)      : {A1_opt:>8.4f} arcsec")
    print(f"M1 (Azimuth Encoder Offset)   : {M1_opt:>8.4f} arcsec")
    print(f"M3 (Elevation Axis Skew)      : {M3_opt:>8.4f} arcsec")
    print(f"M4 (North-South Axis Tilt)    : {M4_opt:>8.4f} arcsec")
    print(f"M5 (East-West Axis Tilt)      : {M5_opt:>8.4f} arcsec")
    print(f"A2 (Elevation Collimation)    : {A2_opt:>8.4f} arcsec")
    print(f"A3 (Gravitational Flexure)    : {A3_opt:>8.4f} arcsec")
    print("="*60)
    print(">>> Ready to be copied into the LCT pointing.c configuration file (.pcc).")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Relative path pointing to the data folder in the repository
    csv_path = "../../data/output_csv/output_para_pointing_c.csv"
    calculate_tpoint_parameters(csv_path)
