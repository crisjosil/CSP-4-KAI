import os
#import leafmap.foliumap as leafmap
#import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee
##ee.Authenticate()
#ee.Initialize()

st.set_page_config(layout="wide")
st.title("Detecting temporal changes in Sentinel-2 imagery")

original_title = '<p style="color:Black; font-size: 20px;">With minor tweaks, the code used for this app was adapted from the code associated with this paper https://www.mdpi.com/2072-4292/12/22/3694.</p>'
st.markdown(original_title, unsafe_allow_html=True)
st.info("Please enable/disable different layers using the icon in the top right of the map.")

Map = geemap.Map(center=[27.029,42.788], zoom=13)
Map.add_basemap('HYBRID')

def date_advancing_later(startDate_later, delta_later, unit_later):
    dateRange = ee.DateRange(startDate_later.advance(delta_later, unit_later), startDate_later)
    return (dateRange)

def date_advancing_earlier(startDate_earlier, delta_earlier, unit_earlier):
    dateRange2 = ee.DateRange(startDate_earlier.advance(delta_earlier, unit_earlier), startDate_earlier)
    return (dateRange2)

def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return (image.updateMask(mask).divide(10000).select("B.*").copyProperties(image, ["system:time_start"]))

# // This is a script designed to automatically detect change to archaeological sites
# // It was written by Louise Rayne (louiserayne@googlemail.com)
# // It has been adapted for these tutorials by Will Deadman (william.m.deadman@gmail.com)

# // ENTER DATE HERE: Latest date to which to apply analysis.  
year_later = '2020'
month_later = '12'
day_later = '31'

#startDate_later = ee.Date.fromYMD(year_later, month_later, day_later)
startDate_later = ee.Date(year_later+'-'+month_later+'-'+day_later)

#// ENTER DATE HERE: Latest date of an earlier period you want to compare it to.
year_earlier = '2020'
month_earlier = '01'
day_earlier = '01'

#startDate_earlier = ee.Date.fromYMD(year_earlier, month_earlier, day_earlier); 
startDate_earlier = ee.Date(year_earlier+'-'+month_earlier+'-'+day_earlier)
#// parameters for date: the date advancing function generates a time range and filters data according to this range

delta_later = -3 #//-1 will count back, 1 will count forward
unit_later = 'month'

delta_earlier = -3
unit_earlier = 'month'

geometry = ee.Geometry.Polygon([[
[42.63526642133934,27.127549207129547],
[42.63526642133934,26.90773642309358],
[42.9718292697259,26.90773642309358],
[42.9718292697259,27.127549207129547],
[42.63526642133934,27.127549207129547]]])

#// imagery visualization parameters
vizParams_S2 = {
  'bands': ['B8', 'B3', 'B2'], #//edit S2 band choice here
  'min': 0,
  'max': 0.5,
  'gamma': 1.602
}


# creates the median of two periods of time

# period 1
col_earlier = (ee.ImageCollection('COPERNICUS/S2_SR')
  .filterDate(date_advancing_earlier(startDate_earlier, delta_earlier, unit_earlier))
  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)) #//you can edit this value to filter cloudy images
  .filterBounds(geometry)
  .map(maskS2clouds)
  .median()
  .clip(geometry))

 # period 2 
col_later = (ee.ImageCollection('COPERNICUS/S2_SR')
  .filterDate(date_advancing_later(startDate_later, delta_later, unit_later))
  .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)) #//you can edit this value to filter cloudy images
  .filterBounds(geometry)
  .map(maskS2clouds)
  .median()
  .clip(geometry))


Map.addLayer(col_earlier, vizParams_S2, 'S2 imagery (earlier)');  
Map.addLayer(col_later , vizParams_S2, 'S2 imagery (later)');

#// calculate the difference between earlier and later imagery composites (RMSE)
def magnitude (image):
    return (image.pow(2).reduce('sum').sqrt())

difference = magnitude(col_later.subtract(col_earlier))
Map.addLayer(difference, {min: 0, max: 0.5}, 'Imagery difference', False)

# mask areas with change greater than 0.2
differencethreshold = difference.gte(0.2); #// edit threshold value here
maskdifferencethreshold = differencethreshold.mask(differencethreshold);
Map.addLayer(maskdifferencethreshold, {'palette': 'black'}, 'Change')

in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
fc = geemap.geojson_to_ee(in_geojson)
Map.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')

Map.to_streamlit()

original_title = '<p style="color:Black; font-size: 20px;">The following code snippet shows the python lines used to obtain an image collection of Sentinel-2 imagery over the desired AOI and dates. In this case, only images where cloud coverage is lower than 10% are considered. After masking clouds, a temporal median is applied to the image collection to reduce the stack of images.</p>'
st.markdown(original_title, unsafe_allow_html=True)


code = '''col_earlier = (ee.ImageCollection('COPERNICUS/S2_SR')
  			.filterDate(date_advancing_earlier(startDate_earlier, delta_earlier, unit_earlier))
  			.filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)) #//you can edit this value to filter cloudy images
  			.filterBounds(geometry)
  			.map(maskS2clouds)
  			.median()
  			.clip(geometry))'''
st.code(code, language='python')

original_title = '<p style="color:Black; font-size: 20px;">A similar process is repeated to obtain the image collection of the second period of time. Then, the difference between the image collections is performed (RMSE) and a threshold is applied to this difference to obtain the change areas. The change areas are then displayed in black. As expected, agricultural fields dominate the changes while there seems to be changes affecting roads and the railway towards the south-east part of the area of interest (red circle).</p>'
st.markdown(original_title, unsafe_allow_html=True)

code = '''def magnitude (image):
    	      return (image.pow(2).reduce('sum').sqrt())

	  difference = magnitude(col_later.subtract(col_earlier))
	  Map.addLayer(difference, {min: 0, max: 0.5}, 'Imagery difference', False)

	  # mask areas with change greater than 0.2
	  differencethreshold = difference.gte(0.2); #// edit threshold value here
	  maskdifferencethreshold = differencethreshold.mask(differencethreshold);'''
st.code(code, language='python')
