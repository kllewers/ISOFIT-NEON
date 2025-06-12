import h5py
import numpy as np
from spectral.io import envi
import sys
from typing import Optional

def convert_to_obs(h5_path: str, out_base: str, replace_fill: Optional[float] = np.nan) -> None:
    """
    Extract selected observation bands from NEON .h5 and save as ENVI BIL format.

    Parameters:
        h5_path (str): Path to the NEON HDF5 file.
        out_base (str): Output file basename (no extension).
        replace_fill (float or None): Replace -9999 with this value (e.g., np.nan or 0.0). Use None to skip.
    """
    with h5py.File(h5_path, 'r') as f:
        obs_full = f['R10C']['Radiance']['Metadata']['Ancillary_Rasters']['OBS_Data'][()]

        # Extract individual bands by index
        sensor_zenith = obs_full[:, :, 2]
        sensor_azimuth = obs_full[:, :, 1]
        solar_zenith = obs_full[:, :, 3]
        solar_azimuth = obs_full[:, :, 7]
        path_length = obs_full[:, :, 0]
        cosine_i = obs_full[:, :, 8]

        # Stack selected bands into a 6-band array
        obs_array = np.stack([
            sensor_zenith,
            sensor_azimuth,
            solar_zenith,
            solar_azimuth,
            path_length,
            cosine_i
        ], axis=-1).astype(np.float32)

    # Replace fill values (-9999)
    if replace_fill is not None:
        obs_array[obs_array == -9999] = replace_fill

    # Prepare ENVI metadata
    output_meta = {
        'lines': obs_array.shape[0],
        'samples': obs_array.shape[1],
        'bands': obs_array.shape[2],
        'interleave': 'bil',
        'data type': 4,
        'byte order': 0
    }

    # Save to .hdr and .img
    envi.save_image(out_base + '.hdr', obs_array, dtype=np.float32, interleave='bil', force=True, metadata=output_meta)
    print(f"✅ Wrote .obs file to: {out_base}.hdr and {out_base}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python obs_conversion.py <input_h5_path> <output_basename>")
    else:
        h5_path = sys.argv[1]
        out_base = sys.argv[2]
        convert_to_obs(h5_path, out_base)
