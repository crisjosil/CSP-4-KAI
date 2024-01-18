import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium
import ee
ee.Initialize()
#import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("Exploring Sentinel-2 band combinations")
original_title = '<p style="color:Black; font-size: 20px;">The following maps show different band combinations created from Sentinel-2 imagery for two dates: January and September 2020. The red circle represents a 5km radius buffer from the lat,lon point: 27.0295, 42.7890</p>'
st.markdown(original_title, unsafe_allow_html=True)

st.info("Drag the images sideways to compare how different band combinations compare to each other. You can zoom in and out to explore specific areas of interest. You can also enable/disable different layers using the icon in the top right of the map.")
center=[27.029,42.788]


image = (ee.ImageCollection('COPERNICUS/S2').filterDate('2020-01-01', '2020-02-01').map(lambda img: img.divide(10000)).median())

st.subheader("Mosaic of images acquired in January 2020")

col1, col2 = st.columns(2)
with col1:
    #st.subheader("Left: Natural Color (B4/B3/B2) / Right: Land/Water (B8/B11/B4)")
    original_title = '<p style="color:Black; font-size: 20px;">Left map: Natural Color (B4/B3/B2), 	Right map: Land/Water (B8/B11/B4)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer = geemap.ee_tile_layer(image,{'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.35, 'gamma': 1.3}, 'Natural Color (B4/B3/B2)')
    right_layer = geemap.ee_tile_layer(image,{'bands': ['B8', 'B11', 'B4'], 'min': 0, 'max': 0.6, 'gamma': 1.3},'Land/Water (B8/B11/B4)')

    Map = geemap.Map(center=center, zoom=12)
    Map.add_basemap('HYBRID')
    dataset = ee.ImageCollection('ESA/WorldCover/v100').first()
    Map.addLayer(dataset, {'bands': ['Map']},'ESA 10m Landcover 2020')
    Map.split_map(left_layer=left_layer, right_layer=right_layer)
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map.to_streamlit(width=600,height=600)

with col2:
    original_title = '<p style="color:Black; font-size: 20px;">Left map: Color Infrared (B8/B4/B3), 	Right map: Vegetation (B12/B11/B4)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer =  geemap.ee_tile_layer(image,{'bands': ['B8', 'B4', 'B3'], 'min': 0, 'max': 0.45, 'gamma': 1.3}, 'Color Infrared (B8/B4/B3)')
    right_layer = geemap.ee_tile_layer(image,{'bands': ['B12', 'B12', 'B4'], 'min': 0, 'max': 0.6, 'gamma': 1.3},'Vegetation (B12/B11/B4)')
    Map2 = geemap.Map(center=center, zoom=12)
    Map2.add_basemap('HYBRID')
    dataset = ee.ImageCollection('ESA/WorldCover/v100').first()
    Map.addLayer(dataset, {'bands': ['Map']},'ESA 10m Landcover 2020')
    Map2.split_map(left_layer=left_layer, right_layer=right_layer)
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map2.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map2.to_streamlit(width=600,height=600)

image2 = (ee.ImageCollection('COPERNICUS/S2').filterDate('2020-09-01', '2020-10-01').map(lambda img: img.divide(10000)).median())

st.subheader("Mosaic of images acquired in September 2020")

col1, col2 = st.columns(2)
with col1:
    #st.subheader("Left: Natural Color (B4/B3/B2) / Right: Land/Water (B8/B11/B4)")
    original_title = '<p style="color:Black; font-size: 20px;">Left map: Natural Color (B4/B3/B2), 	Right map: Land/Water (B8/B11/B4)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer = geemap.ee_tile_layer(image2,{'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.35, 'gamma': 1.3}, 'Natural Color (B4/B3/B2)')
    right_layer = geemap.ee_tile_layer(image2,{'bands': ['B8', 'B11', 'B4'], 'min': 0, 'max': 0.6, 'gamma': 1.3},'Land/Water (B8/B11/B4)')

    Map3 = geemap.Map(center=center, zoom=12)
    Map3.add_basemap('HYBRID')
    Map3.split_map(left_layer=left_layer, right_layer=right_layer)
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map3.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map3.to_streamlit(width=600,height=600)

with col2:
    original_title = '<p style="color:Black; font-size: 20px;">Left map: Color Infrared (B8/B4/B3), 	Right map: Vegetation (B12/B11/B4)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer =  geemap.ee_tile_layer(image2,{'bands': ['B8', 'B4', 'B3'], 'min': 0, 'max': 0.45, 'gamma': 1.3}, 'Color Infrared (B8/B4/B3)')
    right_layer = geemap.ee_tile_layer(image2,{'bands': ['B12', 'B12', 'B4'], 'min': 0, 'max': 0.6, 'gamma': 1.3},'Vegetation (B12/B11/B4)')
    Map4 = geemap.Map(center=center, zoom=12)
    Map4.add_basemap('HYBRID')
    Map4.split_map(left_layer=left_layer, right_layer=right_layer)

    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map4.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map4.to_streamlit(width=600,height=600)

st.subheader("Comparing January and September 2020")

#image_ = (ee.ImageCollection('COPERNICUS/S2').filterDate('2020-01-01', '2020-02-01').map(lambda img: img.divide(10000)).median())

col1, col2 = st.columns(2)
with col1:
    original_title = '<p style="color:Black; font-size: 20px;">Natural Color (B4/B3/B2). Left map: January 2020, Right map: September 2020</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer5 =  geemap.ee_tile_layer(image,{'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.35, 'gamma': 1.3}, 'Natural Color Jan (B4/B3/B2)')
    right_layer5 = geemap.ee_tile_layer(image2,{'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.35, 'gamma': 1.3}, 'Natural Color Sep (B4/B3/B2)')

    Map5 = geemap.Map(center=center, zoom=12)
    Map5.add_basemap('HYBRID')
    Map5.split_map(left_layer=left_layer5, right_layer=right_layer5)

    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map5.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map5.to_streamlit(width=600,height=600)

with col2:
    original_title = '<p style="color:Black; font-size: 20px;">Color Infrared (B8/B4/B3). Left map: January 2020, Right map: September 2020</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    left_layer6 =  geemap.ee_tile_layer(image, {'bands': ['B8', 'B4', 'B3'], 'min': 0, 'max': 0.45, 'gamma': 1.3}, 'Color Infrared Jan (B8/B4/B3)')
    right_layer6 = geemap.ee_tile_layer(image2,{'bands': ['B8', 'B4', 'B3'], 'min': 0, 'max': 0.45, 'gamma': 1.3}, 'Color Infrared Sep (B8/B4/B3)')
    Map6 = geemap.Map(center=center, zoom=12)
    Map6.add_basemap('HYBRID')
    Map6.split_map(left_layer=left_layer6, right_layer=right_layer6)
    
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map6.addLayer(fc.style(**{'color': 'ff0000', 'fillColor': '00000000'}), {}, 'Area of interest')
    Map6.to_streamlit(width=600,height=600)