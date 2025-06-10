This repository (when complete) will go through:
1. Converting L1 NEON radiance files (H5) into ENVI binary format (.rad, .loc, .obs) files to be ISOFIT ready
2. Running ISOFIT on NEON Data

#### What is ISOFIT?
ISOFIT (Imaging Spectrometer Optimal Fit) is an open-source Python-based radiative transfer inversion framework that transforms airborne and spaceborne imaging spectrometer radiance data into surface reflectance. It supports both physical and statistical approaches to atmospheric correction, primarily relying on forward modeling through radiative transfer codes like MODTRAN. ISOFIT is designed to support hyperspectral remote sensing workflows and is used in NASA missions such as AVIRIS-NG, NEON AOP, and SBG for generating high-quality surface reflectance products, but it is designed to be agnostic and for use with non-science and non-NASA spectrometers.



#### Appendix
1. What is MODTRAN
2. What is foreward model
3. What is AVIRIS-NG
