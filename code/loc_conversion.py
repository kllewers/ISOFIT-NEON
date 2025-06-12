import numpy as np
from spectral.io import envi
from spectral.io.envi import read_envi_header
import sys

def generate_loc_from_hdr(hdr_path: str, output_path: str) -> None:
    """
    Generate a .loc file (ENVI BIL format) using map info from a .hdr file.
    
    Parameters:
        hdr_path (str): Path to the ENVI .hdr file
        output_path (str): Path prefix (no extension) for the .loc file to write
    """
    # --- Read and sanitize header values ---
    header = read_envi_header(hdr_path)
    samples = int(header['samples'])
    lines = int(header['lines'])

    # Clean and parse map info values
    map_info = header['map info']
    x_start = float(map_info[3])
    y_start = float(map_info[4])
    pixel_size_x = float(map_info[5])
    pixel_size_y = -float(map_info[6])  # negative for row progression (north to south)

    # --- Create coordinate grid ---
    x_coords = x_start + np.arange(samples, dtype=np.float32) * pixel_size_x
    y_coords = y_start + np.arange(lines, dtype=np.float32) * pixel_size_y
    xx, yy = np.meshgrid(x_coords, y_coords)

    # Stack X and Y into 2-band image (lines, samples, 2)
    loc_array = np.stack([xx, yy], axis=-1).astype(np.float32)

    # --- Write ENVI file ---
    output_meta = {
        'lines': lines,
        'samples': samples,
        'bands': 2,
        'interleave': 'bil',
        'data type': 4,  # float32
        'byte order': 0,
        'map info': map_info
    }

    envi.save_image(f"{output_path}.hdr", loc_array, dtype=np.float32, interleave='bil', force=True, metadata=output_meta)
    print(f"✅ Wrote .loc file to: {output_path}.hdr and {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python loc_conversion.py <input_hdr_path> <output_loc_basename>")
    else:
        hdr_path = sys.argv[1]
        output_path = sys.argv[2]
        generate_loc_from_hdr(hdr_path, output_path)
