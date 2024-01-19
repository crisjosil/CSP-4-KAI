import os
#import leafmap.foliumap as leafmap
#import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee
#ee.Authenticate()
#ee.Initialize()

#// ------- Add ratio
def addLogRatio(img):
    logVV = img.select('VV')
    logVH = img.select('VH')
    logratio = logVH.subtract(logVV).rename('VV/VH')
    #logratio_float = logratio.toFloat()
    return (img.addBands(logratio))


st.set_page_config(layout="wide")
st.title("Sentinel-1 multitemporal metrics")
original_title = '<p style="color:Black; font-size: 20px;">A single SAR image may look noisy. However, multitemporal indices can be highly informative. The following maps show the median and standard deviation of a stack of images collected in 2020.</p>'
st.markdown(original_title, unsafe_allow_html=True)
st.info("Please enable/disable different layers using the icon in the top right of the map.")

Map = geemap.Map(center=[27.029,42.788], zoom=13)
Map.add_basemap('HYBRID')
dataset = ee.ImageCollection('ESA/WorldCover/v100').first()
Map.addLayer(dataset, {'bands': ['Map']},'ESA 10m Landcover 2020')


date1, date2 = '2020-01-01','2020-12-31'
Direction = 'ASCENDING'
#orbit_No = 43

geometry = ee.Geometry.Polygon([[
[42.63526642133934,27.127549207129547],
[42.63526642133934,26.90773642309358],
[42.9718292697259,26.90773642309358],
[42.9718292697259,27.127549207129547],
[42.63526642133934,27.127549207129547]]])

s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterDate(date1, date2)
            #.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
            #.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.eq('orbitProperties_pass', Direction))
            #.filter(ee.Filter.eq('relativeOrbitNumber_start', orbit_No))
            .filterBounds(geometry)
            #.median()
)

# add ratio to the collection
sentinel1 = s1.map(addLogRatio)

VH_median = sentinel1.select('VH').median()
VV_median = sentinel1.select('VV').median()
ratio_median = sentinel1.select(['VV/VH']).median()

Map.addLayer(VV_median,{'min': -30, 'max':0}, 'VV multitemporal median')
Map.addLayer(VH_median,{'min': -35, 'max':-10}, 'VH multitemporal median',False)

rgb_vis = {'min': -30, 'max':-10, 'bands': ['VV', 'VH', 'VV/VH']};
Map.addLayer(sentinel1.median(), rgb_vis, 'RGB - median reducer',False);


VV_std =  sentinel1.select('VV').reduce(ee.Reducer.stdDev())
VH_std =  sentinel1.select('VH').reduce(ee.Reducer.stdDev())
Map.addLayer(VV_std,{'min': 0, 'max':10},'VV_std',False)
Map.addLayer(VH_std,{'min': 0, 'max':10},'VH_std',False)


in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
fc = geemap.geojson_to_ee(in_geojson)
Map.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')

Map.to_streamlit()

original_title = '<p style="color:Black; font-size: 20px;">As you will see in the next tab "Power pylons and wind farms", the information presented above can be used to detect man made structures surrounded by flat surfaces.</p>'
st.markdown(original_title, unsafe_allow_html=True)
