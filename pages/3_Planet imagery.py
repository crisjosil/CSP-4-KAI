import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import geemap.foliumap as geemap
import folium

st.set_page_config(layout="wide")
st.title("Visualising cloud optimised Geotiff (COG) Planet imagery")

st.markdown(
    """
    This page loads COG planet imagery stored in a google cloud bucket. The dates cover from January to December 2020. The bands used are described in the following link (4-band product): https://developers.planet.com/docs/apis/data/sensors/

    """
)

st.info("Loading the files may take a minute. Please enable/disable different dates using the icon in the top right of the map.")

urla = 'https://storage.googleapis.com/cogs-2024/KAI-9Jan2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlb = 'https://storage.googleapis.com/cogs-2024/KAI-14Feb2020_psscene_analytic_sr_udm2/composite.tif'
urlc = 'https://storage.googleapis.com/cogs-2024/KAI-18Mar2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlda = 'https://storage.googleapis.com/cogs-2024/KAI-9Apr2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urldb = 'https://storage.googleapis.com/cogs-2024/KAI-13Apr2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urle = 'https://storage.googleapis.com/cogs-2024/KAI-3May2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlf = 'https://storage.googleapis.com/cogs-2024/KAI-7Jun2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlg = 'https://storage.googleapis.com/cogs-2024/KAI-30Jun2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlh = 'https://storage.googleapis.com/cogs-2024/KAI-2Jul2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urli = 'https://storage.googleapis.com/cogs-2024/KAI-23Aug2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlj = 'https://storage.googleapis.com/cogs-2024/KAI-30Aug2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlk = 'https://storage.googleapis.com/cogs-2024/KAI-25Oct2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urll = 'https://storage.googleapis.com/cogs-2024/KAI-25Nov2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urlm = 'https://storage.googleapis.com/cogs-2024/KAI-6Dec2020_psscene_analytic_sr_udm2/composite_file_format.tif'
urln = 'https://storage.googleapis.com/cogs-2024/KAI-16Dec2020_psscene_analytic_sr_udm2/composite_file_format.tif'

leafmap.cog_bounds(urla)
leafmap.cog_center(urla)
leafmap.cog_bands(urla)

col1, col2 = st.columns(2)
with col1:
    original_title = '<p style="color:Black; font-size: 20px;">Natural Color (B3-R/B2-G/B1-B)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    Map = leafmap.Map()
    Map.add_basemap('HYBRID')
    Map.add_cog_layer(urla,bidx=[3, 2, 1], rescale=["0,3000","0,3000","0,3000"],name ='09-Jan-2020') # R,G,B
    Map.add_cog_layer(urlb,bidx=[3, 2, 1], rescale=["0,3000","0,3000","0,3000"],name ='14-Feb-2020') # -  The False color infrared composite  It is most commonly used to assess plant density and healht
    Map.add_cog_layer(urlc,bidx=[3, 2, 1], rescale=["0,3000","0,3000","0,3000"],name ='18-Mar-2020')    
    Map.add_cog_layer(urld,bidx=[3, 2, 1], rescale=["0,3000","0,3000","0,3000"],name ='13-Apr-2020')
    Map.add_cog_layer(urle,bidx=[3, 2, 1], rescale=["0,3000","0,3000","0,3000"],name ='03-May-2020')
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map.add_geojson(in_geojson, layer_name="AOI")
    Map.to_streamlit()

with col2:
    original_title = '<p style="color:Black; font-size: 20px;">False color infrared composite (B4-NIR/B3-R/B2-G)</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    Map = leafmap.Map()
    Map.add_basemap('HYBRID')
    Map.add_cog_layer(urla,bidx=[4, 3, 2], rescale=["0,4000","0,4000","0,4000"],name ='09-Jan-2020') # 
    Map.add_cog_layer(urlb,bidx=[4, 3, 2], rescale=["0,4000","0,4000","0,4000"],name ='14-Feb-2020') # NIR,R,G -  The False color infrared composite  It is most commonly used to assess plant density and healht
    Map.add_cog_layer(urlc,bidx=[4, 3, 2], rescale=["0,4000","0,4000","0,4000"],name ='18-Mar-2020')    
    Map.add_cog_layer(urld,bidx=[4, 3, 2], rescale=["0,4000","0,4000","0,4000"],name ='13-Apr-2020')  
    Map.add_cog_layer(urle,bidx=[4, 3, 2], rescale=["0,4000","0,4000","0,4000"],name ='03-May-2020')    
    in_geojson = 'https://github.com/crisjosil/CSP-4-KAI/blob/master/AOI_5km_buffer.geojson'
    fc = geemap.geojson_to_ee(in_geojson)
    Map.add_geojson(in_geojson, layer_name="AOI")
    Map.to_streamlit()
	
