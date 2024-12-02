import os
import click
import xarray as xr

from download_era5 import download_era5_time_series
from convert_forcing import era5_to_scm_forcing

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


@cli.command(name='generate_template')
def generate_template():
    """
    Generate a template for CCPP-SCM input file.
    """
    pass


@cli.command(name='convert_forcings')
@click.option('-s', '--era5_surface_file', type=str)
@click.option('-p', '--era5_pressure_levels_file', type=str)
@click.option('-o', '--output_file', type=str)
def convert_forcings(
    era5_surface_file: str,
    era5_pressure_levels_file: str,
    output_file: str,
):
    """
    Convert ERA5 data to CCPP-SCM forcing file.
    """
    ds1 = xr.open_dataset(era5_surface_file)
    ds2 = xr.open_dataset(era5_pressure_levels_file)
    ds = xr.merge([ds1, ds2])
    ds = ds.rename({'valid_time': 'time', 'pressure_level': 'levels',})
    out = era5_to_scm_forcing(ds)

    if os.path.exists(output_file):
        out.to_netcdf(output_file, "a", group="forcing", format="NETCDF4")
    else:
        out.to_netcdf(output_file, "w", group="forcing", format="NETCDF4")
    return out


if __name__ == "__main__":
    cli()