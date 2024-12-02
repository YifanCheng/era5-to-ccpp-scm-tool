# Command line tool for converting ERA5 data to CCPP-SCM input

## Installation

TODO: Describe the installation process

## Usage

## CCPP-SCM input data

### Overall structure
The CCPP-SCM input data is organized in a single netcdf file with multiple groups.
The group names are `forcing`, `initial`, and `scalars`, with a root group that I call `index`.

### Index data

- `soil_depth ('nsoil', )`: Depth of bottom of soil layers (m)

### Forcing data

- `p_surf ('time',)` :  surface pressure ( Pa )
- `T_surf ('time',)` :  surface absolute temperature ( K )
- `w_ls ('levels', 'time')` :  large scale vertical velocity ( m s^-1 )
- `omega ('levels', 'time')` :  large scale pressure vertical velocity ( Pa s^-1 )
- `u_g ('levels', 'time')` :  large scale geostrophic E-W wind ( m s^-1 )
- `v_g ('levels', 'time')` :  large scale geostrophic N-S wind ( - )
- `u_nudge ('levels', 'time')` :  E-W wind to nudge toward ( m s^-1 )
- `v_nudge ('levels', 'time')` :  N-S wind to nudge toward ( m s^-1 )
- `T_nudge ('levels', 'time')` :  absolute temperature to nudge toward ( K )
- `thil_nudge ('levels', 'time')` :  potential temperature to nudge toward ( K )
- `qt_nudge ('levels', 'time')` :  q_t to nudge toward ( kg kg^-1 )
- `dT_dt_rad ('levels', 'time')` :  prescribed radiative heating rate ( K s^-1 )
- `h_advec_thetail ('levels', 'time')` :  prescribed theta_il tendency due to horizontal advection ( K s^-1 )
- `v_advec_thetail ('levels', 'time')` :  prescribed theta_il tendency due to vertical advection ( K s^-1 )
- `h_advec_qt ('levels', 'time')` :  prescribed q_t tendency due to horizontal advection ( kg kg^-1 s^-1 )
- `v_advec_qt ('levels', 'time')` :  prescribe q_t tendency due to vertical advection ( kg kg^-1 s^-1 )

### Initial condition data

- ` height ('levels',) `:  physical height at pressure levels ( m )
- ` thetail ('levels',) `:  initial profile of ice-liquid water potential temperature ( K )
- ` qt ('levels',) `:  initial profile of total water specific humidity ( kg kg^-1 )
- ` ql ('levels',) `:  initial profile of liquid water specific humidity ( kg kg^-1 )
- ` qi ('levels',) `:  initial profile of ice water specific humidity ( kg kg^-1 )
- ` u ('levels',) `:  initial profile of E-W horizontal wind ( m s^-1 )
- ` v ('levels',) `:  initial profile of N-S horizontal wind ( m s^-1 )
- ` tke ('levels',) `:  initial profile of turbulence kinetic energy ( m^2 s^-2 )
- ` ozone ('levels',) `:  initial profile of ozone mass mixing ratio ( kg kg^-1 )
- ` stc ('nsoil',) `:  initial profile of soil temperature ( K )
- ` smc ('nsoil',) `:  initial profile of soil moisture ( m3 m-3 )
- ` slc ('nsoil',) `:  initial profile of soil liquid moisture ( m3 m-3 )

### Scalars 

- ` alvsf () `:  60 degree vis albedo with strong cosz dependency ( - )
- ` alnsf () `:  60 degree nir albedo with strong cosz dependency ( - )
- ` alvwf () `:  60 degree vis albedo with weak cosz dependency ( - )
- ` alnwf () `:  60 degree nir albedo with weak cosz dependency ( - )
- ` facsf () `:  fractional coverage with strong cosz dependency ( - )
- ` facwf () `:  fractional coverage with weak cosz dependency ( - )
- ` vegfrac () `:  vegetation fraction ( - )
- ` canopy () `:  amount of water stored in canopy ( kg m-2 )
- ` f10m () `:  ratio of sigma level 1 wind and 10m wind ( - )
- ` t2m () `:  2-meter absolute temperature ( K )
- ` q2m () `:  2-meter specific humidity ( kg kg-1 )
- ` vegtyp () `:  vegetation type (1-12) ( - )
- ` soiltyp () `:  soil type (1-12) ( - )
- ` uustar () `:  friction velocity ( m s-1 )
- ` ffmm () `:  Monin-Obukhov similarity function for momentum ( - )
- ` ffhh () `:  Monin-Obukhov similarity function for heat ( - )
- ` hice () `:  sea ice thickness ( m )
- ` fice () `:  ice fraction ( - )
- ` tisfc () `:  ice surface temperature ( K )
- ` tprcp () `:  instantaneous total precipitation amount ( m )
- ` srflag () `:  snow/rain flag for precipitation ( - )
- ` snwdph () `:  water equivalent snow depth ( mm )
- ` shdmin () `:  minimum vegetation fraction ( - )
- ` shdmax () `:  maximum vegetation fraction ( - )
- ` slopetyp () `:  slope type (1-9) ( - )
- ` snoalb () `:  maximum snow albedo ( - )
- ` sncovr () `:  snow area fraction ( - )
- ` tsfcl () `:  surface skin temperature over land ( K )
- ` zorll () `:  surface roughness length over land ( cm )
- ` zorli () `:  surface roughness length over ice ( cm )