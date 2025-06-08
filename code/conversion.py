import h5py
import numpy as np
from spectral.io import envi
import sys

def _write_bil_chunk(dat: np.array, outfile: str, line: int, shape: tuple, dtype: str = 'float32') -> None:
    """Write a chunk of data to a BIL binary cube."""
    with open(outfile, 'rb+') as outfile:
        outfile.seek(line * shape[1] * shape[2] * np.dtype(dtype).itemsize)
        outfile.write(dat.astype(dtype).tobytes())

# --- Load the HDF5 ---
h5_path = sys.argv[1]    # Your NEON .h5 file
out_base = sys.argv[2]   # Output file base name (no extension)

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
print('reading....')
print('writing....')

for _line in range(radiance.shape[0]):
    lr = radiance[_line:_line+1, ...].copy().astype(np.float32)
    _write_bil_chunk(lr.transpose((0, 2, 1)), out_base, _line, radiance.shape)
    if _line % 100 == 0:
        print(f'{_line}/{radiance.shape[0]}')

print("Done writing .rad file!")
