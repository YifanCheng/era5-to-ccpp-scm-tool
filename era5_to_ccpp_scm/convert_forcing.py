import numpy as np
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units


def calculate_radiative_heating(swnet_top, swdn_sfc, lwnet_top, lwdn_sfc, 
                              pressure, temperature):
    """
    Calculate radiative heating rate profile.

    Parameters:
    -----------
    swnet_top : array-like, shape (time, )
        Net shortwave radiation at the top of the atmosphere
    swdn_sfc : array-like, shape (time, )
        Downward shortwave radiation at the surface
    lwnet_top : array-like, shape (time, )
        Net longwave radiation at the top of the atmosphere
    lwdn_sfc : array-like, shape (time, )
        Downward longwave radiation at the surface
    pressure : array-like, shape (levels, )
        Pressure levels in Pa
    temperature : array-like, shape (time, levels)
        Temperature at the center point in K
    """
    # Calculate the radiative heating rate
    dT_dt_rad = np.zeros((swnet_top.shape[0], pressure.shape[0]))
    for t in range(swnet_top.shape[0]):
        # Calculate the radiative heating rate
        dT_dt_rad[t, :] = (swnet_top[t] - swdn_sfc[t] + lwnet_top[t] - lwdn_sfc[t]) / (pressure * temperature[t, :])
    return dT_dt_rad


def calculate_grid_spacing(lats, lons, center_idx=1):
    """
    Calculate grid spacing in meters, accounting for latitude.
    
    Parameters:
    -----------
    lats : array-like, shape (3,)
        Latitude values for 3 grid points
    lons : array-like, shape (3,)
        Longitude values for 3 grid points
    center_idx : int
        Index of the center point (default=1)
        
    Returns:
    --------
    dx : float
        Grid spacing in x-direction (meters) at center latitude
    dy : float
        Grid spacing in y-direction (meters)
    """
    # Earth's radius in meters
    R_EARTH = 6371000
    
    # Center latitude for dx calculation
    center_lat = lats[center_idx]
    
    # Convert to radians
    lat_rad = np.deg2rad(center_lat)
    
    # Calculate dy (latitude spacing)
    # For 1-degree latitude difference
    dy = R_EARTH * np.deg2rad(np.abs(lats[2] - lats[0])) / 2
    
    # Calculate dx (longitude spacing)
    # dx varies with latitude due to convergence of meridians
    # For 1-degree longitude difference at the center latitude
    dx = R_EARTH * np.cos(lat_rad) * np.deg2rad(np.abs(lons[2] - lons[0])) / 2
    
    return dx, dy


def calculate_horizontal_gradients(var, lats, lons, center_idx=1):
    """
    Calculate horizontal gradients using centered differences accounting for latitude.
    
    Parameters:
    -----------
    var : array-like, shape (time, level, 3, 3)
        Variable on 3x3 grid centered on column of interest
    lats : array-like, shape (3,)
        Latitude values for 3 grid points
    lons : array-like, shape (3,)
        Longitude values for 3 grid points
    center_idx : int
        Index of the center point (default=1)
        
    Returns:
    --------
    d_dx : array-like, shape (time, level)
        Zonal gradient at center point
    d_dy : array-like, shape (time, level)
        Meridional gradient at center point
    """
    # Get proper grid spacing at center latitude
    dx, dy = calculate_grid_spacing(lats, lons, center_idx)
    
    # Calculate centered differences at the middle point
    d_dx = (var.isel(latitude=1, longitude=2) - var.isel(latitude=1, longitude=0)) / (2 * dx)
    d_dy = (var.isel(latitude=2, longitude=1) - var.isel(latitude=0, longitude=1)) / (2 * dy)
    
    return d_dx, d_dy


