import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee
ee.Authenticate()
ee.Initialize()
st.set_page_config(layout="wide")
st.title("Detecting power pylons from Sentinel-1 imagery")
st.subheader("SAR backscattering from sand is dominated by single bounce scattering and backscattering from power pylons is dominated by double bounce and volume scattering. We can use this knowledge and employ algorithms that highlight double bounce and volume scattering to try to identify man made structures, and in particular for this case, power pylons. The algorithm below was originally designed to identify ships in the sea where the backscattering conditions are similar to those present here (metal structure over a flat surface)")

st.info("Please note that the results of the algorithm update dynamically at different zoom levels. This due to the way that map tiles are rendered in web applications.")

Map = geemap.Map(center=[27.029,42.788], zoom=13)
Map.add_basemap('HYBRID')

ROI1= ee.Geometry.Polygon([[
[42.63526642133934,27.127549207129547],
[42.63526642133934,26.90773642309358],
[42.9718292697259,26.90773642309358],
[42.9718292697259,27.127549207129547],
[42.63526642133934,27.127549207129547]]])

start_time = '2018-01-01';
end_time   = '2020-01-01';
orbit = 43


#// This variables are to add some boxcar filter

    
#// /////////////////////////////////////////////////////
#//Function to convert from dB
def toNatural(img):
    return (ee.Image(10.0).pow(img.divide(10.0)))


#// apply the iDPolRAD
def make_iDPolRAD(image):
    #// C reate the kernels
    win_test  = 1
    win_train = 11
    boxcar_test =  ee.Kernel.square(**{'radius': win_test})
    boxcar_train = ee.Kernel.square(**{'radius': win_train})
  
    #// evaluate each components of the formula
    imageHV_test  = image.select('VH').convolve(boxcar_test);
    imageHV_train = image.select('VH').convolve(boxcar_train);
    #// var imageHH_test  = image.select('HH').convolve(boxcar_test);
    imageHH_train = image.select('VV').convolve(boxcar_train);
  
    #// calculate the iDPolRAD
    iDPolRAD = image.expression('(((hv-hv_train)/(hh_train))*hv)',{'hv': imageHV_test,'hv_train':imageHV_train,'hh_train':imageHH_train})  
    return (iDPolRAD)



#// Functions: Cropping the subsets
def subset_bounds(image):
    return (image.clip(ROI1))



#/////////////////////////////////////////////////////
#////////////////// MAIN ///////////////////////////////
#// Load Sentinel-1 GRD 

S1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterDate(start_time, end_time)
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filterBounds(ROI1)
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    #// .filter(ee.Filter.eq('relativeOrbitNumber_start', orbit_No)); 
)

#////////////////////////////////////////////////
#///// Subsetting the Analysis to the Specific area (Subset Geometry). 
collection = S1.map(subset_bounds)
#print(collection, 'Collection subset')

# Transform in linear scale
coll_lin = collection.map(toNatural)
#print(coll_lin, 'Collection linear')

# Compute the iDPolRAD
iDPolRAD = coll_lin.map(make_iDPolRAD)
#print(iDPolRAD, 'iDPolRAD');

# Make it into a list for visualisation
List_iDP = iDPolRAD.toList(iDPolRAD.size())

# get one test image
iDP_test = ee.Image(List_iDP.get(9))
#print(iDPolRAD, 'iDPolRAD_test')


# Display maps
Map.addLayer(iDP_test, {'min':0,'max':0.075}, 'Pylons in test image')
Map.to_streamlit()

st.subheader("Interestingly, we can also use this algorithm to identify offshore wind turbines as shown below for the London array")
st.markdown(""" Click and drag the mouse to nearby locations to see more turbines""")

Map = geemap.Map(center=[51.678,1.352], zoom=12)
Map.add_basemap('HYBRID')


geometry= ee.Geometry.Polygon([[[0.6489361957490125, 51.83655343394513],
           [0.6489361957490125, 51.27043400412228],
           [1.9000043109833875, 51.27043400412228],
           [1.9000043109833875, 51.83655343394513]]])

start_time = '2020-01-01';
end_time   = '2023-01-01';
orbit_No=59
S1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterDate(start_time, end_time)
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filterBounds(geometry)
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    .filter(ee.Filter.eq('relativeOrbitNumber_start', orbit_No))
    .median()
)

coll_lin  = ee.Image(10.0).pow(S1.divide(10.0)) 
win_test  = 1
win_train = 11
boxcar_test =  ee.Kernel.square(**{'radius': win_test})
boxcar_train = ee.Kernel.square(**{'radius': win_train})
  
imageHV_test  = coll_lin.select('VH').convolve(boxcar_test);
imageHV_train = coll_lin.select('VH').convolve(boxcar_train);
imageHH_train = coll_lin.select('VV').convolve(boxcar_train);
  
iDPolRAD = coll_lin.expression('(((hv-hv_train)/(hh_train))*hv)',{'hv': imageHV_test,'hv_train':imageHV_train,'hh_train':imageHH_train}) 
Map.addLayer(iDPolRAD, {'min':0,'max':0.05}, 'Offshore wind farms (London array)')
Map.to_streamlit()
