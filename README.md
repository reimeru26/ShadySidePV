# ShadySidePV
Calculate the shadow around vertical objects. Working example are vertical PV panels.

## Motivation
Solar panels transform sunshine into electric power. The shaded areas around the panels receive
less sunlight, which may have an impact on biodiversity. This software calculates the effect of the shadow: change in radiation that is perceived on the ground near vertical objects. Time period can be days, weeks, moths, years. Read more in the documentation file (PDF).

## How to run 
There are four files:
- module-single.py (creates a single vertical object)
- module-multi.py (creates four vertical objects in a row, see the shadows overlap)
- Timeseries_shadow_2023.csv (Radiation data from the PVGIS website. Check out the project SunDriver for info about that.)
- ShadySidesPV_documentation.pdf (what is does and examples)

Simply run the Python files from the command line or create a batch file.
(Check out the project SunDriver for info about that.)
Output is a *.PNG file that shows radiation distribution accumulated over time.

The following software needs to be installed on your computer:
- Python (version 3.12.4 was used for development)
- Matplotlib for Python
- PANDAS for Python

This was work for a project.
