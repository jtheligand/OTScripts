# Opentrons Workup Script Generator
A small UI for producing HTE plate workup scripts using volatile solvents for the Opentrons OT-2

Protocol scripts can either workup 3 HTE plates identically, consolidate 4 HTE plates, or do a serial dilution of a single plate

Workup protocols based on Opentrons documentation which can be found [here](https://opentrons-landing-img.s3.amazonaws.com/application+notes/Volatile_Liquid_Handling_App_Note.pdf)

Developed and tested using Python (3.9.18), Opentrons OT-2 (API version 2.15), Panel (1.2.3), Param (1.13.0), Jinja2 (3.1.2), and acetonitrile


