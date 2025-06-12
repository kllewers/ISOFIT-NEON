import h5py
import numpy as np
from spectral.io import envi
import sys
from typing import Tuple

def _write_bil_chunk(dat: np.array, outfile: str, line: int, shape: Tuple[int, int, int], dtype: str = 'float32') -> None:
    """Write a chunk of data to a BIL binary cube."""
    with open(outfile, 'rb+') as f:
        f.seek(line * shape[1] * shape[2] * np.dtype(dtype).itemsize)
        f.write(dat.astype(dtype).tobytes())

def convert_to_rad(h5_path: str, out_base: str) -> None:
    """Convert NEON HDF5 radiance data to BIL format readable by ENVI."""
    ds = h5py.File(h5_path, 'r')

    # --- Extract Radiance (Integer + Decimal Parts) ---
    group = list(ds.keys())[0]  # e.g., 'R10C'
    rad_int = ds[group]['Radiance']['RadianceIntegerPart']
    rad_dec = ds[group]['Radiance']['RadianceDecimalPart']
    radiance = rad_int[()] + rad_dec[()]  # Shape: (lines, samples, bands)

    # --- Extract Metadata ---
    md = ds[group]['Radiance']['Metadata']
    map_info = md['Coordinate_System']['Map_Info'][()].decode('utf-8').split(',')
    wl = [float(x) for x in md['Spectral_Data']['Wavelength'][()]]
    fwhm = [float(x) for x in md['Spectral_Data']['FWHM'][()]]

    # --- Prepare ENVI Metadata ---
    output_meta = {
        'lines': radiance.shape[0],
        'samples': radiance.shape[1],
        'bands': radiance.shape[2],
        'interleave': 'bil',
        'map info': map_info,
        'data type': 4,  # float32
        'wavelength': wl,
        'fwhm': fwhm,
    }

    # --- Create ENVI Image and Header ---
    output = envi.create_image(out_base + '.hdr', output_meta, ext='', force=True)
    mm = output.open_memmap()
    del mm, output

    # --- Write BIL Data Line-by-Line ---
    print("Reading...")
    print("Writing...")

    for _line in range(radiance.shape[0]):
        lr = radiance[_line:_line+1, ...].copy().astype(np.float32)
        _write_bil_chunk(lr.transpose((0, 2, 1)), out_base, _line, radiance.shape)
        if _line % 100 == 0:
            print(f'{_line}/{radiance.shape[0]}')

    print("Done writing .rad file!")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python rad_conversion.py <input_h5> <output_base>")
    else:
        h5_path = sys.argv[1]
        out_base = sys.argv[2]
        convert_to_rad(h5_path, out_base)
