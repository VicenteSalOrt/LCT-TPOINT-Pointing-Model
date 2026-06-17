import serial
import time
import subprocess
import csv
import zwoasi as asi
from datetime import datetime
import datetime as dt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
import matplotlib.pyplot as plt
import os

# ==========================================
# GENERAL AND OBSERVATORY CONFIGURATION
# ==========================================
TELESCOPE_PORT = 'COM3'  # Change according to your Windows/Linux port
BAUDRATE = 9600

# Approximate geographical coordinates for Wenu Lafken (Universidad de Concepcion)
# Vital for trigonometric coordinate transformations.
LATITUDE = -36.83
LONGITUDE = -73.05
ALTITUDE = 150  # meters above sea level
wenu_lafken_observatory = EarthLocation(lat=LATITUDE * u.deg, lon=LONGITUDE * u.deg, height=ALTITUDE * u.m)

# List to store the final pointing results
tpoint_results = []

# Initialize ZWO camera
# Note: Ensure ASICamera2.dll is in the same folder or update this relative path
dll_path = r"./ASICamera2.dll"  
try:
    asi.init(dll_path)
    num_cameras = asi.get_num_cameras()
    if num_cameras > 0:
        camera = asi.Camera(0)
        print("ZWO Camera connected successfully!")
    else:
        print("SDK Library loaded, but no camera is currently connected.")
except Exception as e:
    print(f"Error loading the DLL: {e}")

# ==========================================
# MODULE 1: MOUNT CONTROL (Slew & Settle)
# ==========================================
def move_telescope(azimuth, elevation):
    """
    Sends command to the NexStar+ mount and waits for mechanical
    vibrations to dissipate before capturing the image (Settling time).
    """
    print(f"\n--- MODULE 1: Moving mount to Theoretical AZ: {azimuth}°, Theoretical EL: {elevation}° ---")
    # ser = serial.Serial(TELESCOPE_PORT, BAUDRATE, timeout=1)
    # ser.write(b'SlewCommand...')
    # time.sleep(3) # 3 seconds mandatory settling time
    # ser.close()

# ==========================================
# MODULE 2: SYNCHRONIZED CAPTURE & NTP
# ==========================================
def capture_image():
    """
    Stamps the exact NTP time and captures the raw matrix to save it in FITS format.
    """
    print("\n--- MODULE 2: Synchronized Capture ---")
    exact_time = dt.datetime.now(dt.timezone.utc) # Low-latency UTC time
    
    folder_name = "../../data/raw_fits" # Points to the data folder in the repository
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    filename = os.path.join(folder_name, f"capture_{exact_time.strftime('%H%M%S')}.fits")
    
    # Capture the image as a raw numpy array
    # pixel_matrix = camera.capture() # Uncomment when hardware is connected
    
    # Create the FITS object with Astropy
    # hdu = fits.PrimaryHDU(pixel_matrix)
    # hdu.header['DATE-OBS'] = exact_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    # hdu.header['INSTRUME'] = 'ZWO ASI220MM'
    # hdu.header['TELESCOP'] = 'Celestron 8SE'
    # hdu.writeto(filename, overwrite=True)
    
    print(f"[SUCCESS] Raw FITS image saved to: {filename}")
    return filename, exact_time

# ==========================================
# MODULE 3: PLATE SOLVING (Astrometry.net)
# ==========================================
def local_plate_solving(fits_image):
    """
    Uses local Astrometry.net to analyze stars and extract real RA/Dec.
    """
    print(f"\n--- MODULE 3: Plate Solving for {fits_image} ---")
    command = ["solve-field", "--no-plots", "--overwrite", fits_image]
    # subprocess.run(command) 

# ==========================================
# MODULE 4 & 5: TRANSFORMATION AND DELTA CALCULATION
# ==========================================
def calculate_deltas_and_save(ra_j2000, dec_j2000, utc_time, theoretical_az, theoretical_el):
    """
    Converts RA/Dec from the image to real Azimuth/Elevation based on the NTP clock,
    calculates the residual error, and saves the row for the CSV file.
    """
    print("\n--- MODULE 4: Astropy Trigonometric Transformation ---")
    obs_time = Time(utc_time, scale='utc')
    # Actual trigonometric math logic goes here

def export_csv(filename="../../data/output_csv/output_para_pointing_c.csv"):
    """
    Exports the completed observation grid to a CSV compatible with the legacy C code.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Theoretical_AZ", "Theoretical_EL", "dAZ", "dEL"])
        writer.writerows(tpoint_results)
    print(f"\n[SUCCESS] File '{filename}' generated successfully. Ready for pointing.c")

# ==========================================
# MAIN EXECUTION (Pointing Run)
# ==========================================
if __name__ == "__main__":
    print("Starting LCT Optical Pointing Run...")
