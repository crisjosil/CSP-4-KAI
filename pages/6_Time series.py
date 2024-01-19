import matplotlib.pyplot as plt
import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee
import json
from datetime import datetime
import numpy as np
import pandas as pd


def simplify(fc):
    """Take a feature collection, as returned by mapping a reducer to a ImageCollection,
        and reshape it into a simpler list of dictionaries
    Args:
        fc (dict): Dictionary representation of a feature collection, as returned
            by mapping a reducer to an ImageCollection
    Returns:
        list: A list of dictionaries.
    Examples:
        >>> fc = {u'columns': {},
        ...       u'features': [{u'geometry': None,
        ...                      u'id': u'LC81970292013106',
        ...                      u'properties': {u'B1': 651.8054424353023,
        ...                                      u'B2': 676.6018246419446},
        ...                      u'type': u'Feature'},
        ...                     {u'geometry': None,
        ...                      u'id': u'LC81970292013122',
        ...                      u'properties': {u'B1': 176.99323997958842,
        ...                                      u'B2': 235.83196553144882},
        ...                      u'type': u'Feature'}]}
        >>> simplify(fc)
    """
    def feature2dict(f):
        id = f['id']
        out = f['properties']
        out.update(id=id)
        return out
    out = [feature2dict(x) for x in fc['features']]
    return out

def Time_series_of_a_region(Img_collection,geometry,stats,title,automatic_ax_lim):
    if stats == 'mean':
        fun = ee.Reducer.mean()
    elif stats == 'median':
        fun = ee.Reducer.median()
    elif stats == 'max':
        fun = ee.Reducer.max()
    elif stats == 'min':
        fun = ee.Reducer.min()
    elif stats == 'minMax':
        fun = ee.Reducer.minMax()
    else:
        raise ValueError('Unknown spatial aggregation function. Must be one of mean, median, max, or min')

    def _reduce_region(image):
                    """Spatial aggregation function for a single image and a polygon feature"""
                    #the reduction is specified by providing the reducer (ee.Reducer.mean()), the geometry  (a polygon coord), at the scale (30 meters)
                    stat_dict = image.reduceRegion(fun, geometry, 30);
                    # FEature needs to be rebuilt because the backend doesn't accept to map
                    # functions that return dictionaries
                    return ee.Feature(None, stat_dict)
    fc = Img_collection.filterBounds(geometry).map(_reduce_region).getInfo()
    out = simplify(fc)
    return(out)

st.set_page_config(layout="wide")
st.title("Time series of an area of interest")

st.markdown(
    """
    This page shows a time series of Sentinel-1 imagery for a specific location. It will eventually be a dynamic dashboard which allows a user to define an AOI and a satellite, and retrieve the time series from the Earth engine.

    """
)

st.info("Development of this page is in progress")

Map = geemap.Map(center=[27.029,42.788], zoom=13)
Map.add_basemap('HYBRID')

fc = geemap.geojson_to_ee('https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson')
Map.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')

in_geojson = "https://github.com/crisjosil/CSP-4-KAI/blob/master/Ag_AOI.geojson"
#"https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/france.geojson"
fc1 = geemap.geojson_to_ee(in_geojson)
Map.addLayer(fc1.style(**{'color': 'ff1111', 'fillColor': '00000000'}), {}, 'Agricultural area')

Map.to_streamlit()


# Sentinel-1
date_a = '2019-01-01'
date_b = '2024-01-01'
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
            .filterDate(date_a, date_b)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
        # .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
         .filter(ee.Filter.eq('orbitProperties_pass', Direction))
         .filter(ee.Filter.eq('relativeOrbitNumber_start', orbit_No))
         .filterBounds(ee.Geometry.Point(float(Longitude),float(Latitude)))
)

stats = 'mean'    #   median, max, min, minMax
title= ""
#gdf = gpd.read_file('/media/Scratch/Cristian/Tests/CSP-4-KAI/pages/Ag_AOI.geojson')
#gdf = gpd.read_file(in_geojson, driver='GeoJSON')
#geom=json.loads(gdf.to_json())['features'][0]['geometry']['coordinates']
#geometry=ee.Geometry.Polygon(geom)
out=Time_series_of_a_region(sentinel1,fc1,stats,title,automatic_ax_lim="Yes")


arr=np.zeros(len(out)).tolist()
Dates=np.zeros(len(out)).tolist()
df_=pd.DataFrame()
for i in range(len(out)):
    a=out[i]['id'].split('_')[4].split('T')[0]
    Dates[i]=datetime.strptime(a, "%Y%m%d")
    arr[i]=out[i]['VV']

df_['Dates']=Dates
df_['VV']=arr

# ####
# # S2 
# ####

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


# Use Sentinel-2 L2A data - which has better cloud masking
S2_collection = (ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(date_a, date_b)
    .map(maskCloudAndShadows)
    .map(addNDVI)
    #.map(addSand)
    #.map(addNDWI)
    .filter(ee.Filter.bounds(AOI))
)

out=Time_series_of_a_region(S2_collection,fc1,stats,title,automatic_ax_lim="Yes")
#print(out[i])

arr=np.zeros(len(out)).tolist()
Dates=np.zeros(len(out)).tolist()
df_1=pd.DataFrame()
for i in range(len(out)):
    a=out[i]['id'].split('_')[0].split('T')[0]
    Dates[i]=datetime.strptime(a, "%Y%m%d")
    arr[i]=out[i]['ndvi']

df_1['Dates']=Dates
df_1['NDVI']=arr

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    original_title = '<p style="color:Black; font-size: 20px;">Agricultural area: Sentinel-1 VV Backscatter</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    fig = plt.figure(figsize = (19, 10))
    plt.scatter(df_.Dates, df_.VV, color = 'k')
    plt.plot(df_.Dates, df_.VV, color = 'k')
    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('VV (dB)')
    plt.title('Sentinel-1 VV Backscatter')
    st.pyplot(fig)

with row1_col2:
    original_title = '<p style="color:Black; font-size: 20px;">Agricultural area: Sentinel-2 NDVI</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    fig = plt.figure(figsize = (19, 10))
    plt.scatter(df_1.Dates, df_1.NDVI, color = 'k')
    plt.plot(df_1.Dates, df_1.NDVI, color = 'k')
    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('NDVI')
    plt.title('Sentinel-2 NDVI')
    st.pyplot(fig)

# # ds2 = geemap.ee_to_xarray(S2_collection, crs='EPSG:3857',scale=10,geometry=AOI)

# # lat_,lon_ = 27.066248937837237, 42.777011429493655

# # sample_point = ds2.ndvi.sel(Y=lat_, X=lon_, method='nearest')

# # fig = plt.figure(figsize = (19, 10))
# # plt.scatter(sample_point.time.values, sample_point.values, color = 'k')
# # plt.plot(sample_point.time.values, sample_point.values, color = 'k')
# # plt.grid(True)
# # plt.xlabel('Date')
# # plt.ylabel('VV (dB)')
# # plt.title('Backscatter at lat,lon')

# # st.pyplot(fig)
