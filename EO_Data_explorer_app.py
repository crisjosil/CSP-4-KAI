import streamlit as st
import leafmap.foliumap as leafmap
import geemap.foliumap as geemap
import os

os.environ["EARTHENGINE_TOKEN"]=st.secrets["EARTHENGINE_TOKEN"]
geemap.ee_initialize()

st.set_page_config(layout="wide")
st.title("Hi Keen AI,")

st.markdown(
    """
I created this web app using [streamlit](https://streamlit.io) and popular open-source geospatial libraries including [leafmap](https://leafmap.org), [geemap](https://geemap.org), and the ESA Copernicus browser. 
You can find all the code associated with the app hosted in [this repo](https://github.com/crisjosil/CSP-4-KAI). 
    """
)

st.info("Click on the left sidebar menu to navigate to the different apps.")

st.subheader("Timelapse of Satellite Imagery")
st.markdown(
    """
    The following timelapse animations were created using either [Copernicus browser](https://dataspace.copernicus.eu/browser/) or the timelapse feature within geemap. 
"""
)

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    original_title = '<p style="color:Black; font-size: 20px;">Sentinel-2 false color</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.image("https://github.com/crisjosil/CSP-4-KAI/raw/master/GIFs/sentinel2.gif")
    
    original_title = '<p style="color:Black; font-size: 20px;">Larger area Sentinel-2 false color</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.image("https://github.com/crisjosil/CSP-4-KAI/raw/master/GIFs/Sentinel-2_L2A-larger-timelapse.gif")

with row1_col2:
    original_title = '<p style="color:Black; font-size: 20px;">Sentinel-1 VV polarisation</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.image("https://github.com/crisjosil/CSP-4-KAI/raw/master/GIFs/sentinel1_VV.gif")
    
    original_title = '<p style="color:Black; font-size: 20px;">Sentinel-2 zoomed in  </p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.image("https://github.com/crisjosil/CSP-4-KAI/raw/master/GIFs/Sentinel-2_L2A-roads_rail-timelapse.gif")

