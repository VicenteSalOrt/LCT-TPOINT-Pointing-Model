# Installation and Setup Guide 🛠️

This guide details the steps required to set up the software environment for the LCT Optical Pointing system, including the Python dependencies, the ZWO camera SDK, and the local Plate Solving engine.

## 1. Python Environment Setup
We recommend using a virtual environment (e.g., `venv` or `conda`) to avoid dependency conflicts.
Run the following command in your terminal to install all required libraries:

```bash
pip install -r requirements.txt
2. ZWO ASI Camera SDK Configuration
The zwoasi Python library acts as a wrapper and requires the native C++ SDK library (ASICamera2.dll for Windows or libASICamera2.so for Linux) to communicate with the CMOS sensor.
Download the ASI Camera SDK from the official ZWO Astronomy Cameras website.
Extract the SDK and locate the library file matching your operating system architecture (e.g., x64/ASICamera2.dll).
Place the .dll or .so file in the src/acquisition/ folder, or update the ruta_dll path in the tpoint_prueba.py script to point to your local installation path.
3. Astrometry.net (Local Plate Solving)
The acquisition module uses the solve-field command locally to extract the absolute RA/Dec coordinates from the FITS images without relying on an internet connection.
For Linux/macOS:
Install Astrometry.net directly through your package manager:
sudo apt-get install astrometry.net
For Windows:
Astrometry.net is natively a Linux application. To run it locally on Windows, you must:
Install WSL (Windows Subsystem for Linux) or Cygwin.
Install Astrometry.net within the Linux subsystem.
Download the index files (Tycho-2 catalog recommended for our FOV) and place them in the /usr/share/astrometry/data directory.
Ensure the solve-field command is accessible in the system's PATH so the Python subprocess module can invoke it.

***
