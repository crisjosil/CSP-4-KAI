import matplotlib.pyplot as plt
import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee

# Sentinel-1

date1 = ee.Date('2015-01-01')
date2 = ee.Date('2024-01-01')
Direction = 'ASCENDING'
orbit_No = 43
Longitude = 42.788 #-4.25
Latitude = 27.029 #56.15


#AOI = ee.Geometry.Rectangle(-5,56,-2, 57) # stirlingshire
AOI = ee.Geometry.Polygon([[
[42.63526642133934,27.127549207129547],
[42.63526642133934,26.90773642309358],
[42.9718292697259,26.90773642309358],
[42.9718292697259,27.127549207129547],
[42.63526642133934,27.127549207129547]]])

sentinel1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterDate('2019-01-01', '2022-01-01')
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
        # .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
         .filter(ee.Filter.eq('orbitProperties_pass', Direction))
         .filter(ee.Filter.eq('relativeOrbitNumber_start', orbit_No))
         .filterBounds(ee.Geometry.Point(float(Longitude),float(Latitude)))
)

#sentinel1 = sentinel1.filterBounds(ee.Geometry.Point(float(Longitude),float(Latitude)))
ds1 = geemap.ee_to_xarray(sentinel1, crs='EPSG:3857',scale=10,geometry=AOI)

lat_,lon_ = 27.066248937837237, 42.777011429493655
#sample_point = ds1.VH.sel(lat=lat_, lon=lon_, method='nearest')
sample_point = ds1.VV.sel(Y=lat_, X=lon_, method='nearest')

#fig = px.line(sample_point, x=sample_point.time.values, y=sample_point.VV.values, title="Air Passenger Travel")
#st.plotly_chart(fig)

fig = plt.figure(figsize = (19, 10))
plt.scatter(sample_point.time.values, sample_point.values, color = 'k')
plt.plot(sample_point.time.values, sample_point.values, color = 'k')
plt.grid(True)
plt.xlabel('Date')
plt.ylabel('VV (dB)')
plt.title('Backscatter at lat,lon')

st.pyplot(fig)


####
# S2 
####

#Function to remove cloud and snow pixels
def maskCloudAndShadows(image):
    cloudProb = image.select('MSK_CLDPRB');
    snowProb = image.select('MSK_SNWPRB');
    cloud = cloudProb.lt(5);
    snow = snowProb.lt(5);
    scl = image.select('SCL'); 
    shadow = scl.eq(3) # // 3 = cloud shadow
    cirrus = scl.eq(10) # // 10 = cirrus
    #Cloud probability less than 5% or cloud shadow classification
    mask = (cloud.And(snow)).And(cirrus.neq(1)).And(shadow.neq(1));
    return (image.updateMask(mask))


# Adding a NDVI band
def addNDVI(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return (image.addBands([ndvi]))

# Adding a modified sand index
def addSand(image): 
    sand = image.normalizedDifference(['B4', 'B2']).rename('sand_index')
    return (image.addBands([sand]))

# Adding NDWI index
def addNDWI(image):
    mndwi = image.normalizedDifference(['B3', 'B11']).rename(['mndwi']);
    return (image.addBands([mndwi]))

startDate = '2018-01-01'
endDate = '2021-12-31'
# Use Sentinel-2 L2A data - which has better cloud masking

#//var point = ee.Geometry.Point([42.8284913628064, 27.006930467249838]);


S2_collection = (ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(startDate, endDate)
    .map(maskCloudAndShadows)
    .map(addNDVI)
    #.map(addSand)
    #.map(addNDWI)
    .filter(ee.Filter.bounds(AOI))
)

ds2 = geemap.ee_to_xarray(S2_collection, crs='EPSG:3857',scale=10,geometry=AOI)

lat_,lon_ = 27.066248937837237, 42.777011429493655

sample_point = ds2.ndvi.sel(Y=lat_, X=lon_, method='nearest')

fig = plt.figure(figsize = (19, 10))
plt.scatter(sample_point.time.values, sample_point.values, color = 'k')
plt.plot(sample_point.time.values, sample_point.values, color = 'k')
plt.grid(True)
plt.xlabel('Date')
plt.ylabel('VV (dB)')
plt.title('Backscatter at lat,lon')

st.pyplot(fig)