def calculate_geostrophic_wind(z, lat, lon):
    """
    Calculate geostrophic wind components from geopotential height.
    
    Parameters:
    -----------
    z : array-like, shape (time, level, 3, 3)
        Geopotential height on 3x3 grid
    lat : array-like, shape (3, 3)
        Latitudes of grid points
    lon : array-like, shape (3, 3)
        Longitudes of grid points
    
    Returns:
    --------
    u_g : array-like, shape (time, level)
        Zonal geostrophic wind at center point
    v_g : array-like, shape (time, level)
        Meridional geostrophic wind at center point
    """
    # Coriolis parameter at center point
    f = 2 * 7.2921e-5 * np.sin(np.deg2rad(lat[1]))
    
    # Calculate height gradients with proper spacing
    dz_dx, dz_dy = calculate_horizontal_gradients(z, lat, lon)
    
    # Calculate geostrophic wind components
    u_g = -(1/f) * 9.81 * dz_dy
    v_g = (1/f) * 9.81 * dz_dx
    
    return u_g, v_g


def theta_from_t(temperature, pressure):
    """Convert temperature to potential temperature."""
    return mpcalc.potential_temperature(
        pressure * units.Pa, 
        temperature * units.kelvin
    )


def rho_from_sp(sp, t):
    """Calculate air density from surface pressure and temperature."""
    return sp / (287.05 * t)


def calculate_advection(var, u, v, w, lats, lons, pressure, temperature, center_idx=1):
    """
    Calculate advection terms using 3x3 grid with proper grid spacing.
    
    Parameters:
    -----------
    var : array-like, shape (time, level, 3, 3)
        Variable to calculate advection for
    u : array-like, shape (time, level)
        Zonal wind at center point
    v : array-like, shape (time, level)
        Meridional wind at center point
    w : array-like, shape (time, level)
        Vertical velocity at center point
    lats : array-like, shape (3,)
        Latitude values for 3 grid points
    lons : array-like, shape (3,)
        Longitude values for 3 grid points
    pressure : array-like, shape (level,)
        Pressure levels in Pa
    temperature : array-like, shape (time, level)
        Temperature at center point in K
    center_idx : int
        Index of the center point (default=1)
    """
    # Calculate horizontal gradients with proper spacing
    dvardx, dvardy = calculate_horizontal_gradients(var, lats, lons, center_idx)
    
    # Calculate heights for vertical gradient
    pressure_hpa = pressure * units.Pa / 100
    temperature = temperature * units.kelvin
    
    heights = np.zeros((var.shape[0], var.shape[1]))
    for t in range(var.shape[0]):
        heights[t, :] = mpcalc.pressure_to_height_std(pressure_hpa)
    
    # Calculate vertical gradient (at center point)
    dvardz = xr.DataArray(np.zeros((var.shape[0], var.shape[1])), dims=('time', 'levels'))
    for t in range(var.shape[0]):
        dvardz[t, :] = np.gradient(var[t, :, center_idx, center_idx], heights[t, :])
    
    # Calculate advection terms
    h_advec = -(u * dvardx + v * dvardy)
    v_advec = -w * dvardz
    
    return h_advec, v_advec


