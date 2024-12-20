import os
import click
import xarray as xr
import numpy as np
import netCDF4 as nc

from . import templates
from .util import _maybe_open
from typing import Union, Optional
from .download_era5 import download_era5_time_series
from .convert_forcing import era5_to_scm_forcing

@click.group()
def cli():
    """
    ERA5 to CCPP-SCM data processing CLI. Commands are:
     1. download_era5
     2. generate_template
     3. convert_forcings
     4. all
    """
    pass


@cli.command(name='download_era5')
@click.option('--start_date', type=str)
@click.option('--end_date', type=str)
@click.option('--lat', type=float)
@click.option('--lon', type=float)
@click.option('--output_dir', type=str)
@click.option('--name', type=str, default='era5')
def download_era5(
    start_date: str,
    end_date: str,
    lat: float,
    lon: float,
    output_dir: str,
    name: str = 'era5'
):
    """
    Download ERA5 data for a given time period and location.
    """
    download_era5_time_series(
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        lon=lon,
        output_dir=output_dir,
        name=name
    )


@cli.command(name='convert_forcings')
@click.option('-s', '--era5_surface_file', type=str)
@click.option('-p', '--era5_pressure_levels_file', type=str)
@click.option('-o', '--output_file', type=str)
def convert_forcings(
    era5_surface_file: Union[str, xr.Dataset],
    era5_pressure_levels_file: Union[str, xr.Dataset],
    output_file: Optional[str]=None,
):
    """
    Convert ERA5 data to CCPP-SCM forcing file.
    """
       
    ds1 = _maybe_open(era5_surface_file)
    ds2 = _maybe_open(era5_pressure_levels_file)
    ds = xr.merge([ds1, ds2])
    ds = ds.rename({'valid_time': 'time', 'pressure_level': 'levels',})
    out = era5_to_scm_forcing(ds)

    if output_file is not None:
        if os.path.exists(output_file):
            out.to_netcdf(output_file, "a", group="forcing", format="NETCDF4")
        else:
            out.to_netcdf(output_file, "w", group="forcing", format="NETCDF4")

    return out



@cli.command(name='convert_era5_from_template')
@click.option('-f', '--era5_processed_forcings', type=Union[str, xr.Dataset])
@click.option('-t', '--template', type=str, default='gabls3')
@click.option('-o', '--output_file', type=str)
def convert_era5_from_template(
    era5_processed_forcings: Union[str, xr.Dataset], 
    template: str, 
    output_file: str
):
    """
    Generate a template for CCPP-SCM input file.
    """
    # Open the template file and the ERA5 data
    template_file = templates.AVAILABLE_TEMPLATES[template]
    template_index = xr.open_dataset(template_file)
    template_forcing = xr.open_dataset(template_file, group='forcing')
    template_initial = xr.open_dataset(template_file, group='initial')
    template_scalars = xr.open_dataset(template_file, group='scalars')
    era5_ds = _maybe_open(era5_processed_forcings)

    # Interpolate the ERA5 data to the template levels
    # TODO: Is a linear interpolation the best way to do this?
    era5_ds = era5_ds.interp(levels=template_index.levels, method='linear')

    # Convert the timestamps to SCM format
    # And also convert the time variable in the index/root group
    dt = era5_ds.time.values[1] - era5_ds.time.values[0]
    dt = dt.astype('timedelta64[s]').astype(int)
    new_time = np.arange(0, era5_ds.time.size * dt, dt)
    era5_ds = era5_ds.assign_coords(time=new_time)
    era5_ds.time.attrs['units'] = 's'
    era5_ds.time.attrs['long_name'] = 'elapsed time since the beginning of the simulation'
    template_index = template_index.drop_vars('time').assign_coords({'time': new_time})

    # Replace the lat/lon values in the template with the ERA5 values
    template_scalars = template_scalars.assign_coords(
        latitude=era5_ds.latitude, longitude=era5_ds.longitude
    )

    # First write the root dataset
    template_index.to_netcdf(output_file, mode='w')
    
    # Then create groups and write to them
    with nc.Dataset(output_file, 'a') as root_grp:
        # Create the groups
        grp1 = root_grp.createGroup('forcing')
        grp2 = root_grp.createGroup('initial')
        grp3 = root_grp.createGroup('scalars')
        
        # Write to each group
        era5_ds.to_netcdf(output_file, group='forcing', mode='a')
        template_initial.to_netcdf(output_file, group='initial', mode='a')
        template_scalars.to_netcdf(output_file, group='scalars', mode='a')


@cli.command(name='run_full_pipeline')
@click.option('--start_date', type=str)
@click.option('--end_date', type=str)
@click.option('--lat', type=float)
@click.option('--lon', type=float)
@click.option('--output_dir', type=str)
@click.option('--name', type=str, default='era5')
@click.option('--template', type=str, default='gabls3')
@click.option('--output_file', type=str)
def run_full_pipeline(
    start_date: str,
    end_date: str,
    lat: float,
    lon: float,
    output_dir: str,
    name: str = 'era5',
    template: str = 'gabls3',
    output_file: str = 'output.nc'
):
    """
    Run the full pipeline from downloading ERA5 data to generating a CCPP-SCM input file.
    """
    download_era5_time_series(
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        lon=lon,
        output_dir=output_dir,
        name=name
    )
    era5_file = f'{output_dir}/{name}_pl.nc'
    era5_sfc_file = f'{output_dir}/{name}_sfc.nc'
    era5_processed = convert_forcings(era5_sfc_file, era5_file)
    convert_era5_from_template(era5_processed, template, output_file)



if __name__ == "__main__":
    cli()