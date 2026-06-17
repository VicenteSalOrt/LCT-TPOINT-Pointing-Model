# Validation of TPOINT Pointing Models through Optical Metrology for the LCT Project 

This repository contains the software architecture and optomechanical design for an auxiliary optical metrology system. This system was designed for the **Leighton Chajnantor Telescope (LCT)** testbed, aiming to achieve a strict residual pointing accuracy of 2 to 3 arcseconds (RMS) for submillimeter observations in the 350 $\mu m$ band [1].

The project implements the *Optical Offset Pointing* technique, coupling a high-sensitivity CMOS sensor to a refractor to bypass the limitations of traditional radio frequency (RF) calibration [1].

## Software Architecture

The system's workflow is divided into three core components connecting starlight to servomotor control:

### 1. Optical Acquisition (`tpoint_prueba.py`)
Real-time script for data capture and metrology [3].
* **Mount Control:** Telescope handling and Settling Time to mitigate mechanical vibrations [4].
* **NTP Synchronized Capture:** Low-latency time-stamped control of the ZWO ASI220MM sensor to evade kinematic drag [5].
* **Plate Solving (Pattern Recognition):** Local integration with `Astrometry.net` to extract absolute equatorial coordinates (RA/Dec) [6].
* **Trigonometric Transformation:** Uses `Astropy` to project real coordinates into the local sky (Azimuth and Elevation) and compute the residual error ($\Delta AZ$, $\Delta EL$) in degrees [6, 7].

### 2. Mathematical Optimizer (`codigotpointfinal.py`)
The "Analytical Brain" based on the `scipy.optimize` library [8].
* **Digital Twin:** Python replica of David Woody's kinematic model, modeling 7 physical antenna parameters (collimation, encoder offsets, gravitational flexure, etc.) [8].
* **Least Squares:** Iterative algorithm that ingests the error `.csv`, transforms degrees to arcseconds, and deduces the exact mount defects by minimizing the cost function [9, 10].

### 3. Antenna Controller (`pointing.c`)
Legacy C code from the LCT observatory (originally developed for the Leighton telescopes).
* Consumes the 7 coefficients extracted by the Python optimizer to apply real-time trigonometric corrections to the motors.

## ⚙️ Hardware Requirements

* **Testbed:** Celestron NexStar 8SE Telescope (Focal length: 2032 mm) or TWB-50600 auxiliary refractor [11].
* **Metrology Camera:** CMOS ZWO ASI220MM Mini ($4.0 \mu m$ pixels, high NIR sensitivity) [12, 13].
* **Enclosure:** IP65-rated watertight housing with a dry air purge system to prevent condensation and thermal gradients [14, 15].

*(Note: The optical combination guarantees a focal resolution that induces controlled oversampling [RMS radius $\approx 31\mu m$], enabling sub-pixel accuracy and mitigating the pixel-locking error [16]).*

##  Installation & Dependencies

The Python environment requires the following scientific libraries, detailed in the `requirements.txt` file [3]:

```bash
pip install numpy pandas scipy astropy zwoasi pyserial matplotlib
It is strictly necessary to have a local installation of Astrometry.net or access to its API, as well as native drivers and the ZWO ASI SDK DLL (ASICamera2.dll)
.
 Usage (Concept of Operations)
Pointing Run: Run tpoint_prueba.py at night. The script will move the telescope through a grid of Tycho-2 catalog stars, waiting 3 seconds per target, capturing FITS images, and processing them.
Residual Generation: The system automatically outputs an output_para_pointing_c.csv file with the horizontal pointing deltas
.
Reverse Engineering: Run codigotpointfinal.py feeding it the CSV. The optimizer will iterate to find the root of the mechanical error
.
Closing the Loop: Copy the 7 generated parameters from the terminal and paste them into the .pcc configuration file of the LCT master control system in Linux (pointing.c).
 Additional Documentation
In the /docs folder you will find:
Requirements Verification Matrix (RVM): Traceability from the overarching scientific requirement (2 to 3 arcsec RMS) down to hardware and environmental control constraints
.
Pointing Error Budget: Detailed RSS allocation of error margins by subsystem validating a theoretical final accuracy of ≈2.60 
′′
 
.
 Author & Acknowledgments
Author: Vicente Maximiliano Salazar Ortega
.
Developed under the LCT Project framework at the Center for Astronomical Instrumentation (CePIA), Universidad de Concepción, Chile
.
