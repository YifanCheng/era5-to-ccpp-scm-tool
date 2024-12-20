import time
import cdsapi
import datetime as dt


def download_era5_time_series(start_date, end_date, lat, lon, output_dir, name='era5'):
    """
    Download ERA5 data for a time period.
    
    Parameters:
        start_date (datetime): Start date
        end_date (datetime): End date
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        output_prefix (str): Prefix for output filenames
    """
    # Format dates for CDS API
    date_range = start_date + "/" + end_date
    
    # Ensure longitude is in 0-360 format
    if lon < 0:
        lon = lon + 360
        
    # Area definition (3x3 grid centered at lat, lon)
    area = [lat + 0.25, lon - 0.25, lat - 0.25, lon + 0.25]
    
    # Pressure levels
    pressure_levels = [
        '1', '2', '3', '5', '7', '10', '20', '30', '50', '70',
        '100', '125', '150', '175', '200', '225', '250', '300',
        '350', '400', '450', '500', '550', '600', '650', '700',
        '750', '775', '800', '825', '850', '875', '900', '925',
        '950', '975', '1000'
    ]
    
    c = cdsapi.Client()
    
    # Download pressure level data
    print("Downloading pressure level time series...")
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [
                'geopotential',
                'specific_humidity',
                'temperature',
                'u_component_of_wind',
                'v_component_of_wind',
                'vertical_velocity',
            ],
            'pressure_level': pressure_levels,
            'date': date_range,
            'time': [f"{h:02d}:00" for h in range(0, 24)],
            'area': area,
        },
        f'{output_dir}/{name}_pl.nc'
    )
    # Sleep for 5 seconds to ensure things wrap up cleanly
    time.sleep(1)
    
    # Download surface data
    print("Downloading surface data time series...")
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [
                'surface_pressure',
                'skin_temperature',
                'top_net_solar_radiation',
                'surface_net_solar_radiation',
                'top_net_thermal_radiation',
                'surface_net_thermal_radiation',
                '2m_temperature',
                '10m_u_component_of_wind',
                '10m_v_component_of_wind',
                'surface_solar_radiation_downwards',
                'surface_thermal_radiation_downwards',
            ],
            'date': date_range,
            'time': [f"{h:02d}:00" for h in range(0, 24)],
            'area': area,
        },
        f'{output_dir}/{name}_sfc.nc'
    )
    # Sleep for 5 seconds to ensure things wrap up cleanly
    time.sleep(5)
    

if __name__ == "__main__":
    # Example usage for time series
    start = dt.datetime(2024, 1, 1)
    end = dt.datetime(2024, 1, 2)
    download_era5_time_series(
        start_date=start,
        end_date=end,
        lat=40.0,
        lon=-105.0,
        output_prefix="era5_timeseries"
    )