def era5_to_scm_forcing(ds):
    # Create output dataset
    out = xr.Dataset()
    pressure_levels = ds.levels * 100  # convert hPa to Pa
    out.coords['levels'] = pressure_levels

    u_g, v_g = calculate_geostrophic_wind(ds.z, ds.latitude, ds.longitude)

    h_advec_theta, v_advec_theta = calculate_advection(
        theta_from_t(ds.t, pressure_levels).transpose('time', 'levels', 'latitude', 'longitude'),
        ds.u.values[..., 1, 1],  # center point
        ds.v.values[..., 1, 1],
        ds.w.values[..., 1, 1],
        ds['latitude'].values,
        ds['longitude'].values,
        ds.levels.values * 100,
        ds.t.values[..., 1, 1]
    )

    h_advec_qt, v_advec_qt = calculate_advection(
        ds.q,
        ds.u.isel(latitude=1, longitude=1).values,
        ds.v.isel(latitude=1, longitude=1).values,
        ds.w.values[..., 1, 1],
        ds['latitude'].values,
        ds['longitude'].values,
        ds.levels.values * 100,
        ds.t.isel(latitude=1, longitude=1).values
    )

    # Convert omega to w
    rho = ds.sp / (287.0 * ds.t)  # approximate air density
    w = -ds.w / (rho * 9.81)
    out['w_ls'] = w.isel(latitude=1, longitude=1)
    out['omega'] = ds.w.isel(latitude=1, longitude=1)

    # Nudging fields
    out['u_nudge'] = ds.u.isel(latitude=1, longitude=1)
    out['v_nudge'] = ds.v.isel(latitude=1, longitude=1)
    out['T_nudge'] = ds.t.isel(latitude=1, longitude=1)
    out['thil_nudge'] = (('time', 'levels'), 
                         theta_from_t(ds.t.isel(latitude=1, longitude=1), pressure_levels).values.T)
    out['qt_nudge'] = ds.q.isel(latitude=1, longitude=1)

    out['u_g'] = u_g
    out['v_g'] = v_g
    out['h_advec_thetail'] = h_advec_theta
    out['v_advec_thetail'] = v_advec_theta
    out['h_advec_qt'] = h_advec_theta
    out['v_advec_qt'] = v_advec_theta
    out['p_surf'] = ds.sp.isel(latitude=1, longitude=1)
    out['T_surf'] = ds.t2m.isel(latitude=1, longitude=1)
    
    # Calculate radiative heating rate
    swnet_top = ds.tsr.isel(latitude=1, longitude=1).values
    # Possibly below should be `ds.ssrd`
    swdn_sfc = ds.ssr.isel(latitude=1, longitude=1).values
    lwnet_top = ds.ttr.isel(latitude=1, longitude=1).values
    # Possibly below should be `ds.strd`
    lwdn_sfc = ds.str.isel(latitude=1, longitude=1).values
    
    # Reshape pressure levels to match the time dimension
    pressure_2d = np.tile(pressure_levels.values, (swnet_top.shape[0], 1))
    print(pressure_2d.shape)
    temperature = ds.t.isel(latitude=1, longitude=1).values
    
    # Calculate radiative heating rate
    dT_dt_rad = calculate_radiative_heating(
        swnet_top, swdn_sfc, lwnet_top, lwdn_sfc, 
        pressure_levels, temperature
    )
    print("dT_dt_rad shape:", dT_dt_rad.shape)
    
    # Add to output dataset
    out['dT_dt_rad'] = (('time', 'levels'), dT_dt_rad)

    # Add variable attributes
    var_attrs = {
        'p_surf': {'units': 'Pa', 'long_name': 'surface pressure'},
        'T_surf': {'units': 'K', 'long_name': 'surface absolute temperature'},
        'w_ls': {'units': 'm s^-1', 'long_name': 'large scale vertical velocity'},
        'omega': {'units': 'Pa s^-1', 'long_name': 'large scale pressure vertical velocity'},
        'u_g': {'units': 'm s^-1', 'long_name': 'large scale geostrophic E-W wind'},
        'v_g': {'units': 'm s^-1', 'long_name': 'large scale geostrophic N-S wind'},
        'u_nudge': {'units': 'm s^-1', 'long_name': 'E-W wind to nudge toward'},
        'v_nudge': {'units': 'm s^-1', 'long_name': 'N-S wind to nudge toward'},
        'T_nudge': {'units': 'K', 'long_name': 'absolute temperature to nudge toward'},
        'thil_nudge': {'units': 'K', 'long_name': 'potential temperature to nudge toward'},
        'qt_nudge': {'units': 'kg kg^-1', 'long_name': 'q_t to nudge toward'},
        'dT_dt_rad': {'units': 'K s^-1', 'long_name': 'prescribed radiative heating rate'},
        'h_advec_thetail': {'units': 'K s^-1', 'long_name': 'prescribed theta_il tendency due to horizontal advection'},
        'v_advec_thetail': {'units': 'K s^-1', 'long_name': 'prescribed theta_il tendency due to vertical advection'},
        'h_advec_qt': {'units': 'kg kg^-1 s^-1', 'long_name': 'prescribed q_t tendency due to horizontal advection'},
        'v_advec_qt': {'units': 'kg kg^-1 s^-1', 'long_name': 'prescribed q_t tendency due to vertical advection'}
    }
    
    for var in out.variables:
        if var in var_attrs:
            out[var].attrs = var_attrs[var]
 
    return out.transpose('levels', 'time')
