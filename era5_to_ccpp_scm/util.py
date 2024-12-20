import xarray as xr

def _maybe_open(f):
    if isinstance(f, str):
        return xr.open_dataset(f)
    elif isinstance(f, xr.Dataset):
        return f
    else:
        raise ValueError("Invalid type for input file")
 